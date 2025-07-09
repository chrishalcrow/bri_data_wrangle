from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pynapple as nap
import numpy as np

from spatial_manifolds.util import gaussian_filter_nan

from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.scores.nagelhus import get_object_position, compute_nagelhus, make_gaussian_template
from bri_data_wrangle.filepaths import get_sessions, chris_linux_datapath, get_session_path, get_days

data_path = chris_linux_datapath

mouse = 1544
dates = get_days(mouse, parent_path=data_path)

derivatives_folder = Path("/home/nolanlab/Work/Bri_Project/derivatives/chR2")

all_obj_scores = pd.DataFrame()
all_grid_scores = pd.DataFrame()

data = []
for date in dates:

    if date == "2023-04-11":
        continue

    sessions = get_sessions(mouse, date, parent_path=data_path)
    sessions = [session for session in sessions if 'opto' not in session]

    if set(sessions) != set(["of", "obj", "of2"]):
        continue


    obj_comparison = pd.DataFrame(columns=["cluster_id", "of_p", "obj_p", "of2_p"])

    obj_datapath = get_session_path(data_path, mouse=mouse, date=date, session="obj")

        # load in data
    behavior, maxmins = load_and_wrangle_behavior(obj_datapath, speed_threshold=1.0)
    object_position_pixels = get_object_position(obj_datapath)
    xmin, xmax, ymin, ymax = maxmins
    object_position = [100/xmax*(object_position_pixels[0]-xmin), 100/ymax*(object_position_pixels[1]-ymin)]

    of_obj_template_score = pd.read_parquet(derivatives_folder / Path(f'{mouse}/{date}/of/scores/obj_template_score.parquet'))
    obj_obj_template_score = pd.read_parquet(derivatives_folder / Path(f'{mouse}/{date}/obj/scores/obj_template_score.parquet'))
    of2_obj_template_score = pd.read_parquet(derivatives_folder / Path(f'{mouse}/{date}/of2/scores/obj_template_score.parquet'))
    
    one_cluster = []
    for cluster_index, cluster_id in enumerate(of_obj_template_score.index):

        template_parameters = obj_obj_template_score['parameters'][cluster_id]
        p1, p2, p3 = template_parameters
        distance_from_object = np.sqrt( pow(object_position[0] - p2/0.4,2) + pow(object_position[1] - p1/0.4, 2) )
        
        one_cluster = [
            date,
            cluster_id,
            float(of_obj_template_score['pearson_score'][cluster_id]),
            float(obj_obj_template_score['pearson_score'][cluster_id]),
            float(of2_obj_template_score['pearson_score'][cluster_id]),
            float(distance_from_object)
        ]

        data.append(one_cluster)



data_df = pd.DataFrame(data, columns=["date", "cluster_id", "of_p", "obj_p", "of2_p", "dist"])
