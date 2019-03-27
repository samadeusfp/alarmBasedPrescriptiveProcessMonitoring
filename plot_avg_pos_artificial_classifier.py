import pandas as pd
import numpy as np
import os
from statistics import mode
from statistics import mean
from statistics import median
from scipy.stats.stats import spearmanr
import csv

path_dir = "/Users/stephanf/SCP/ArtificialClassifierResults"

data_5 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold_0.5.csv"),delimiter=";")
data_6 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold_0.6.csv"),delimiter=";")
data_7 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold_0.7.csv"),delimiter=";")
data_8 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold_0.8.csv"),delimiter=";")
data_9 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold_0.9.csv"),delimiter=";")

print("loaded all csv as pandas data frames")

data_5_cost = data_5.loc[data_5['metric'] == "cost_avg"]
data_6_cost = data_6.loc[data_6['metric'] == "cost_avg"]
data_7_cost = data_7.loc[data_7['metric'] == "cost_avg"]
data_8_cost = data_8.loc[data_8['metric'] == "cost_avg"]
data_9_cost = data_9.loc[data_9['metric'] == "cost_avg"]

del data_5
del data_6
del data_7
del data_8
del data_9

data_5_cost['cost_avg_6'] = data_6_cost['value']
data_5_cost['cost_avg_7'] = data_7_cost['value']
data_5_cost['cost_avg_8'] = data_8_cost['value']
data_5_cost['cost_avg_9'] = data_9_cost['value']

del data_6_cost
del data_7_cost
del data_8_cost
del data_9_cost


print("filtered all pandas data frames")

positions5 = []
positions6 = []
positions7 = []
positions8 = []
positions9 = []

for row in data_5_cost.itertuples():
    if row.early_type == "linear":
        values = []
        values.append(row.value)
        values.append(row.cost_avg_6)
        values.append(row.cost_avg_7)
        values.append(row.cost_avg_8)
        values.append(row.cost_avg_9)
        correlValues = values
        values = sorted(values)
        positions5.append(values.index(row.value)+1)
        positions6.append(values.index(row.cost_avg_6)+1)
        positions7.append(values.index(row.cost_avg_7)+1)
        positions8.append(values.index(row.cost_avg_8)+1)
        positions9.append(values.index(row.cost_avg_9)+1)

print("0.5")
print("mean: " + str(mean(positions5)))
print("mode: " + str(mode(positions5)))
print("median: " + str(median(positions5)))
print("avg_cost:" + str(mean(data_5_cost['value'])))

print("0.6")
print("mean: " + str(mean(positions6)))
print("mode: " + str(mode(positions6)))
print("median: " + str(median(positions6)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_6'])))



print("0.7")
print("mean: " + str(mean(positions7)))
#print("mode: " + str(mode(positions7)))
print("median: " + str(median(positions7)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_7'])))


print("0.8")
print("mean: " + str(mean(positions8)))
#print("mode: " + str(mode(positions8)))
print("median: " + str(median(positions8)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_8'])))


print("0.9")
print("mean: " + str(mean(positions9)))
print("mode: " + str(mode(positions9)))
print("median: " + str(median(positions9)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_9'])))

fileName = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/OutputArtificialEvalSingleCorel/test_trafficfines.csv"
with open(fileName, 'w', newline='') as csvResultFile:
    csvWriter = csv.writer(csvResultFile, delimiter=';', quoting=csv.QUOTE_NONE)
    printRow = []
    printRow.append("dataset")
    printRow.append("c_action")
    printRow.append("c_miss")
    printRow.append("c_com")
    printRow.append("early_type")
    printRow.append("value")
    csvWriter.writerow(printRow)

    for row in data_5_cost.itertuples():
        printRow = []
        printRow.append(row.dataset)
        printRow.append(row.c_action)
        printRow.append(row.c_miss)
        printRow.append(row.c_com)
        printRow.append(row.early_type)
        HitRatios = []
        HitRatios.append(0.5)
        HitRatios.append(0.6)
        HitRatios.append(0.7)
        HitRatios.append(0.8)
        HitRatios.append(0.9)
        values = []
        values.append(row.value*-1)
        values.append(row.cost_avg_6*-1)
        values.append(row.cost_avg_7*-1)
        values.append(row.cost_avg_8*-1)
        values.append(row.cost_avg_9*-1)
        correlValues = values
        test = spearmanr(HitRatios, values)
        printRow.append(test.correlation)
        csvWriter.writerow(printRow)
        print(str(test.correlation))


data_5 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold_0.5.csv"),delimiter=";")
data_6 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold_0.6.csv"),delimiter=";")
data_7 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold_0.7.csv"),delimiter=";")
data_8 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold_0.8.csv"),delimiter=";")
data_9 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold_0.9.csv"),delimiter=";")


print("loaded all csv as pandas data frames")

data_5_cost = data_5.loc[data_5['metric'] == "cost_avg"]
data_6_cost = data_6.loc[data_6['metric'] == "cost_avg"]
data_7_cost = data_7.loc[data_7['metric'] == "cost_avg"]
data_8_cost = data_8.loc[data_8['metric'] == "cost_avg"]
data_9_cost = data_9.loc[data_9['metric'] == "cost_avg"]

del data_5
del data_6
del data_7
del data_8
del data_9

data_5_cost['cost_avg_6'] = data_6_cost['value']
data_5_cost['cost_avg_7'] = data_7_cost['value']
data_5_cost['cost_avg_8'] = data_8_cost['value']
data_5_cost['cost_avg_9'] = data_9_cost['value']

del data_6_cost
del data_7_cost
del data_8_cost
del data_9_cost

fileName = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/OutputArtificialEvalSingleCorel/test_bpic2017.csv"
with open(fileName, 'w', newline='') as csvResultFile:
    csvWriter = csv.writer(csvResultFile, delimiter=';', quoting=csv.QUOTE_NONE)
    printRow = []
    printRow.append("dataset")
    printRow.append("c_action")
    printRow.append("c_miss")
    printRow.append("c_com")
    printRow.append("early_type")
    printRow.append("value")
    csvWriter.writerow(printRow)

    for row in data_5_cost.itertuples():
        printRow = []
        printRow.append(row.dataset)
        printRow.append(row.c_action)
        printRow.append(row.c_miss)
        printRow.append(row.c_com)
        printRow.append(row.early_type)
        HitRatios = []
        HitRatios.append(0.5)
        HitRatios.append(0.6)
        HitRatios.append(0.7)
        HitRatios.append(0.8)
        HitRatios.append(0.9)
        values = []
        values.append(row.value*-1)
        values.append(row.cost_avg_6*-1)
        values.append(row.cost_avg_7*-1)
        values.append(row.cost_avg_8*-1)
        values.append(row.cost_avg_9*-1)
        correlValues = values
        test = spearmanr(HitRatios, values)
        printRow.append(test.correlation)
        csvWriter.writerow(printRow)
        print(str(test.correlation))