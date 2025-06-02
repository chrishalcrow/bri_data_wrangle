import numpy as np
import pynapple as nap
import matplotlib.pyplot as plt

from scipy.interpolate import griddata
from spatial_manifolds.util import gaussian_filter_nan


def chris_interp(tc, num_bins):

    bins = (num_bins,num_bins)

    x = np.arange(0, bins[0])
    y = np.arange(0, bins[1])
    #mask invalid values
    array = np.ma.masked_invalid(tc)
    xx, yy = np.meshgrid(x, y)
    #get only the valid values
    x1 = xx[~array.mask]
    y1 = yy[~array.mask]
    newarr = array[~array.mask]

    GD1 = griddata((x1, y1), newarr.ravel(), (xx, yy), method='cubic')

    return GD1

def get_rate_map(behavior, spike_frame, num_bins):

    bins = (num_bins, num_bins)
    tuning_curve = nap.compute_2d_tuning_curves(
        nap.TsGroup([spike_frame]),
        np.stack([behavior['P_x'], behavior['P_y']], axis=1),
        nb_bins=bins,
        ep=behavior['moving'],
    )[0][0]

    return tuning_curve

def get_rate_map_fig(behavior, spike_frame, smooth_sigma=1.5, num_bins=40):

    tuning_curve = get_rate_map(behavior, spike_frame, num_bins)
    filtered_curve = chris_interp(tuning_curve, num_bins)
    filtered_curve = gaussian_filter_nan(np.array([filtered_curve]), sigma=[0, smooth_sigma, smooth_sigma])[0]


    fig, axes = plt.subplots(1,2)
    axes[0].imshow(tuning_curve)
    axes[1].imshow(filtered_curve)

    return fig
