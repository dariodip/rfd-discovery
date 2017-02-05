import unittest
import utils.utils as ut
import os
import logging

from random import randint
from loader import distance_mtr

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

class MyTestCase(unittest.TestCase):

    def test_distance_mtr_control_example(self):
        path = "../resources"
        datasets = self.__load_all_files__(path)
        for ds in datasets:
            logging.info("Next df: {}".format(ds))
            current_ds = path + "/" + ds
            try:
                c_sep, has_header = ut.check_sep_n_header(current_ds)
            except Exception as ex:
                print("Failed to load separator and header. Skipping test for {}".format(ds))
                pass
            logging.info("Loading distance matrix")
            dm = distance_mtr.DiffMatrix(current_ds, sep=c_sep, first_col_header=has_header)  # create class
            self.assertIsNotNone(dm, "check that dm is not null (none in python)")
            dist_m = dm.split_sides({'lhs': [1, 2, 3], 'rhs': [0]})  # split dm according to control RHS and LHS
            split_rhs = dist_m.loc[:,'RHS']
            split_lhs = dist_m.drop('RHS', 1)
            logging.info("Dataset loaded")
            logging.info("Check splitting")
            self.assertIsNotNone(split_rhs, "check if split_rhs is not none")
            self.assertIsNotNone(split_lhs, "check if split_lhs is not none")
            self.assertGreater(len(split_rhs), 0, "check if split_rhs is not an empty list")
            self.assertGreater(len(split_lhs), 0, "check if split_lhs is not an empty list")
            self.assertEqual(len(split_rhs), len(split_lhs), "check if rhs and lhs length is the same")
            logging.info("Check rows values")
            rnd = randint(1, len(split_rhs)- 1)
            rand_row = dist_m.loc[rnd]
            self.assertTrue(all(isinstance(item, float) for item in rand_row.tolist()), "check if each element is a float")
            logging.info("Check the presence of NaN values")
            self.assertFalse(dist_m.isnull().values.any(), "check if same value is NaN")
            logging.info("All Ok!")

    @staticmethod
    def __load_all_files__(path="../resources") -> list:
        return [file for file in os.listdir(path) if not file.startswith("distance") and file.endswith('.csv')]

if __name__ == '__main__':
    unittest.main()
