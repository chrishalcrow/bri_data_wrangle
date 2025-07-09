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

for date in dates:

    if date == "2023-04-11":
        continue

    sessions = get_sessions(mouse, date, parent_path=data_path)

    sessions = [session for session in sessions if 'opto' not in session]
    print("sessions: ", sessions)

    derivatives_folder = Path("/home/nolanlab/Work/Bri_Project/derivatives/chR2")

    all_folder = derivatives_folder / Path(f'{mouse}/{date}/all/')
    if all_folder.is_dir():
        continue
    else:
        all_folder.mkdir()
    mouseday_deriv_path = derivatives_folder / Path(f'{mouse}/{date}/{sessions[0]}')
    scores_folder = mouseday_deriv_path / "scores"
    base_grid_score = pd.read_parquet(scores_folder / "grid_score.parquet")

    for cluster_id in base_grid_score.index:

        fig, axes = plt.subplots(len(sessions),4)
        if len(sessions) == 1:
            axes = [axes]

        for session, axs in zip(sessions, axes):

            mouseday_deriv_path = derivatives_folder / Path(f'{mouse}/{date}/{session}')
            scores_folder = mouseday_deriv_path / "scores"

            session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)

            # load in data
            behavior, maxmins = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
            object_position_pixels = get_object_position(session_datapath)
            xmin, xmax, ymin, ymax = maxmins
            object_position = [100/xmax*(object_position_pixels[0]-xmin), 100/ymax*(object_position_pixels[1]-ymin)]
            spikes_frame = load_and_wrangle_spikes(session_datapath)

            obj_template_score = pd.read_parquet(scores_folder / "obj_template_score.parquet")
            grid_score = pd.read_parquet(scores_folder / "grid_score.parquet")

            gs = grid_score['grid_score'][cluster_id]
            gsig = grid_score['sig'][cluster_id]
            ps = obj_template_score['pearson_score'][cluster_id]
            spikes = spikes_frame[cluster_id]

            tc = nap.compute_2d_tuning_curves(
                nap.TsGroup([spikes]),
                np.stack([behavior["P_x"], behavior["P_y"]], axis=1),
                nb_bins=(40,40),
                ep=behavior["moving"],
            )[0][0]
            
            filtered_tc = gaussian_filter_nan(tc, sigma=[1.5, 1.5])

            template_parameters = obj_template_score['parameters'][cluster_id]
            p1, p2, p3 = template_parameters
            distance_from_object = np.sqrt( pow(object_position[0] - p2/0.4,2) + pow(object_position[1] - p1/0.4, 2) )
            template = make_gaussian_template(p1, p2, p3, 40, 40)

            axs[1].imshow(tc)
            axs[2].imshow(filtered_tc)
            axs[3].imshow(template)

            for ax in axs[1:]:
                ax.axis('off')
                ax.scatter(x=object_position[0]*0.4, y=object_position[1]*0.4, marker="o", color="red")




            axs[0].axis('off')
            axs[0].text(0,0.2,f"Session {session} \n\
Grid score: {gs:.2f} \n\
Grid sig: {gsig} \n\
Pearson coeff: {ps:.2f}\n\
From object: {distance_from_object:.2f}")
            
            fig.tight_layout()

            fig.suptitle(f"mouse {mouse}, date {date}, cluster {cluster_id}")

            fig.savefig(all_folder / f"summary_{cluster_id}.png")
            plt.close()









