import EncoderFactory
from DatasetManager import DatasetManager

import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score, precision_recall_fscore_support, confusion_matrix
from sklearn.pipeline import FeatureUnion

import time
import os
import sys
import csv
from sys import argv
import pickle


def calculate_cost(x, costs):
    return costs[int(x['prediction']), int(x['actual'])](x)

dataset_name = argv[1]
predictions_dir = argv[2]
conf_threshold_dir = argv[3]
results_dir = argv[4]

method = "opt_threshold"

# create results directory
if not os.path.exists(os.path.join(results_dir)):
    os.makedirs(os.path.join(results_dir))
    
# load predictions    
dt_preds = pd.read_csv(os.path.join(predictions_dir, "preds_%s.csv" % dataset_name), sep=";")

# write results to file
out_filename = os.path.join(results_dir, "results_%s_%s.csv" % (dataset_name, method))
with open(out_filename, 'w') as fout:
    writer = csv.writer(fout, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE)
    writer.writerow(["dataset", "method", "metric", "value", "c_miss", "c_action", "c_postpone", "threshold"])

    cost_weights = [(1,1), (2,1), (3,1), (5,1), (10,1), (20,1)]
    c_postpone_weight = 0
    for c_miss_weight, c_action_weight in cost_weights:

        c_miss = c_miss_weight / (c_miss_weight + c_action_weight)
        c_action = c_action_weight / (c_miss_weight + c_action_weight)

        costs = np.matrix([[lambda x: 0,
                              lambda x: c_miss],
                             [lambda x: c_action + c_postpone_weight * (x['prefix_nr']-1) / x['case_length'],
                              lambda x: c_action + c_postpone_weight * (x['prefix_nr']-1) / x['case_length'] +
                              (x['prefix_nr']-1) / x['case_length'] * c_miss
                             ]])
        # load the optimal confidence threshold
        conf_file = os.path.join(conf_threshold_dir, "optimal_confs_%s_%s_%s_%s.pickle" % (dataset_name, c_miss_weight, c_action_weight, c_postpone_weight))

        with open(conf_file, "rb") as fin:
            conf_threshold = pickle.load(fin)['conf_threshold']

        # trigger alarms according to conf_threshold
        dt_final = pd.DataFrame()
        unprocessed_case_ids = set(dt_preds.case_id.unique())
        for nr_events in range(1, dt_preds.prefix_nr.max() + 1):
            tmp = dt_preds[(dt_preds.case_id.isin(unprocessed_case_ids)) & (dt_preds.prefix_nr == nr_events)]
            tmp = tmp[tmp.predicted_proba >= conf_threshold]
            tmp["prediction"] = 1
            dt_final = pd.concat([dt_final, tmp], axis=0)
            unprocessed_case_ids = unprocessed_case_ids.difference(tmp.case_id)
        tmp = dt_preds[(dt_preds.case_id.isin(unprocessed_case_ids)) & (dt_preds.prefix_nr == 1)]
        tmp["prediction"] = 0
        dt_final = pd.concat([dt_final, tmp], axis=0)

        case_lengths = dt_preds.groupby("case_id").prefix_nr.max().reset_index()
        case_lengths.columns = ["case_id", "case_length"]
        dt_final = dt_final.merge(case_lengths)

        # calculate precision, recall etc.
        prec, rec, fscore, _ = precision_recall_fscore_support(dt_final.actual, dt_final.prediction, pos_label=1, average="binary")
        tn, fp, fn, tp = confusion_matrix(dt_final.actual, dt_final.prediction).ravel()

        # calculate earliness based on the "true alarms" only
        tmp = dt_final[(dt_final.prediction == 1) & (dt_final.actual == 1)]
        earliness = (1 - ((tmp.prefix_nr-1) / tmp.case_length))
        tmp = dt_final[(dt_final.prediction == 1)]
        earliness_alarms = (1 - ((tmp.prefix_nr-1) / tmp.case_length))

        writer.writerow([dataset_name, method, "prec", prec, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "rec", rec, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "fscore", fscore, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "tn", tn, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "fp", fp, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "fn", fn, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "tp", tp, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "earliness_mean", earliness.mean(), c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "earliness_std", earliness.std(), c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "earliness_alarms_mean", earliness_alarms.mean(), c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "earliness_alarms_std", earliness_alarms.std(), c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])

        cost = dt_final.apply(calculate_cost, costs=costs, axis=1).sum()
        writer.writerow([dataset_name, method, "cost", cost, c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
        writer.writerow([dataset_name, method, "cost_avg", cost / len(dt_final), c_miss_weight, c_action_weight, c_postpone_weight, conf_threshold])
