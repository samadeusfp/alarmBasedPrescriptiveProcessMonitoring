from sklearn.base import BaseEstimator
import numpy as np

class LGBMCalibrationWrapper(BaseEstimator):
    def __init__(self, cls):
        self.cls = cls
        self.classes_ = [0,1]
    
    def predict_proba(self, X):
        preds = self.cls.predict(X)
        preds = np.array([1-preds, preds]).T
        return preds

"""
from sklearn.base import BaseEstimator
import numpy as np
import lightgbm as lgb

class LGBMCalibrationWrapper(BaseEstimator):
    def __init__(self, cls=None, param=None, n_lgbm_iter=100):
        self.cls = cls
        self.param = param
        self.classes_ = [0,1]
        self.n_lgbm_iter = n_lgbm_iter
    
    def fit(self, X_train, y_train):
        train_data = lgb.Dataset(X_train, label=y_train)
        self.cls = lgb.train(self.param, train_data, self.n_lgbm_iter)
        return self.cls
    
    def predict_proba(self, X):
        preds = self.cls.predict(X)
        preds = np.array([1-preds, preds]).T
        return preds

"""