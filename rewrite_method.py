import csv
import os
from sys import argv



fileName = argv[1]
methodName = argv[2]

events = []
with open(fileName) as csvDataFile:
    csvReader = csv.reader(csvDataFile, delimiter=';')
    for row in csvReader:
        events.append(row)

with open(fileName, 'w') as csvResultFile:
    csvWriter = csv.writer(csvResultFile, delimiter=';', quoting=csv.QUOTE_NONE)
    currentPreds = 0
    firstLine = True
    for row in events:
        if firstLine == False:
            row[1] = methodName
        else:
            row[1] = "method"
            firstLine = False
        csvWriter.writerow(row)
