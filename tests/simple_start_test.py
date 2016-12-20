import unittest
import os.path as op
import pandas as pnd
import numpy as np

from math import sqrt
from random import randint
from loader import distance_mtr
from ast import literal_eval

DATASET_CSV = "../resources/dataset.csv"
DS_CSV = "../resources/distance-ds_test.csv"


class MyTestCase(unittest.TestCase):

    def test_distance_mtr_control_example(self):
        dm = distance_mtr.DiffMatrix(DATASET_CSV)  # create class
        dm.load()  # load data set from csv
        self.assertIsNotNone(dm.df, "check that dm is not null (none in python)")
        split = dm.split_sides([1, 2, 3], [0])  # split dm according to control RHS and LHS
        self.assertTrue('rhs' in split and 'lhs' in split, "check if 'rhs' and 'lhs' keys exist")
        split_rhs = split['rhs']
        split_lhs = split['lhs']
        self.assertIsNotNone(split_rhs, "check if split_rhs is not none")
        self.assertIsNotNone(split_lhs, "check if split_lhs is not none")
        self.assertGreater(len(split_rhs), 0, "check if split_rhs is not an empty list")
        self.assertGreater(len(split_lhs), 0, "check if split_lhs is not an empty list")
        self.assertEqual(len(split_rhs), len(split_lhs), "check if rhs and lhs length is the same")
        self.assertEqual((split_rhs.shape[1] + split_lhs.shape[1]), 4, "check if the sum of RHSs and LHSs is 4")
        dist_m = dm.distance_matrix(split)  # create distance matrix according to split on RHS and LHS
        keys = dist_m.index
        print(keys)
        expected_pairs = int(len(split_rhs) * (len(split_rhs) - 1) / 2)  # (n*n-1)/2 pairs on n els
        self.assertEqual(len(keys), expected_pairs, "check if number of pairs is n*(n-1)/2")
        # generate a random pair of indexes
        rnd1 = randint(1, len(split_rhs)- 1)
        rnd2 = randint(rnd1, len(split_rhs))
        while rnd2 <= rnd1:
            rnd2 = randint(1, len(split_rhs))
        rand_index = (rnd1, rnd2)
        rand_row = dist_m.loc[str(rand_index)]
        self.assertTrue(all(isinstance(item, float) for item in rand_row.tolist()), "check if each element is an int")
        h_distance_row = dist_m['RHS']
        lhdr = h_distance_row.tolist()
        self.assertTrue(all(lhdr[i] >= lhdr[i+1] for i in range(len(lhdr)-1)), "check if distance on RHS is sorted")

        #check if the distances correspond to the value in the oracle
        oracle = pnd.read_csv("../resources/dataset_oracle.csv", sep=",", header=0, index_col=0)

        for key in keys:
            key_tuple = literal_eval(key) #extract the value from the tuple in a string form
            row, col = key_tuple
            a_tuple = dist_m.loc[key].tolist()
            # complete the formula of the euclidean's distances of the R's method dist
            distance = sqrt(sum(x**2 for x in a_tuple))
            #oracle.loc[row index] return a Series with the index in string form
            #never check the equality of two floating numbers with the equals' operator
            self.assertTrue(np.isclose(distance, oracle.loc[row][str(col)]), "value error")

        dist_m.to_csv(DS_CSV, sep=";")  # save distance csv in resources
        self.assertTrue(op.isfile(DS_CSV), "check if distance matrix is saved")
        self.assertTrue(op.exists(DS_CSV), "check if distance matrix is saved")

if __name__ == '__main__':
    unittest.main()
