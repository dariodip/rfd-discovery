import unittest
import os.path as op
import pandas as pnd
import numpy as np
import utils.utils as ut
import os

from math import sqrt
from random import randint
from loader import distance_mtr
from ast import literal_eval


class MyTestCase(unittest.TestCase):

    def test_distance_mtr_control_example(self):
        path = "../resources"
        datasets = self.__load_all_files__(path)
        for ds in datasets:
            current_ds = path + "/" + ds
            try:
                c_sep, has_header = ut.check_sep_n_header(current_ds)
            except Exception as ex:
                print("Failed to load separator and header. Skipping test for {}".format(ds))
                pass
            dm = distance_mtr.DiffMatrix(current_ds, sep=c_sep, first_col_header=has_header)  # create class
            self.assertIsNotNone(dm, "check that dm is not null (none in python)")
            dist_m = dm.split_sides({'lhs': [1, 2, 3], 'rhs': [0]})  # split dm according to control RHS and LHS
            split_rhs = dist_m['RHS']
            split_lhs = dist_m.drop('RHS', 1)
            self.assertIsNotNone(split_rhs, "check if split_rhs is not none")
            self.assertIsNotNone(split_lhs, "check if split_lhs is not none")
            self.assertGreater(len(split_rhs), 0, "check if split_rhs is not an empty list")
            self.assertGreater(len(split_lhs), 0, "check if split_lhs is not an empty list")
            self.assertEqual(len(split_rhs), len(split_lhs), "check if rhs and lhs length is the same")
            #keys = dist_m.index
            #expected_pairs = int(len(split_rhs) * (len(split_rhs) - 1) / 2)  # (n*n-1)/2 pairs on n els
            #self.assertEqual(len(keys), expected_pairs, "check if number of pairs is n*(n-1)/2")
            # generate a random pair of indexes
            rnd1 = randint(1, len(split_rhs)- 1)
            rand_row = dist_m.loc[rnd1]
            self.assertTrue(all(isinstance(item, float) for item in rand_row.tolist()), "check if each element is a float")

    @staticmethod
    def __load_all_files__(path="../resources") -> list:
        return [file for file in os.listdir(path) if not file.startswith("distance") and file.endswith('.csv')]

if __name__ == '__main__':
    unittest.main()
