from bri_data_wrangle.filepaths import get_sessions, chris_linux_datapath, get_session_path, get_days, get_mice
import pandas as pd
from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.scores.nagelhus import get_object_position
import numpy as np

data_path = chris_linux_datapath

mice = get_mice(data_path)

data = []
for mouse in mice:

    dates = get_days(mouse, parent_path=data_path)
    
    for date in dates:

        sessions = get_sessions(mouse, date, parent_path=data_path)

        for session in sessions:

            session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)

            # load in data
            try:
                behavior, maxmins = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
                object_position_pixels = get_object_position(session_datapath)
                xmin, xmax, ymin, ymax = maxmins
                object_position = [100/xmax*(object_position_pixels[0]-xmin), 100/ymax*(object_position_pixels[1]-ymin)]

                data.append([mouse, date, session, object_position[0], object_position[1]])
            except:
                data.append([mouse, date, session, np.nan, np.nan])
                print(f"Failure for {mouse} {date} {session}.")

objects = pd.DataFrame(data, columns=['mouse', 'date', 'session', 'object_position_x', 'object_position_y'])
objects.to_csv("object_positions.csv")