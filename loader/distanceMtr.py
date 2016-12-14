import numpy as np
import csv
import os

def load(path):
    matrix = np.matrix([])
    with open(path, newline = '\n') as csvfile:
        mycsv = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in mycsv:
            print(row)

