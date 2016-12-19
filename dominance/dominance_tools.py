from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np


def get_dominance(path: str):
    diff_mtx = DiffMatrix(path)
    diff_mtx.load()
    distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides([1, 2, 3], [0]))
    naive_dominance(distance_matrix, [1, 2, 3], [0])


def naive_dominance(d_mtx: pnd.DataFrame, lhs: list, rhs: list):
    list_of_dominance_set = list()
    distance_values = list(set(np.asarray(d_mtx.iloc[:, rhs].values, dtype='int').flatten()))
    distance_values.sort(reverse=True)
    previous = set()
    for dist in distance_values:
        df_act_dist = d_mtx[d_mtx.RHS == dist]
        for index, row in df_act_dist.iterrows():
            if len(previous) == 0:
                print(row.values)
                previous.add(row.values)
                print(previous)


if __name__ == "__main__":
    get_dominance("../resources/dataset.csv")
