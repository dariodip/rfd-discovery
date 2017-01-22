import unittest
from dominance.dominance_tools import RFDDiscovery
import os
from datetime import datetime
import pandas as pd
import time

cols = ['ds_name', 'ds_len', 'ds_attr_size', 'ds_file_size_B', 'time_elapsed', 'rfd_count', 'attr_comb', 'iterations']
ITERATION_TIME = 10


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test_count = 1
        result_df = pd.DataFrame(columns=cols)  # Data frame in which save results
        path = "../resources"  # path in which datasets are stored
        datasets = self.__load_all_files__(path)
        for ds in datasets:
            if ds not in ['dataset.csv', 'dataset_oracle.csv']:  # TODO
                continue
            current_ds = path + "/" + ds                                # abs path for current dataset
            file_size = os.stat(current_ds).st_size                     # get file size
            ds_shape = self.__get_ds_shape(current_ds)                  # get df shape
            lhs_vs_rhs = self.__get_hs_combination(ds_shape['col'])     # combination for HS
            for combination in lhs_vs_rhs:
                for i in range(ITERATION_TIME):                         # repeat test X times
                    start_time = time.time()                            # get t0
                    rfdd = RFDDiscovery()
                    rfd_df = rfdd.get_dominance(current_ds, rfdd.naive_dominance, combination)
                    elapsed_time = time.time() - start_time             # get deltaT = now - t0
                    rfd_count = rfd_df.shape[0]
                    self.__append_result(ds, ds_shape['row'], ds_shape['col'], file_size, round(elapsed_time*1000,3),
                                         rfd_count, str(combination), result_df)    # append to result df
                    print("Test n.", test_count)
                    test_count += 1
        abs_path = os.path.abspath("../resources/test/{}-results.csv".format(time.strftime("%Y-%m-%d_%H-%M-%S")))
        result_df.to_csv(abs_path, sep=";", header=cols)

    @staticmethod
    def __append_result(name: str, row_len: int, attr_size: int, file_size: int, elapsed_time: float, rdf_count: int,
                        combination: str, df: pd.DataFrame) -> object:
        now = datetime.now()
        id = now.strftime("%Y-%m-%d_%H:%M:%S.%f")
        row_to_add = [name, row_len, attr_size, file_size, elapsed_time, rdf_count, combination, ITERATION_TIME]
        df.loc[id] = row_to_add

    @staticmethod
    def __get_hs_combination(col_len: int) -> list:
        col_list = list(range(col_len))
        combination = list()
        for i in range(0, len(col_list)):
            combination.append({'rhs': [col_list[i]], 'lhs': col_list[:i] + col_list[i + 1:]})
        return combination

    @staticmethod
    def __load_all_files__(path="../resources") -> list:
        return [file for file in os.listdir(path) if file.startswith("dataset")]

    @staticmethod
    def __get_ds_shape(ds: str) -> dict:
        df = pd.read_csv(ds, sep=";")
        shape = df.shape
        return {'col': shape[1] - 1, 'row': shape[0], 'col_caption': df.columns[1:]}


if __name__ == '__main__':
    myTest = MyTestCase('test')
    myTest.test_something(format='csv')
