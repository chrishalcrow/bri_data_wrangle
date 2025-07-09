import pandas as pd
import numpy as np
from numba import njit
import pynapple as nap

from spatial_manifolds.util import gaussian_filter_nan

from scipy.stats import norm

from warnings import warn


def compute_ori_score(
    session,
    session_type,
    cluster_spikes,
    object_position,
):
    
    num_bins = (40,40)
    mask_cm = 20

    tc = nap.compute_2d_tuning_curves(
            nap.TsGroup([cluster_spikes]),
            np.stack([session["P_x"], session["P_y"]], axis=1),
            nb_bins=num_bins,
            minmax=(0,100,0,100),
            ep=session["moving"],
        )[0][0]

    object_position_in_bins = object_position/100*num_bins[0]

    grid = np.meshgrid(np.arange(num_bins[0]), np.arange(num_bins[1]))

    object_mask = np.sqrt(np.pow(grid[0] - object_position_in_bins[0][0], 2) + np.pow(grid[1] - object_position_in_bins[0][1], 2)) < mask_cm*num_bins[0]/100

    obj_firing = np.nansum(tc*object_mask)
    non_obj_firing = np.nansum(tc*(~object_mask))

    return {'ori_score': (obj_firing - non_obj_firing)/(obj_firing + non_obj_firing) }



def classify_ori_score(grid_info, null_distribution, alpha=0.05):
    return {
        "sig": grid_info["ori_score"]
        > norm.ppf(
            1 - alpha,
            loc=np.nanmean(null_distribution["ori_score"]),
            scale=np.nanstd(null_distribution["ori_score"]),
        ),
        "sig_neg": grid_info["ori_score"]
        < norm.ppf(
            alpha,
            loc=np.nanmean(null_distribution["ori_score"]),
            scale=np.nanstd(null_distribution["ori_score"]),
        ),
    }