import pandas as pd
import numpy as np
import os
from statistics import mode
from statistics import mean
from statistics import median
from scipy.stats.stats import spearmanr
import csv
from math import isnan

path_dir = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/NonMyopicOutput"

data_1 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_opt_threshold.csv"), delimiter=";")
data_2 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_2prefixes_threshold.csv"), delimiter=";")
data_3 = pd.read_csv(os.path.join(path_dir, "results_traffic_fines_1_3prefixes_threshold.csv"), delimiter=";")


print("loaded all traffic_fines as pandas data frames")

data_5_cost = data_1.loc[data_1['metric'] == "cost_avg"]
data_6_cost = data_2.loc[data_2['metric'] == "cost_avg"]
data_7_cost = data_3.loc[data_3['metric'] == "cost_avg"]


del data_1
del data_2
del data_3


data_5_cost['cost_avg_6'] = data_6_cost['value']
data_5_cost['cost_avg_7'] = data_7_cost['value']


del data_6_cost
del data_7_cost



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
        correlValues = values
        values = sorted(values)
        positions5.append(values.index(row.value)+1)
        positions6.append(values.index(row.cost_avg_6)+1)
        positions7.append(values.index(row.cost_avg_7)+1)

print("1 Prefix")
print("mean: " + str(mean(positions5)))
print("mode: " + str(mode(positions5)))
print("median: " + str(median(positions5)))
print("avg_cost:" + str(mean(data_5_cost['value'])))

print("2 Prefixes")
print("mean: " + str(mean(positions6)))
print("mode: " + str(mode(positions6)))
print("median: " + str(median(positions6)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_6'])))



print("3 Prefixes")
print("mean: " + str(mean(positions7)))
print("mode: " + str(mode(positions7)))
print("median: " + str(median(positions7)))
print("avg_cost:" + str(mean(data_5_cost['cost_avg_7'])))



fileName = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopicRanking/test_trafficfines.csv"
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
        HitRatios.append(1)
        HitRatios.append(2)
        HitRatios.append(3)
        values = []
        values.append(row.value*-1)
        values.append(row.cost_avg_6*-1)
        values.append(row.cost_avg_7*-1)
        correlValues = values
        test = spearmanr(HitRatios, values)
        if row.value == row.cost_avg_6 and row.value == row.cost_avg_7:
            printRow.append(0.0)
        else:
            printRow.append(test.correlation)
        csvWriter.writerow(printRow)
#        print(str(test.correlation))


data_1 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_opt_threshold.csv"), delimiter=";")
data_2 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_2prefixes_threshold.csv"), delimiter=";")
data_3 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_cancelled_3prefixes_threshold.csv"), delimiter=";")



print("loaded all bpic2017_cancelled as pandas data frames")

data_5_cost = data_1.loc[data_1['metric'] == "cost_avg"]
data_6_cost = data_2.loc[data_2['metric'] == "cost_avg"]
data_7_cost = data_3.loc[data_3['metric'] == "cost_avg"]


del data_1
del data_2
del data_3


data_5_cost['cost_avg_6'] = data_6_cost['value']
data_5_cost['cost_avg_7'] = data_7_cost['value']

del data_6_cost
del data_7_cost


fileName = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopicRanking/test_bpic2017_cancelled.csv"
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
        HitRatios.append(1)
        HitRatios.append(2)
        HitRatios.append(3)
        values = []
        values.append(row.value*-1)
        values.append(row.cost_avg_6*-1)
        values.append(row.cost_avg_7*-1)
        correlValues = values
        test = spearmanr(HitRatios, values)
        if row.value == row.cost_avg_6 and row.value == row.cost_avg_7:
            printRow.append(0.0)
        else:
            printRow.append(test.correlation)
        csvWriter.writerow(printRow)
        print(str(test.correlation))


data_1 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_refused_opt_threshold.csv"), delimiter=";")
data_2 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_refused_2prefixes_threshold.csv"), delimiter=";")
data_3 = pd.read_csv(os.path.join(path_dir, "results_bpic2017_refused_3prefixes_threshold.csv"), delimiter=";")



print("loaded all bpic2017_refused as pandas data frames")

data_5_cost = data_1.loc[data_1['metric'] == "cost_avg"]
data_6_cost = data_2.loc[data_2['metric'] == "cost_avg"]
data_7_cost = data_3.loc[data_3['metric'] == "cost_avg"]


del data_1
del data_2
del data_3


data_5_cost['cost_avg_6'] = data_6_cost['value']
data_5_cost['cost_avg_7'] = data_7_cost['value']

del data_6_cost
del data_7_cost


fileName = "/Users/stephanf/Dropbox/Dokumente/Masterstudium/Masterthesis/testresults/NonMyopicRanking/test_bpic2017_refused.csv"
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
        HitRatios.append(1)
        HitRatios.append(2)
        HitRatios.append(3)
        values = []
        values.append(row.value*-1)
        values.append(row.cost_avg_6*-1)
        values.append(row.cost_avg_7*-1)
        correlValues = values
        test = spearmanr(HitRatios, values)
        if row.value == row.cost_avg_6 and row.value == row.cost_avg_7:
            printRow.append(0.0)
        else:
            printRow.append(test.correlation)
        csvWriter.writerow(printRow)

 #       print(str(test.correlation))