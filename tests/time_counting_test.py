import logging
import os
import time
import unittest
from datetime import datetime
import pandas as pd
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
cols = ['ds_name', 'ds_len', 'ds_attr_size', 'ds_file_size_B', 'time_elapsed', 'distance_time',
        'rfd_count', 'attr_comb', 'iterations']
ITERATION_TIME = 1


class MyTestCase(unittest.TestCase):

    def test_something(self):
        test_count = 1
        logging.info("Starting test")
        result_df = pd.DataFrame(columns=cols)  # Data frame in which save results
        path = "../resources"  # path in which datasets are stored
        datasets = self.__load_all_files__(path)
        logging.info("All files loaded")
        for ds in datasets:
            logging.info("Starting test for dataset {}".format(ds))
            current_ds = path + "/" + ds                                # abs path for current dataset
            file_size = os.stat(current_ds).st_size                     # get file size
            logging.info("Checking separator and header for dataset {}".format(ds))
            try:
                c_sep, has_header = ut.check_sep_n_header(current_ds)
            except Exception as ex:
                logging.ERROR("Failed to load separator and header. Skipping test for {}".format(ds))
                pass
            logging.info("{} has separator '{}' and has {} header".format(ds, c_sep, "no" if has_header is None else ""))
            ds_shape = self.__get_ds_shape(current_ds, sep=c_sep, first_row_head=has_header)  # get df shape
            lhs_vs_rhs = ut.get_hs_combination(ds_shape['col'])     # combination for HS
            diff_matrix, elapsed_time_dist = self.__get_diff_mtx(c_sep, current_ds, has_header)
            for combination in lhs_vs_rhs:
                logging.info("Testing on combination: {}".format(str(combination)))
                dist_mtx = diff_matrix.split_sides(combination)
                diff_mtx = None  # for free unused memory
                for i in range(ITERATION_TIME):                         # repeat test X times
                    logging.info("Test no.{}".format(i))
                    start_time = time.time()                            # get t0
                    rfdd = RFDDiscovery(dist_mtx)
                    compiled = rfdd.is_compiled()
                    rfd_df = rfdd.get_rfds(rfdd.standard_algorithm, combination)
                    elapsed_time = time.time() - start_time             # get deltaT = now - t0
                    logging.info("RFDs discovery process finished")
                    rfd_count = rfd_df.shape[0]
                    logging.info("Discovered {} RFDs".format(rfd_count))
                    logging.info("Result added")
                    logging.info("Appending result to result's dataframe")
                    # append to result df
                    self.__append_result(ds, ds_shape['row'], ds_shape['col'], file_size, round(elapsed_time*1000,3),
                                         round(elapsed_time_dist*1000,3), rfd_count, str(combination), result_df)
                    test_count += 1
                    elapsed_time_dist = 0
        logging.info("Saving file")
        abs_path = os.path.abspath("../resources/test/{}-results-{}.csv"
                                   .format(time.strftime("%Y-%m-%d_%H-%M-%S"), "c" if compiled else "p"))
        result_df.to_csv(abs_path, sep=";", header=cols, decimal=',')
        logging.info("File saved")

    @staticmethod
    def __get_diff_mtx(c_sep, current_ds, has_header):
        start_time_dist = time.time()
        logging.info("Creating class DiffMatrix")
        logging.info("Class DiffMatrix created. Now loading file...")
        diff_matrix = DiffMatrix(current_ds, sep=c_sep, first_col_header=has_header)
        logging.info("File loaded. Now computing distance matrix...")
        logging.info("Computing distance matrix finish. Let's do the true work")
        end_time_dist = time.time()
        elapsed_time_dist = end_time_dist - start_time_dist
        return diff_matrix, elapsed_time_dist

    @staticmethod
    def __append_result(name: str, row_len: int, attr_size: int, file_size: int, elapsed_time: float,
                        dist_time_elaps: float, rdf_count: int, combination: str, df: pd.DataFrame) -> object:
        now = datetime.now()
        id = now.strftime("%Y-%m-%d_%H:%M:%S.%f")
        row_to_add = [name, row_len, attr_size, file_size, elapsed_time, dist_time_elaps,
                      rdf_count, combination, ITERATION_TIME]
        df.loc[id] = row_to_add

    @staticmethod
    def __load_all_files__(path="../resources") -> list:
        logging.info("Loading all files")
        return [file for file in os.listdir(path) if not file.startswith("distance") and file.endswith('.csv')]

    @staticmethod
    def __get_ds_shape(ds: str, sep: str, first_row_head) -> dict:
        df = pd.read_csv(ds, sep=sep, header=first_row_head)
        shape = df.shape
        return {'col': shape[1], 'row': shape[0], 'col_caption': df.columns[1:]}


if __name__ == '__main__':
    myTest = MyTestCase('test')
    myTest.test_something(format='csv')
