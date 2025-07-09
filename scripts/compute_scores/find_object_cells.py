import numpy as np
import pandas as pd

from spatial_manifolds.util import gaussian_filter_nan
from spatial_manifolds.tuning_scores.grid_score import classify_grid_score, compute_grid_score
from spatial_manifolds.tuning_scores import with_null_distribution

from bri_data_wrangle.filepaths import get_session_path, chris_mac_datapath, chris_linux_datapath, get_days, get_sessions, get_mice
from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.plotting import get_rate_map_fig, get_rate_map
from bri_data_wrangle.scores.nagelhus import get_object_position, compute_nagelhus
from bri_data_wrangle.scores.firing_rate import compute_ori_score, classify_ori_score

from bri_data_wrangle.plotting import plot_object_check
data_path = chris_linux_datapath


df = pd.read_csv("ori_sigs.csv")

mice = np.unique(df['mouse'].values)
for mouse in mice:
    dates = np.unique(df.query(f'mouse == {mouse}')['dates'].values)

    for date in dates:

        clusters = np.unique(df.query(f'mouse == {mouse} & dates == "{date}"')['cluster_id'].values)

        sessions = np.unique(df.query(f'mouse == {mouse} & dates == "{date}"')['session'].values)
        


        for cluster_id in clusters:
            sig_over_sessions = df.query(f"mouse == {mouse} & dates == '{date}' & cluster_id == {cluster_id}")['sig'].values[:3]
            sessions = df.query(f"mouse == {mouse} & dates == '{date}' & cluster_id == {cluster_id}")['session'].values[:3]
            if len(sig_over_sessions) < 3: 
                break
            #print(f"Testing mouse {mouse}, date {date}, cluster {cluster_id}")
            if np.all(sig_over_sessions == np.array([False, True, False])):
                print(f"mouse {mouse}, date {date}, cluster {cluster_id}")
                fig = plot_object_check(mouse, date, sessions, cluster_id, data_path=data_path)
                fig.savefig(f"figs/ori/M{mouse}_D{date}_C{cluster_id}.png")
            if np.all(df.query(f"mouse == {mouse} & dates == '{date}' & cluster_id == {cluster_id}")['sig_neg'].values[:3] == np.array([False, True, False])):
                print(f"mouse {mouse}, date {date}, cluster {cluster_id} NEG")



# for date in dates:

#     sessions = get_sessions(mouse, date, parent_path=data_path)
#     if ('obj' not in sessions) or len(sessions) < 3:
#         continue



#     for cluster_id in spikes_frame.keys():
#         if np.all(df.query(f"date == '{date}' & cluster_id == {cluster_id}")['sig'].values == np.array([False, True, False])):
#             print(f"mouse {mouse}, date {date}, cluster {cluster_id}")