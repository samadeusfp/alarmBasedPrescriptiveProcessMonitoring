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

dataset_name = argv[1]
predictions_dir = argv[2]
results_dir = argv[3]

# create results directory
if not os.path.exists(os.path.join(results_dir)):
    os.makedirs(os.path.join(results_dir))

# load predictions
dt_preds = pd.read_csv(os.path.join(predictions_dir, "preds_train_%s.csv" % dataset_name), sep=";")

# write results to file
out_filename = os.path.join(results_dir, "accuracy_%s_fixedconfs.csv" % (dataset_name))
with open(out_filename, 'w') as fout:
    writer = csv.writer(fout, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE)
    writer.writerow(["dataset", "prefix", "accuracy"])

    conf_threshold = 0.5
    for nr_event in range(1, dt_preds.prefix_nr.max() + 1):
        # trigger alarms according to conf_threshold
        dt_final = pd.DataFrame()
        unprocessed_case_ids = set(dt_preds.case_id.unique())
        tmp = dt_preds[(dt_preds.case_id.isin(unprocessed_case_ids)) & (dt_preds.prefix_nr == nr_event)]
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

        # calculate precision, recall etc. independent of the costs
        tn, fp, fn, tp = confusion_matrix(dt_final.actual, dt_final.prediction).ravel()

        accuracy = (tn+tp)/(tn+fp+fn+tp)
        writer.writerow([dataset_name, str(nr_event), str(accuracy)])

