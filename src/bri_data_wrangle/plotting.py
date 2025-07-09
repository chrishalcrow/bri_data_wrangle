import numpy as np
import pynapple as nap
import pandas as pd
import matplotlib.pyplot as plt

from scipy.interpolate import griddata
from spatial_manifolds.util import gaussian_filter_nan

from bri_data_wrangle.filepaths import get_session_path
from bri_data_wrangle.wrangle import  load_and_wrangle_spikes,load_and_wrangle_behavior
from bri_data_wrangle.scores.nagelhus import make_gaussian_template

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

def get_rate_map_fig(behavior, spike_frame, smooth_sigma=1.5, num_bins=40, object_position_in_bins=None, parameters=None):

    tuning_curve = get_rate_map(behavior, spike_frame, num_bins)
    #filtered_curve = chris_interp(tuning_curve, num_bins)
    filtered_curve = gaussian_filter_nan(np.array([tuning_curve]), sigma=[0, smooth_sigma, smooth_sigma])[0]

    subplots = 2
    if parameters is not None:
        subplots += 1

    fig, axes = plt.subplots(1,subplots)

    axes[0].imshow(tuning_curve)
    axes[1].imshow(filtered_curve)
    if object_position_in_bins is not None:
        axes[0].scatter(object_position_in_bins[0][0], object_position_in_bins[0][1], color='red')
        axes[1].scatter(object_position_in_bins[0][0], object_position_in_bins[0][1], color='red')

    if parameters is not None:
        template = make_gaussian_template(parameters[0], parameters[1], parameters[2], 40, 40)
        axes[2].imshow(template)

    return fig

def plot_rate_map(mouse, date, session, cluster, data_path):

    session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)
    behavior, _ = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
    spikes_frame = load_and_wrangle_spikes(session_datapath)

    fig = get_rate_map_fig(behavior, spikes_frame[cluster])

    return fig


def plot_object_cell_check(mouse, date, session, cluster, data_path, parameters=None):

    all_object_positions = pd.read_csv('object_positions.csv')
    object_position = all_object_positions.query(f'mouse == {mouse} & date == "{date}" & session == "obj"')[['object_position_x','object_position_y']].values
    object_position_in_bins = object_position/100*40

    all_parameters = pd.read_csv('nagelhus_pearson.csv')
    these_parameters = all_parameters.query(f'mouse == {mouse} & date == "{date}" & session == "{session}" & cluster_id == {cluster}')
    parameters = [these_parameters['parameters_0'].values[0], these_parameters['parameters_1'].values[0], these_parameters['parameters_2'].values[0]]

    session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)
    behavior, _ = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
    spikes_frame = load_and_wrangle_spikes(session_datapath)

    fig = get_rate_map_fig(behavior, spikes_frame[cluster], object_position_in_bins=object_position_in_bins,parameters=parameters)

    return fig


def plot_object_check(mouse, date, sessions, cluster, data_path, parameters=None):

    num_bins = 40
    smooth_sigma = 1.5

    fig, axes = plt.subplots(3,3)

    all_object_positions = pd.read_csv('object_positions.csv')
    object_position = all_object_positions.query(f'mouse == {mouse} & date == "{date}" & session == "obj"')[['object_position_x','object_position_y']].values
    object_position_in_bins = object_position/100*40

    all_parameters = pd.read_csv('nagelhus_pearson.csv')

    for session_id, session in enumerate(sessions[:3]):

        these_parameters = all_parameters.query(f'mouse == {mouse} & date == "{date}" & session == "{session}" & cluster_id == {cluster}')
        parameters = [these_parameters['parameters_0'].values[0], these_parameters['parameters_1'].values[0], these_parameters['parameters_2'].values[0]]

        session_datapath = get_session_path(data_path, mouse=mouse, date=date, session=session)
        behavior, _ = load_and_wrangle_behavior(session_datapath, speed_threshold=1.0)
        spike_frame = load_and_wrangle_spikes(session_datapath)[cluster]

        tuning_curve = get_rate_map(behavior, spike_frame, num_bins)
        filtered_curve = gaussian_filter_nan(np.array([tuning_curve]), sigma=[0, smooth_sigma, smooth_sigma])[0]

        axes[session_id,0].imshow(tuning_curve)
        axes[session_id, 1].imshow(filtered_curve)
        if object_position_in_bins is not None:
            axes[session_id, 0].scatter(object_position_in_bins[0][0], object_position_in_bins[0][1], color='red')
            axes[session_id, 1].scatter(object_position_in_bins[0][0], object_position_in_bins[0][1], color='red')

        if parameters is not None:
            template = make_gaussian_template(parameters[0], parameters[1], parameters[2], 40, 40)
            axes[session_id, 2].imshow(template)
            axes[session_id, 2].scatter(object_position_in_bins[0][0], object_position_in_bins[0][1], color='red')

    return fig

