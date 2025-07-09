from pathlib import Path

import pandas as pd
import numpy as np

from bri_data_wrangle.filepaths import get_sessions, chris_linux_datapath, get_session_path, get_days

data_path = chris_linux_datapath

derivatives_folder = Path("/home/nolanlab/Work/Bri_Project/derivatives/chR2")

mouse = 1544
dates = get_days(mouse, parent_path=data_path)

num_cells = 0
num_grids = 0

for date in dates:
    sessions = get_sessions(mouse, date, parent_path=data_path)
    sessions = [session for session in sessions if 'opto' not in session]
    
    session = sessions[0]

    grid_score = pd.read_parquet(derivatives_folder / Path(f'{mouse}/{date}/{session}/scores/grid_score.parquet'))

    num_cells += len(grid_score)

    just_grid_cells = grid_score.query('sig == True')
    num_grids += len(just_grid_cells)


