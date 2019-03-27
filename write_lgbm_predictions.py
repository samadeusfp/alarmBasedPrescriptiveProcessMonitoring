import EncoderFactory
from DatasetManager import DatasetManager
from calibration_wrappers import LGBMCalibrationWrapper

import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score
from sklearn.pipeline import FeatureUnion
from sklearn.calibration import CalibratedClassifierCV
#from sklearn.imblearn.over_sampling import RandomOverSampler

from sklearn.metrics import brier_score_loss

import time
import os
import sys
from sys import argv
import pickle

import lightgbm as lgb


def create_model(param, n_lgbm_iter=100, calibrate=False):
    
    param['metric'] = ['auc', 'binary_logloss']
    param['objective'] = 'binary'
    param['verbosity'] = -1
    
    if oversample:
#        train_data = lgb.Dataset(X_train_ros, label=y_train_ros)
        print("that should not happen")
    else:
        train_data = lgb.Dataset(X_train, label=y_train)
    lgbm = lgb.train(param, train_data, n_lgbm_iter)
    
    if calibrate:
        wrapper = LGBMCalibrationWrapper(lgbm)
        cls = CalibratedClassifierCV(wrapper, cv="prefit", method=calibration_method)
        cls.fit(X_val, y_val)
        return (cls, lgbm)
    else:
        return lgbm


dataset_name = argv[1]
optimal_params_filename = argv[2]
results_dir = argv[3]

calibrate = False
split_type = "temporal"
oversample = False
calibration_method = "beta"

train_ratio = 0.8
val_ratio = 0.2

# create results directory
if not os.path.exists(os.path.join(results_dir)):
    os.makedirs(os.path.join(results_dir))
    
print('Preparing data...')
start = time.time()

# read the data
dataset_manager = DatasetManager(dataset_name)
data = dataset_manager.read_dataset()

min_prefix_length = 1
max_prefix_length = int(np.ceil(data.groupby(dataset_manager.case_id_col).size().quantile(0.9)))

    
cls_encoder_args = {'case_id_col': dataset_manager.case_id_col, 
                    'static_cat_cols': dataset_manager.static_cat_cols,
                    'static_num_cols': dataset_manager.static_num_cols, 
                    'dynamic_cat_cols': dataset_manager.dynamic_cat_cols,
                    'dynamic_num_cols': dataset_manager.dynamic_num_cols, 
                    'fillna': True}
    
# split into training and test
if split_type == "temporal":
    train, test = dataset_manager.split_data_strict(data, train_ratio, split=split_type)
else:
    train, test = dataset_manager.split_data(data, train_ratio, split=split_type)

train, val = dataset_manager.split_val(train, val_ratio)
    
# generate data where each prefix is a separate instance
dt_train_prefixes = dataset_manager.generate_prefix_data(train, min_prefix_length, max_prefix_length)
dt_val_prefixes = dataset_manager.generate_prefix_data(val, min_prefix_length, max_prefix_length)
dt_test_prefixes = dataset_manager.generate_prefix_data(test, min_prefix_length, max_prefix_length)

# encode all prefixes
feature_combiner = FeatureUnion([(method, EncoderFactory.get_encoder(method, **cls_encoder_args)) for method in ["static", "agg"]])
X_train = feature_combiner.fit_transform(dt_train_prefixes)
X_test = feature_combiner.fit_transform(dt_test_prefixes)
y_train = dataset_manager.get_label_numeric(dt_train_prefixes)
y_test = dataset_manager.get_label_numeric(dt_test_prefixes)
X_val = feature_combiner.fit_transform(dt_val_prefixes)
y_val = dataset_manager.get_label_numeric(dt_val_prefixes)

#if oversample:
#    ros = RandomOverSampler(random_state=42)
#    X_train_ros, y_train_ros = ros.fit_sample(X_train, y_train)


# train the model with pre-tuned parameters
with open(optimal_params_filename, "rb") as fin:
    best_params = pickle.load(fin)

# get predictions for test set
if calibrate:
    gbm, gbm_uncalibrated = create_model(best_params, calibrate=calibrate)

    preds_train = gbm.predict_proba(X_train)[:,1]
    preds_val = gbm.predict_proba(X_val)[:,1]
    preds = gbm.predict_proba(X_test)[:,1]
    
    preds_train_not_cal = gbm_uncalibrated.predict(X_train)
    preds_val_not_cal = gbm_uncalibrated.predict(X_val)
    preds_not_cal = gbm_uncalibrated.predict(X_test)
    
    print("Brier scores:")
    print("train calibrated: %s, train not calibrated: %s" % (brier_score_loss(y_train, preds_train), brier_score_loss(y_train, preds_train_not_cal)))
    print("val calibrated: %s, val not calibrated: %s" % (brier_score_loss(y_val, preds_val), brier_score_loss(y_val, preds_val_not_cal)))
    print("test calibrated: %s, test not calibrated: %s" % (brier_score_loss(y_test, preds), brier_score_loss(y_test, preds_not_cal)))

else:
    lgbm = create_model(best_params, calibrate=calibrate)
    preds_train = lgbm.predict(X_train)
    preds_val = lgbm.predict(X_val)
    preds = lgbm.predict(X_test)

    
# write train-val set predictions
dt_preds = pd.DataFrame({"predicted_proba": preds_train, "actual": y_train,
                         "prefix_nr": dt_train_prefixes.groupby(dataset_manager.case_id_col).first()["prefix_nr"],
                         "case_id": dt_train_prefixes.groupby(dataset_manager.case_id_col).first()["orig_case_id"]})
dt_preds_val = pd.DataFrame({"predicted_proba": preds_val, "actual": y_val,
                         "prefix_nr": dt_val_prefixes.groupby(dataset_manager.case_id_col).first()["prefix_nr"],
                         "case_id": dt_val_prefixes.groupby(dataset_manager.case_id_col).first()["orig_case_id"]})
#dt_preds = pd.concat([dt_preds, dt_preds_val], axis=0)
dt_preds.to_csv(os.path.join(results_dir, "preds_train_%s.csv" % dataset_name), sep=";", index=False)
dt_preds_val.to_csv(os.path.join(results_dir, "preds_val_%s.csv" % dataset_name), sep=";", index=False)


# write test set predictions
dt_preds = pd.DataFrame({"predicted_proba": preds, "actual": y_test,
                         "prefix_nr": dt_test_prefixes.groupby(dataset_manager.case_id_col).first()["prefix_nr"],
                         "case_id": dt_test_prefixes.groupby(dataset_manager.case_id_col).first()["orig_case_id"]})

dt_preds.to_csv(os.path.join(results_dir, "preds_%s.csv" % dataset_name), sep=";", index=False)


# write AUC for every prefix length
with open(os.path.join(results_dir, "results_%s.csv" % dataset_name), 'w') as fout:
    fout.write("dataset;nr_events;auc\n")

    for i in range(min_prefix_length, max_prefix_length+1):
        tmp = dt_preds[dt_preds.prefix_nr==i]
        if len(tmp.actual.unique()) > 1:
            auc = roc_auc_score(tmp.actual, tmp.predicted_proba)
            fout.write("%s;%s;%s\n" % (dataset_name, i, auc))
            

# write errors for every prefix length
with open(os.path.join(results_dir, "errors_%s.csv" % dataset_name), 'w') as fout:
    fout.write("dataset;prefix_nr;mean_error;std_error\n")

    for i in range(min_prefix_length, max_prefix_length+1):
        tmp = dt_preds_val[dt_preds_val.prefix_nr==i]
        mean = np.mean(tmp.actual - tmp.predicted_proba)
        std = np.std(tmp.actual - tmp.predicted_proba)
        fout.write("%s;%s;%s;%s\n" % (dataset_name, i, mean, std))
            
            
# write deltas for every prefix length
with open(os.path.join(results_dir, "deltas_%s.csv" % dataset_name), 'w') as fout:
    mean_cols = ["mean_delta_%s" % i for i in range(min_prefix_length, max_prefix_length)]
    std_cols = ["std_delta_%s" % i for i in range(min_prefix_length, max_prefix_length)]
    fout.write("dataset;prefix_nr;%s;%s\n" % (";".join(mean_cols), ";".join(std_cols)))

    for k in range(min_prefix_length, max_prefix_length):
        tmp_k = dt_preds_val[dt_preds_val.prefix_nr==k]
        means = []
        stds = []
        for i in range(k+1, max_prefix_length+1):
            tmp_i = dt_preds_val[dt_preds_val.prefix_nr==i]
            tmp_merged = tmp_k.merge(tmp_i, on="case_id", suffixes=["_k", "_i"])
            mean = np.mean(tmp_merged.predicted_proba_i - tmp_merged.predicted_proba_k)
            std = np.std(tmp_merged.predicted_proba_i - tmp_merged.predicted_proba_k)
            means.append(mean)
            stds.append(std)
        for i in range(k-1):
            means.append(mean)
            stds.append(std)
        fout.write("%s;%s;%s;%s\n" % (dataset_name, k, ";".join([str(val) for val in means]), ";".join([str(val) for val in stds])))