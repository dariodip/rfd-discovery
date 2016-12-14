import numpy as np
import csv
import os


class DiffMatrix:

    def __init__(self, path):
        self.path = path

    def load(self):
        matrix = np.matrix([])
        with open(self.path, newline='\n') as csvfile:
            mycsv = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in mycsv:
                #print(row)


    def diffmatrix(self):
        pass