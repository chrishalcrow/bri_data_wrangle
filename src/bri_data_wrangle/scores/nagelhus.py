import pandas as pd
import numpy as np
from numba import njit
import pynapple as nap

from spatial_manifolds.util import gaussian_filter_nan

from warnings import warn

@njit
def make_gaussian_template(x0, y0, decay, x_len, y_len):

    x_grid = np.arange(x_len)
    y_grid = np.arange(y_len)
    template = np.zeros((x_len, y_len))

    for x in x_grid:
        for y in y_grid:
            template[x, y] = make_gaussian_pt(x,y,x0,y0,decay)

    return template

@njit
def make_gaussian_pt(x,y,x0,y0,decay):
    return np.exp(-decay*(pow(x-x0,2) + pow(y-y0,2)))

def compute_pearson_correlation_2d(rate_map, template_map, num_mask):

    X = rate_map[num_mask]
    Y = template_map[num_mask]

    uX = np.mean(X)
    uY = np.mean(Y)

    numerator = np.mean((X - uX)*(Y - uY))
    denominator = np.sqrt((np.mean(pow(X, 2)) - pow(uX, 2)) *
                          (np.mean(pow(Y, 2)) - pow(uY, 2)))

    return numerator/denominator

def get_num_mask(rate_map):
    
    nan_mask = np.isnan(rate_map)
    return ~nan_mask


def compute_E(x0, y0, decay, rate_map, num_mask):
    
    xlen, ylen = np.shape(rate_map)
    
    template = make_gaussian_template(x0,y0,decay,xlen, ylen)
    score = compute_pearson_correlation_2d(rate_map, template, num_mask)

    return score

def compute_dE(x0, y0, decay, rate_map, num_mask):
    
    E0 = compute_E(x0, y0, decay, rate_map, num_mask)
    dp = np.array([0.001,0.001,0.001])

    Ep = np.array([
        compute_E(x0 + dp[0], y0, decay, rate_map, num_mask),
        compute_E(x0, y0 + dp[1], decay, rate_map, num_mask),
        compute_E(x0, y0, decay + dp[2], rate_map, num_mask)
    ])

    dE = (Ep - E0)/dp

    return dE

def grad_flow(trial_parameter, rate_map, num_mask, dt=0.01):

    parameters = trial_parameter

    old_pearson_score = compute_E(parameters[0], parameters[1], parameters[2], rate_map, num_mask)
    print(f"PS: {old_pearson_score}")
    
    for a in range(10000):

        dE = compute_dE(parameters[0], parameters[1], parameters[2], rate_map, num_mask)
        parameters += dt*dE

    new_pearson_score = compute_E(parameters[0], parameters[1], parameters[2], rate_map, num_mask)
    print(f"PS: {new_pearson_score}")
    
    return parameters, new_pearson_score


def find_best_template(rate_map, x_range, y_range, decay_range=np.arange(0.01, 0.12, 0.01), method="grad_flow"):

    num_mask = get_num_mask(rate_map)

    x_len, y_len = np.shape(rate_map)

    if method == "grad_flow":
        
        trial_parameters = [np.array([17.0,12.0,0.06])]

        for trial_parameter in trial_parameters:
            best_parameters = grad_flow(trial_parameter, rate_map, num_mask)

    elif method == "scan":

        x_range = range(x_len)
        y_range = range(y_len)

        possible_parameters = []
        for x0 in x_range:
            for y0 in y_range:
                for decay in decay_range:
                    possible_parameters.append([x0, y0, decay])

        best_pearson_correlation = 0
        best_parameters = [0, 0, 0]

        for parameters in possible_parameters:
            template_map = make_gaussian_template(
                x0=parameters[0], y0=parameters[1], decay=parameters[2], x_len=x_len, y_len=y_len)
            new_pearson_correlation = compute_pearson_correlation_2d(
                rate_map, template_map, num_mask)
            if new_pearson_correlation > best_pearson_correlation:
                best_parameters = parameters
                best_pearson_correlation = new_pearson_correlation

    return best_parameters

def get_object_position(session_datapath):

    object_csv_path_list = list(session_datapath.glob('*_object.csv'))

    if len(object_csv_path_list) == 0:

        warn(f"Cannot find object filepath in {session_datapath}. Setting object position to (0,0).")

        obj_x = 0
        obj_y = 0

    object_csv_path = object_csv_path_list[0]

    object_df = pd.read_csv(object_csv_path, header=None)

    obj_xs = np.array([float(obj_loc.split(" ")[0]) for obj_loc in object_df[0]])
    obj_ys = np.array([float(obj_loc.split(" ")[1]) for obj_loc in object_df[0]])

    obj_xs = obj_xs[~np.isnan(obj_xs)]
    obj_ys = obj_ys[~np.isnan(obj_ys)]

    obj_x = np.median(obj_xs)
    obj_y = np.median(obj_ys)

    return [obj_x, obj_y]


def compute_nagelhus(
    session,
    session_type,
    cluster_spikes,
):
    
    num_bins = (40,40)
    
    tc = nap.compute_2d_tuning_curves(
            nap.TsGroup([cluster_spikes]),
            np.stack([session["P_x"], session["P_y"]], axis=1),
            nb_bins=num_bins,
            minmax=(0,100,0,100),
            ep=session["moving"],
        )[0][0]
    
    filtered_tc = gaussian_filter_nan(tc, sigma=[1.5, 1.5])
    
    best_parameters = find_best_template(filtered_tc, num_bins[0], num_bins[1], method="scan")
    tweaked_parameters, new_pearson_score = grad_flow(best_parameters, filtered_tc, get_num_mask(tc))
    template = make_gaussian_template(tweaked_parameters[0], tweaked_parameters[1], tweaked_parameters[2], 40, 40)

    return {
        "parameters": tweaked_parameters,
        "template": template,
        "pearson_score": new_pearson_score,
    }


    





