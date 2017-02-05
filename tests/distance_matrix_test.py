import unittest
import utils.utils as ut
import os
import logging
import pandas as pnd

from random import randint
from loader import distance_mtr

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

class MyTestCase(unittest.TestCase):

    def test_distance_mtr_control_example(self):
        path = "../resources"
        datasets = self.__load_all_files__(path)
        for ds in datasets:
            logging.info("Next data frame: {}".format(ds))
            current_ds = path + "/" + ds
            logging.info("Getting header and separator")
            try:
                c_sep, has_header = ut.check_sep_n_header(current_ds)
            except Exception as ex:
                logging.ERROR("Failed to load separator and header. Skipping test for {}".format(ds))
                pass
            logging.info("{} has separator '{}' and has{}header".format(ds, c_sep, " no " if has_header is None else " "))
            logging.info("Loading data frame")
            df = self.__load_df(current_ds, sep=c_sep, first_col_header=has_header)
            logging.info("Done")
            logging.info("Loading distance matrix")
            dm = distance_mtr.DiffMatrix(current_ds, sep=c_sep, first_col_header=has_header)  # create class
            self.assertIsNotNone(dm, "check that dm is not null (none in python)")
            logging.info("Using a sample's splitting")
            dist_m = dm.split_sides({'lhs': [i for i in range(1, df.shape[1])], 'rhs': [0]})  # split dm according to control RHS and LHS
            logging.info("Dataset loaded")
            logging.info("Checking shape")
            self.assertIsNotNone(dist_m, "check if distance matrix is not none")
            self.assertGreater(dist_m.shape[0], 0, "check if row's number is greater than zero")
            self.assertGreater(dist_m.shape[1], 0, "check if col's number is greater than zero")
            max_pairs = int(df.shape[0] * (df.shape[0] - 1) / 2)
            self.assertGreaterEqual(max_pairs, dist_m.shape[0], "check if there are not too many pairs")
            logging.info("Checking rows values")
            rnd = randint(1, dist_m.shape[0] - 1)
            rand_row = dist_m.loc[rnd]
            self.assertTrue(all(isinstance(item, float) for item in rand_row.tolist()), "check if each element is a float")
            logging.info("Checking the presence of NaN values")
            self.assertFalse(dist_m.isnull().values.any(), "check if same value is NaN")
            logging.info("All Ok!")

    @staticmethod
    def __load_all_files__(path="../resources") -> list:
        return [file for file in os.listdir(path) if not file.startswith("distance") and file.endswith('.csv')]

    @staticmethod
    def __load_df(path, datetime=False, sep=';', missing='?', first_col_header=0, index_col=False):
        """Load a pandas data frame from a csv file stored in the path df.
        """
        df = pnd.read_csv(path, sep=sep, header=first_col_header, index_col=index_col, engine='c',
                               na_values=['', missing], parse_dates=datetime)
        return df

if __name__ == '__main__':
    unittest.main()
