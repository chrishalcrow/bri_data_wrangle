from bri_data_wrangle.filepaths import get_sessions, chris_linux_datapath, get_session_path, get_days, get_object_protocol, get_mice, get_protocol_from_sessions
import pandas as pd

data_path = chris_linux_datapath

mice = get_mice(data_path)

data = []
for mouse in mice:

    dates = get_days(mouse, parent_path=data_path)
    
    for date in dates:

        sessions = get_sessions(mouse, date, parent_path=data_path)
        print(f"mouse {mouse}, date {date}, sessions {sessions}")

#        protocols = []
#        for session in sessions:
        protocol = get_protocol_from_sessions(sessions)
            #protocol = get_object_protocol(mouse, date, session, parent_path=data_path)
#            protocols += protocol

        data.append([mouse, date, sessions, protocol])

df = pd.DataFrame(data)

df.rename({0: 'mouse', 1: 'date', 2: 'sessions', 3: 'protocol'}, axis=1, inplace=True)

df.to_pickle("all_sessions_and_protocols_from_guess.pkl")
df.to_csv("all_sessions_and_protocols_from_guess.csv")