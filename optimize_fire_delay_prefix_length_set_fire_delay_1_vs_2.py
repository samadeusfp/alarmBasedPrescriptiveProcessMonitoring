import EncoderFactory
from DatasetManager import DatasetManager

import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score
from sklearn.pipeline import FeatureUnion

import time
import os
import sys
from sys import argv
import pickle
import csv

from conf_constant_costfunctions import get_constant_costfunctions

from hyperopt import Trials, STATUS_OK, STATUS_FAIL, tpe, fmin, hp
import hyperopt
from multiprocessing import Process as Process


def calculate_cost(x, costs):
    return costs[int(x['prediction']), int(x['actual'])](x)


def evaluate_model_cost(args):
    conf_thresholds = args['conf_threshold']
    c_action = args['c_action']
    c_action2 = args['c_action2']
    c_miss = args['c_miss']
    c_com = args['c_com']
    c_com2 = args['c_com2']
    myopic_param = args['myopic_param']
    prefix_threshold = args['prefix_threshold']
    min_thresholds = args['min_thresholds']

    if early_type == "linear":
        costs = np.matrix([[lambda x: c_action2 * (x['prefix_nr'] - 1) / x['case_length'] + c_com2,
                            lambda x: c_action2 * (x['prefix_nr'] - 1) / x['case_length'] + (x['prefix_nr']) / x[
                                'case_length'] * c_miss
                            ],
                           [lambda x: c_action * (x['prefix_nr'] - 1) / x['case_length'] + c_com,
                            lambda x: c_action * (x['prefix_nr'] - 1) / x['case_length'] + (x['prefix_nr']) / x[
                                'case_length'] * c_miss
                            ]])
    elif early_type == "nonmonotonic":
        costs = np.matrix([[lambda x: (c_action2 * (
                                   1 - min(x['prefix_nr'], aConst) / bConst)) + (c_com2 * (
                                   1 - min(x['prefix_nr'], cConst) / dConst)),
                            lambda x: (c_action2 * (
                                   1 - min(x['prefix_nr'], aConst) / bConst)) + (1 - max(min(eConst,x['prefix_nr'])/fConst,1) *  c_miss)
                            ],
                           [lambda x: (c_action * (
                                   1 - min(x['prefix_nr'], aConst) / bConst)) + (c_com * (
                                   1 - min(x['prefix_nr'], cConst) / dConst)),
                            lambda x: (c_action * (
                                   1 - min(x['prefix_nr'], aConst) / bConst)) + (1 - max(min(eConst,x['prefix_nr'])/fConst,1) *  c_miss)
                            ]])
    else:
        costs = np.matrix([[lambda x: c_action2 + c_com2,
                            lambda x: c_action2 + (x['prefix_nr'] - 1) / x['case_length'] * c_miss
                            ],
                           [lambda x: c_action + c_com,
                            lambda x: c_action + (x['prefix_nr'] - 1) / x['case_length'] * c_miss
                            ]])


    # trigger alarms according to conf_threshold
    dt_final = pd.DataFrame()
    unprocessed_case_ids = set(dt_preds.case_id.unique())
    case_counter = pd.DataFrame()
    case_counter["case_id"] = dt_preds.case_id.unique()
    case_counter["counter"] = 0
    useful_experiment = True
    for nr_events in range(1, dt_preds.prefix_nr.max() + 1):
        if nr_events < prefix_threshold:
            threshold = conf_thresholds[0]
        else:
            threshold = conf_thresholds[1]
        if threshold < min_thresholds[nr_events-1]:
            useful_experiment = False
        tmp = dt_preds[(dt_preds.case_id.isin(unprocessed_case_ids)) & (dt_preds.prefix_nr == nr_events)]
        tmp = tmp[tmp.predicted_proba >= threshold]
        tmp["prediction"] = 1
        case_counter.loc[case_counter.case_id.isin(tmp.case_id), ['counter']] = case_counter["counter"] + 1
        tmp_case_counter = case_counter[case_counter.counter > myopic_param]
        tmp = tmp[tmp.case_id.isin(tmp_case_counter.case_id)]
        dt_final = pd.concat([dt_final, tmp], axis=0)
        unprocessed_case_ids = unprocessed_case_ids.difference(tmp.case_id)
    tmp = dt_preds[(dt_preds.case_id.isin(unprocessed_case_ids)) & (dt_preds.prefix_nr == 1)]
    tmp["prediction"] = 0
    dt_final = pd.concat([dt_final, tmp], axis=0)

    case_lengths = dt_preds.groupby("case_id").prefix_nr.max().reset_index()
    case_lengths.columns = ["case_id", "case_length"]
    dt_final = dt_final.merge(case_lengths)

    cost = dt_final.apply(calculate_cost, costs=costs, axis=1).sum()

    cost = cost * 100000

    return {'loss': cost, 'status': STATUS_OK, 'model': dt_final}


def run_experiment(c_miss_weight, c_action_weight, c_com_weight, early_type):
    c_action = c_action_weight / (c_miss_weight + c_action_weight + c_com_weight)
    c_com = c_com_weight / (c_miss_weight + c_action_weight + c_com_weight)
    c_miss = c_miss_weight / (c_miss_weight + c_action_weight + c_com_weight)

    c_action2 = c_action * 1.2
    c_com2 = c_com * 0.5

    # load the optimal confidence threshold
    conf_file_0_vs_1 = os.path.join(conf_threshold_dir, "0_vs_1/", "optimal_confs_%s_%s_%s_%s_%s_%s.pickle" % (
        dataset_name, c_miss_weight, c_action_weight, c_postpone_weight, c_com_weight, early_type))

    # load the optimal confidence threshold
    conf_file_0_vs_2 = os.path.join(conf_threshold_dir, "0_vs_2/", "optimal_confs_%s_%s_%s_%s_%s_%s.pickle" % (
        dataset_name, c_miss_weight, c_action_weight, c_postpone_weight, c_com_weight, early_type))

    with open(conf_file_0_vs_1, "rb") as fin:
        conf_param = pickle.load(fin)
        conf_threshold_0_vs_1 = conf_param['conf_threshold']
        prefix_threshold_0_vs_1 = conf_param['prefix_threshold']
    with open(conf_file_0_vs_2, "rb") as fin:
        conf_param = pickle.load(fin)
        conf_threshold_0_vs_2 = conf_param['conf_threshold']
        prefix_threshold_0_vs_2 = conf_param['prefix_threshold']

    fire_delay_file = os.path.join(fire_delay_dir, "optimal_firedelay_%s_%s_%s_%s_%s_%s.pickle" % (
        dataset_name, c_miss_weight, c_action_weight, c_postpone_weight, c_com_weight, early_type))
    with open(fire_delay_file, "rb") as fin:
        best_fire_delay_params  = pickle.load(fin)
        myopic_param = best_fire_delay_params['myopic_param']

    min_thresholds = []
    for nr_event in range(1, dt_preds.prefix_nr.max() + 1):
        if nr_event < prefix_threshold_0_vs_1:
            threshold_0_vs_1 = conf_threshold_0_vs_1[0]
        else:
            threshold_0_vs_1 = conf_threshold_0_vs_1[0]
        if nr_event < prefix_threshold_0_vs_2:
            threshold_0_vs_2 = conf_threshold_0_vs_2[0]
        else:
            threshold_0_vs_2 = conf_threshold_0_vs_2[0]
        min_thresholds.append(min(threshold_0_vs_1,threshold_0_vs_2))


    min_conf_threshold = min(conf_threshold_0_vs_1 + conf_threshold_0_vs_2)



    conf_thresholds = []
    for i in range(2):
        string_conf_threshold = "conf_threshold" + str(i)
        conf_thresholds.append(hp.uniform(string_conf_threshold, min_conf_threshold, 1))

    space = {'conf_threshold': conf_thresholds,
             'min_thresholds': min_thresholds,
             'c_action2': c_action2,
             'c_miss': c_miss,
             'c_com2': c_com2,
             'c_com': c_com,
             'myopic_param': myopic_param,
             'prefix_threshold': hp.choice("prefix_threshold", range(1, dt_preds.prefix_nr.max() + 1)),
             'c_action':c_action}
    trials = Trials()
    best = fmin(evaluate_model_cost, space, algo=tpe.suggest, max_evals=700, trials=trials)

    best_params = hyperopt.space_eval(space, best)

    outfile = os.path.join(params_dir, "optimal_confs_%s_%s_%s_%s_%s_%s.pickle" % (
        dataset_name, c_miss_weight, c_action_weight, c_postpone_weight, c_com_weight, early_type))
    # write to file
    with open(outfile, "wb") as fout:
        pickle.dump(best_params, fout)


print('Preparing data...')
start = time.time()

dataset_name = argv[1]
preds_dir = argv[2]
conf_threshold_dir = argv[3]
fire_delay_dir = argv[4]
params_dir = argv[5]

# create output directory
if not os.path.exists(os.path.join(params_dir)):
    os.makedirs(os.path.join(params_dir))

# read the data
dataset_manager = DatasetManager(dataset_name)

# prepare the dataset
dt_preds = pd.read_csv(os.path.join(preds_dir, "preds_val_%s.csv" % dataset_name), sep=";")

# set nonomonotic constants
aConst, bConst, cConst, dConst, eConst, fConst = get_constant_costfunctions(dataset_name)

print('Optimizing parameters...')
processes = []
cost_weights = [(10, 1), (10, 2), (10, 3), (10, 4), (10, 5)]
c_com_weights = [1, 2, 3, 4, 5, 10, 20, 30, 40]
c_postpone_weight = 0
for c_miss_weight, c_action_weight in cost_weights:
    for c_com_weight in c_com_weights:
        for early_type in ["const","linear","nonmonotonic"]:
            p = Process(target=run_experiment, args=(c_miss_weight, c_action_weight, c_com_weight, early_type))
            p.start()
            processes.append(p)
for p in processes:
    p.join()
