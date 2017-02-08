import unittest
import utils.utils as ut
import os
import logging
import pandas as pnd

from random import randint
from loader import distance_mtr

"""This module contain the testing code used for test the correctness of the class DiffMatrix"""

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

class MyTestCase(unittest.TestCase):
    """
    Class containing the code used for test the correctness of the class DiffMatrix
    """
    def test_distance_mtr_control_example(self):
        """
        Check if the class DiffMatrix compute the distance matrix correctly. The code is tested with a series of
        dataset contained in the variable path. For each step print a logging message.
        """
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
        """
        Given a valid path of a directory, it return a list with all the CSV files' names contained in the directory
        if that names do not start with the prefix 'distance'
        :param path: valid path to a directory
        :type path: str
        :return: list of all the CSV files in path that do not start with the prefix 'distance'
        :rtype: list
        """
        return [file for file in os.listdir(path) if not file.startswith("distance") and file.endswith('.csv')]

    @staticmethod
    def __load_df(path, datetime=False, sep=';', missing='?', first_col_header=0, index_col=False):
        """
        Load a pandas data frame from a CSV file stored in the path df.
        :param path: valid path of a CSV file
        :type path: str
        :param datetime: denote if we want that some column in the dataset must be interpreted as a date.
        To indicate that columns, whe use a list of integers indexes, where each index represent a column of the dataset
        containing the dates. False value indicate that we do not have any column with date. Default behavior is as if set to False if no value is passed.
        :type datetime: bool or list
        :param sep: the separator used to separate the values in the CSV file. Default behavior is as if set to ';' if no value is passed.
        :type sep: str
        :param missing: the character used to notify a missing value. Default behavior is as if set to '?' if no value is passed.
        :type missing: str
        :param first_col_header: row number(s) to use as column names, and the start of the data. Default behavior is as if set to 0 if no value is passed.
        :type first_col_header: int or list of int
        :param index_col: the column which contains the primary key of the dataset. Specifying it, this will not calculate as distance.
        :type index_col: int
        :return: the data frame containing the CSV data
        :rtype: pandas.core.frame.DataFrame
        """
        df = pnd.read_csv(path, sep=sep, header=first_col_header, index_col=index_col, engine='c',
                               na_values=['', missing], parse_dates=datetime)
        return df

if __name__ == '__main__':
    unittest.main()
