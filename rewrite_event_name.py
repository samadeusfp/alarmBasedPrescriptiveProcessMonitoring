import csv
import os
from sys import argv
from DatasetManager import DatasetManager

dataset_name = argv[1]
preds_dir = argv[2]
fileName = os.path.join(preds_dir, "preds_val_%s.csv" % dataset_name)

events = []
with open(fileName, newline='') as csvDataFile:
    csvReader = csv.reader(csvDataFile, delimiter=';')
    for row in csvReader:
        events.append(row)

# read the data
dataset_manager = DatasetManager(dataset_name)
data = dataset_manager.read_dataset()



with open(fileName, 'w', newline='') as csvResultFile:
    csvWriter = csv.writer(csvResultFile, delimiter=';', quoting=csv.QUOTE_NONE)
    firstLine = True
    csvWriter.writerow(row)
