# Prescriptive Process Monitoring

This repository contains all the scripts required to reproduce the experiments from the paper:
"Fire Now, Fire Later: Alarm-Based Systems for Prescriptive Process Monitoring" by Stephan A. Fahrenkrog-Petersen, Niek Tax, Irene Teinemaa, Marlon,Dumas, Massimiliano de Leoni, Fabrizio Maria Maggi, and Matthias Weidlich.

The code is written in Python 3. 

A lot of the code in this repository was based on code from Irene Teinemaa and Niek Tax, available here:
https://github.com/TaXxER/AlarmBasedProcessPrediction


## Predictive Process Monitoring Scripts

The foundations of a prescriptive process monitoring systems are the predictions made by a predictive process monitoring systems. To get these results, we apply a two-step approach. First, we use hyperparameter optimazation to ensure high quality results, this can be done with different scripts, depending on the choosen machine learning algorithm:

```
python optimize_params_rf.py <dataset_name> <output_dir>
python optimize_params_lgbm.py <dataset_name> <output_dir>
python optimize_params_xgboost.py <dataset_name> <output_dir>
```

For the parameters the following applies:

- dataset_name - the name of the dataset, should correspond to the settings specified in dataset_confs.py
- output_dir - the name of the directory where the optimal parameters will be written

## R-Scripts

The R-scripts in this repository were used to generate the respective figures in the paper. They used the results generated by the approach implemented within the Python scripts.
