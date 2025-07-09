


from spatial_manifolds.util import gaussian_filter_nan
from spatial_manifolds.tuning_scores.grid_score import classify_grid_score, compute_grid_score
from spatial_manifolds.tuning_scores import with_null_distribution

from bri_data_wrangle.filepaths import get_session_path, chris_mac_datapath, chris_linux_datapath, get_days, get_sessions, get_mice, get_protocol_from_sessions
from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.plotting import get_rate_map_fig, get_rate_map
from bri_data_wrangle.scores.nagelhus import get_object_position, compute_nagelhus
from bri_data_wrangle.scores.firing_rate import compute_ori_score, classify_ori_score


import matplotlib.pyplot as plt
from pathlib import Path
import pynapple as nap
import numpy as np
import pandas as pd

data_path = chris_linux_datapath

mice = get_mice(data_path)

ori = {}
data = []

for mouse in mice:
    dates = get_days(mouse, parent_path=data_path)
    #date = '2023-04-17'
    ori[mouse] = {}


    #dates = ['2023-04-17']

    for date in dates:
        
        ori[mouse][date] = {}
        sessions = get_sessions(mouse, date, parent_path=data_path)
        protocol = get_protocol_from_sessions(sessions)

        if protocol not in ['1','5']:
            continue

        sessions = [session for session in sessions if 'opto' not in session]
        
        all_object_positions = pd.read_csv('object_positions.csv')

        ori_score_with_null = with_null_distribution(
            compute_ori_score,
            classify_ori_score,
            100,
        )
        
        if 'obj' not in sessions:
            continue
            
        for session in sessions:
                
            ori[mouse][date][session] = {}

            session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)

            derivatives_folder = Path("/home/nolanlab/Work/Bri_Project/derivatives/chR2")
            mouseday_deriv_path = derivatives_folder / Path(f'{mouse}/{date}/{session}')

            behavior, maxmins = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
            object_position = all_object_positions.query(f'mouse == {mouse} & date == "{date}" & session == "obj"')[['object_position_x','object_position_y']].values
            spikes_frame = load_and_wrangle_spikes(session_datapath)


            for cluster_id, spikes in spikes_frame.items():

                ori[mouse][date][session][cluster_id] = ori_score_with_null(
                    behavior,
                    "no no no",
                    spikes,
                    object_position=object_position,
                )

                data.append([mouse, date, session, cluster_id, ori[mouse][date][session][cluster_id]['sig'], ori[mouse][date][session][cluster_id]['sig_neg']])

df = pd.DataFrame(data, columns=["mouse", "date", "session", "cluster_id", "sig", "sig_neg"])
df.to_csv("ori_sigs.csv")

# data = []
# for date in dates:
#     sessions = get_sessions(mouse, date, parent_path=data_path)
#     sessions = [session for session in sessions if 'opto' not in session]
#     for session in sessions:
#         session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)
#         spikes_frame = load_and_wrangle_spikes(session_datapath)
#         for cluster_id, spikes in spikes_frame.items():
#             if ori[date].get(cluster_id) is not None:
#                 data.append([mouse, date, session, cluster_id, ori[date][cluster_id]['sig']])