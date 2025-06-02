from pathlib import Path

import numpy as np
import pandas as pd

import pynapple as nap

def get_min_max_pos(positions):

    non_nan_x_pos = positions[~np.isnan(positions)]
    xmin = np.min(non_nan_x_pos)
    xmax = np.max(non_nan_x_pos)

    return xmin, xmax, 


def load_spikes(session_datapath):

    spikes_path = session_datapath / Path('MountainSort/DataFrames/spatial_firing.pkl')
    spikes_df = pd.read_pickle(spikes_path)

    return spikes_df

def wrangle_spikes(spikes_df, sampling_frequency):

    spikes_dict = spikes_df['firing_times'].to_dict()
    # convert to seconds
    spikes_dict_s = {key: nap.Ts(t=value/sampling_frequency) for key, value in spikes_dict.items()}
    spikes_frame = nap.TsGroup(data=spikes_dict_s)

    return spikes_frame



def load_and_wrangle_spikes(session_datapath, sampling_frequency = 30_000):

    spikes_df = load_spikes(session_datapath)
    spikes_frame = wrangle_spikes(spikes_df, sampling_frequency)

    return spikes_frame

def load_behavior(session_datapath):

    position_path = session_datapath / Path('MountainSort/DataFrames/position.pkl')
    position_df = pd.read_pickle(position_path)

    return position_df

def wrangle_behavior(position_df, speed_threshold):

    xmin, xmax = get_min_max_pos(position_df['position_x_pixels'].values)
    ymin, ymax = get_min_max_pos(position_df['position_y_pixels'].values)
    maxmins = (xmin, xmax, ymin, ymax)


    position_df['position_x_m'] = position_df['position_x_pixels'].map(lambda x: 100/xmax*(x - xmin))
    position_df['position_y_m'] = position_df['position_y_pixels'].map(lambda y: 100/ymax*(y - ymin))

    synced_time, position_x, position_y, speed = np.transpose(position_df[[
        'synced_time', 'position_x_m', 'position_y_m', 'speed']].values)

    behavior = {}
    speed_nap = nap.Tsd(t=synced_time, d=speed)

    behavior['P_x'] = nap.Tsd(t=synced_time, d=position_x)
    behavior['P_y'] = nap.Tsd(t=synced_time, d=position_y)
    behavior['moving'] = speed_nap.threshold(speed_threshold, method="above").time_support

    return behavior, maxmins

def load_and_wrangle_behavior(session_datapath, speed_threshold=1.0):

    position_df = load_behavior(session_datapath)
    behavior, maxmins = wrangle_behavior(position_df, speed_threshold=speed_threshold)

    return behavior, maxmins