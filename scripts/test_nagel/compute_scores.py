from bri_data_wrangle.scores.nagelhus import get_object_position, find_best_template, grad_flow, get_num_mask, make_gaussian_template, compute_nagelhus
from spatial_manifolds.util import gaussian_filter_nan
from spatial_manifolds.data.binning import get_bin_config

from spatial_manifolds.tuning_scores.grid_score import (
    classify_grid_score,
    compute_grid_score
    )

from spatial_manifolds.tuning_scores import (
    for_all_clusters,
    for_all_groups,
    with_null_distribution,
    with_travel_shifts,
)

from spatial_manifolds.tuning_scores import compute_grid_score

from bri_data_wrangle.filepaths import get_session_path, chris_mac_datapath 
from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.plotting import get_rate_map_fig, get_rate_map

import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import pynapple as nap
import numpy as np

data_path = chris_mac_datapath

mouse = 1544
date = '2023-04-17'
session = 'obj'

session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)

derivatives_folder = Path("/Users/christopherhalcrow/Work/Bri_Project/derivatives/chR2")
mouseday_deriv_path = derivatives_folder / Path(f'{mouse}/{date}/{session}')

# make scores folder
scores_folder = mouseday_deriv_path / "scores"
scores_folder.mkdir(exist_ok=True)
plot_folder = mouseday_deriv_path / "plots"
plot_folder.mkdir(exist_ok=True)

# load in data
behavior, maxmins = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
object_position_pixels = get_object_position(session_datapath)
xmin, xmax, ymin, ymax = maxmins
object_position = [100/xmax*(object_position_pixels[0]-xmin), 100/ymax*(object_position_pixels[1]-ymin)]
                   
spikes_frame = load_and_wrangle_spikes(session_datapath)

grid_score_with_null = with_null_distribution(
    compute_grid_score,
    classify_grid_score,
    100,
)

nagelhus_with_null = with_null_distribution(
    compute_nagelhus,
    classify_grid_score,
    100,
)


gs = {}
gs_no_null = {}

nh = {}
nh_no_null = {}

for cluster_id, spikes in spikes_frame.items():

    print(f"doing {cluster_id}")

    gs[cluster_id] = grid_score_with_null(
        behavior,
        "no no no",
        spikes,
        bin_config = {
            "dim": "2d",
            "bounds": (0.0, 100.0, 0.0, 100.0),
            "num_bins": 40,
            "smooth_sigma": 1.5,
        }
    )

    nh[cluster_id] = compute_nagelhus( 
        behavior,
        "no no no",
        spikes,
    )

    gs_no_null[cluster_id] = {key: value for key, value in gs[cluster_id].items() if key != "null"}
    nh_no_null[cluster_id] = {key: value for key, value in nh[cluster_id].items() if key != "null"}

    tc = nap.compute_2d_tuning_curves(
        nap.TsGroup([spikes]),
        np.stack([behavior["P_x"], behavior["P_y"]], axis=1),
        nb_bins=(40,40),
        ep=behavior["moving"],
    )[0][0]
    
    filtered_tc = gaussian_filter_nan(tc, sigma=[1.5, 1.5])

    fig, axes = plt.subplots(1,3, figsize=(10,4))
    axes[0].imshow(tc)
    axes[1].imshow(filtered_tc)
    axes[2].imshow(nh[cluster_id]['template'])

    for ax in axes:
        ax.scatter(x=object_position[0]*0.4, y=object_position[1]*0.4, marker="o", color="red")
        ax.set_xticks([0,10,20,30,40])
        ax.set_xticklabels([0,25,50,75,100])
        ax.set_yticks([0,10,20,30,40])
        ax.set_yticklabels([0,25,50,75,100])

    x0, y0 = nh[cluster_id]['parameters'][0], nh[cluster_id]['parameters'][1]
    distance_from_object = np.sqrt( pow(object_position[0] - y0/0.4,2) + pow(object_position[1] - x0/0.4, 2) )

    fig.suptitle(f"mouse {mouse} date {date} session {session} cluster {cluster_id}\n\
Grid score: {gs[cluster_id]['grid_score']:.2f} \n\
Pearson coeff: {nh[cluster_id]['pearson_score']:.2f}\n\
Distance from object: {distance_from_object:.2f}")

    fig.savefig(plot_folder / f"summary_{cluster_id}.png")

