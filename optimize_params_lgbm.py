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

import lightgbm as lgb

from hyperopt import Trials, STATUS_OK, tpe, fmin, hp
import hyperopt


def create_and_evaluate_model(args, n_lgbm_iter=100):
    global trial_nr
    if trial_nr % 50 == 0:

        print(trial_nr)
    trial_nr += 1
    
    param = {'num_leaves': int(args['num_leaves']),
             'max_depth': int(args['max_depth']),
             'learning_rate': args['learning_rate'],
             'max_bin': int(args['max_bin']),
             'bagging_fraction': args['bagging_fraction']}
    param['metric'] = ['auc', 'binary_logloss']
    param['objective'] = 'binary'
    param['verbosity'] = -1
    
    score = 0
    for current_train_names, current_test_names in dataset_manager.get_idx_split_generator(dt_for_splitting, n_splits=n_splits):
        
        train_idxs = case_ids.isin(current_train_names)
        X_train = X_all[train_idxs]
        y_train = y_all[train_idxs]
        X_test = X_all[~train_idxs]
        y_test = y_all[~train_idxs]
        
        train_data = lgb.Dataset(X_train, label=y_train)
        lgbm = lgb.train(param, train_data, n_lgbm_iter)
        preds = lgbm.predict(X_test)

        score += roc_auc_score(y_test, preds)
    return {'loss': -score / n_splits, 'status': STATUS_OK, 'model': lgbm}


print('Preparing data...')
start = time.time()

dataset_name = argv[1]
params_dir = argv[2]

train_ratio = 0.8
n_splits = 3

trial_nr = 1

# create results directory
if not os.path.exists(os.path.join(params_dir)):
    os.makedirs(os.path.join(params_dir))
    
# read the data
dataset_manager = DatasetManager(dataset_name)
data = dataset_manager.read_dataset()

min_prefix_length = 1
if "bpic2017" in dataset_name:
    max_prefix_length = min(20, dataset_manager.get_pos_case_length_quantile(data, 0.95))
elif "uwv" in dataset_name or "bpic2018" in dataset_name:
    max_prefix_length = dataset_manager.get_pos_case_length_quantile(data, 0.9)
else:
    max_prefix_length = min(40, dataset_manager.get_pos_case_length_quantile(data, 0.95))

cls_encoder_args = {'case_id_col': dataset_manager.case_id_col, 
                    'static_cat_cols': dataset_manager.static_cat_cols,
                    'static_num_cols': dataset_manager.static_num_cols, 
                    'dynamic_cat_cols': dataset_manager.dynamic_cat_cols,
                    'dynamic_num_cols': dataset_manager.dynamic_num_cols, 
                    'fillna': True}
    
# split into training and test
train, _ = dataset_manager.split_data_strict(data, train_ratio, split="temporal")
    
# generate data where each prefix is a separate instance
dt_prefixes = dataset_manager.generate_prefix_data(train, min_prefix_length, max_prefix_length)

# encode all prefixes
feature_combiner = FeatureUnion([(method, EncoderFactory.get_encoder(method, **cls_encoder_args)) for method in ["static", "agg"]])
X_all = feature_combiner.fit_transform(dt_prefixes)
y_all = np.array(dataset_manager.get_label_numeric(dt_prefixes))

# generate dataset that will enable easy splitting for CV - to guarantee that prefixes of the same case will remain in the same chunk
case_ids = dt_prefixes.groupby(dataset_manager.case_id_col).first()["orig_case_id"]
dt_for_splitting = pd.DataFrame({dataset_manager.case_id_col: case_ids, dataset_manager.label_col: y_all}).drop_duplicates()

print('Optimizing parameters...')

space = {'num_leaves': hp.choice('num_leaves', np.arange(2, 300, dtype=int)),
         'max_depth': hp.choice('max_depth', np.arange(1, 15, dtype=int)),
         'learning_rate': hp.loguniform('learning_rate', np.log(0.00001), np.log(0.1)),
         'max_bin': hp.choice('max_bin', np.arange(2, 300, dtype=int)),
         'bagging_fraction': hp.uniform("bagging_fraction", 0.001, 0.999)}
trials = Trials()
best = fmin(create_and_evaluate_model, space, algo=tpe.suggest, max_evals=200, trials=trials)

best_params = hyperopt.space_eval(space, best)

outfile = os.path.join(params_dir, "optimal_params_lgbm_%s.pickle" % (dataset_name))
# write to file
with open(outfile, "wb") as fout:
    pickle.dump(best_params, fout)
