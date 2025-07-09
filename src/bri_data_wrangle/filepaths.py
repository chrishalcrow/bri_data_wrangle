from pathlib import Path

chris_mac_datapath = "/Volumes/cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Bri/optetrode_recordings/chR2"
chris_linux_datapath = "/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Bri/optetrode_recordings/chR2"

def get_protocol_from_sessions(
    sessions: list[str]
):
    if len(sessions) < 2:
        return 'U'
    
    second_session = sessions[1]

    if second_session.startswith('opto'):
        return '2'
    elif second_session.startswith('of'):
        return '4'
    else:
        if len(sessions) == 2:
            return 'U'
        third_session = sessions[2]
        if third_session.startswith('obj'):
            return '3'
        elif third_session.startswith('opto'):
            return '6'
        else:
            if len(sessions) == 3:
                return 'U'
            fourth_session = sessions[3]
            if fourth_session.startswith('opto'):
                return '1'
            elif fourth_session.startswith('obj'):
                return '5'
            else:
                return 'U'

def get_object_protocol(
    mouse: str | int, 
    date: str,
    session: str,
    parent_path: str | Path
):
    
    mouse = str(mouse)
    parent_path = Path(parent_path)
    mouse_directory = parent_path / mouse
    
    session_dir = list(mouse_directory.glob(f'{mouse}_{date}*{session}'))
    object_protocol_filepath = Path(session_dir[0]) / "object_protocol.txt"

    if object_protocol_filepath.is_file():

        with open(object_protocol_filepath) as f:
            protocol = f.read()

    else:
        protocol = "U"
    
    return protocol
    

def get_mice(
    data_path: str | Path
):
    data_path = Path(data_path)
    assert data_path.is_dir(), f"The data folder {data_path} does not exist."

    dirs_in_data_dir = data_path.glob(f'1*')

    mice = [str(dir_in_data_dir.name) for dir_in_data_dir in dirs_in_data_dir]

    return mice

def get_days(
        mouse: str | int, 
        parent_path: str | Path
    ):
    """
    For a given mouse id, returns all days the experiment was run.
    """

    mouse = str(mouse)
    parent_path = Path(parent_path)

    mouse_directory = parent_path / mouse
    assert mouse_directory.is_dir(), f"No folder named {mouse} in {mouse_directory}"

    dirs_in_mouse_dir = mouse_directory.glob(f'{mouse}*')

    # directories of the form {mouse}_{date}_{time}_{sessions}
    dates = [dir_in_mouse_dir.name.split('_')[1] for dir_in_mouse_dir in dirs_in_mouse_dir]

    unique_dates = set(dates)

    return list(unique_dates)
        
def get_sessions(
    mouse: str | int, 
    date: str, 
    parent_path: str | Path
):
    """
    For a given mouseday, return the sessions.
    """

    mouse = str(mouse)
    parent_path = Path(parent_path)

    mouse_directory = parent_path / mouse
    assert mouse_directory.is_dir(), f"No folder named {mouse} in {mouse_directory}"

    dirs_in_mouse_dir = list(mouse_directory.glob(f'{mouse}_{date}*'))

    assert len(dirs_in_mouse_dir) > 0, f"No folders of the form {mouse}_{date}* in {mouse_directory}"

    # directories of the form {mouse}_{date}_{time}_{sessions}
    times = [dir_in_mouse_dir.name.split('_')[2] for dir_in_mouse_dir in dirs_in_mouse_dir]
    sessions = [dir_in_mouse_dir.name.split('_')[3] for dir_in_mouse_dir in dirs_in_mouse_dir]

    #print("times: ", times)
    times.sort()

    sorted_sesions = []
    for time in times:
        for a, session in enumerate(dirs_in_mouse_dir):
            if time in str(session):
                sorted_sesions.append(sessions[a])

    return sorted_sesions

def make_derivatives_folders(
    derivative_dir: str | Path,
    data_path: str | Path,
):
    
    derivative_dir = Path(derivative_dir)
    assert derivative_dir.is_dir(), f"The derivatives folder {derivative_dir} does not exist."

    data_path = Path(data_path)
    assert data_path.is_dir(), f"The data folder {data_path} does not exist."

    mice = get_mice(data_path)

    for mouse in mice:
        dates = get_days(mouse, data_path)
        for date in dates:
            sessions = get_sessions(mouse, date, data_path)    
            for session in sessions:
                mouse_date_session_dir = derivative_dir / mouse / date / session
                mouse_date_session_dir.mkdir(parents=True)

    return None

def get_session_path(
    data_path: str | Path,
    mouse: str | int, 
    date: str,
    session: str,
):
    
    mouse = str(mouse)
    data_path = Path(data_path)

    mouse_directory = data_path / mouse
    assert mouse_directory.is_dir(), f"No folder named {mouse} in {mouse_directory}"

    dirs_in_mouse_dir = list(mouse_directory.glob(f'{mouse}_{date}*{session}'))
    assert len(dirs_in_mouse_dir) > 0, f"No folders of the form {mouse}_{date}*{session} in {mouse_directory}"

    return dirs_in_mouse_dir[0]


