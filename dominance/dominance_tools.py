from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np


def get_dominance(path: str, dominance_funct):
    diff_mtx = DiffMatrix(path)
    diff_mtx.load()
    distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides([1, 2, 3], [0]))
    dominance_funct(distance_matrix, [1, 2, 3], [0])


def naive_dominance(d_mtx: pnd.DataFrame, lhs: list, rhs: list):
    list_of_dominance_set = list()
    distance_values = list(set(np.asarray(d_mtx.iloc[:, rhs].values, dtype='int').flatten()))
    distance_values.sort(reverse=True)
    previous = set()
    on_distance_dom = dict()
    max_dist = max(distance_values)
    for dist in distance_values:
        df_act_dist = d_mtx[d_mtx.RHS == dist]
        for index, row in df_act_dist[lhs].iterrows():
            last_row = tuple(row.values.tolist())
            if len(previous) == 0 or check_dominance(last_row, previous):
                previous.add(last_row)
                add_to_dict_set(on_distance_dom, last_row, dist)
    print(previous)
    print(on_distance_dom)
    print(len(previous))


def check_dominance(y: tuple, tuples_set: set) -> bool:
    # X dominates X iff foreach x in X, foreach y in Y, x < y <=> x - y < 0
    to_remove = set()
    if len(tuples_set) == 0:
        return True
    for x in tuples_set:
        diff = np.array(x) - np.array(y)
        if all(diff < 0):  # X dominates Y
            if len(to_remove) == 0:
                return False
            else:
                break
        elif all(diff > 0):  # Y dominates X
            to_remove.add(x)

    if len(to_remove) == 0:
        return True
    else:
        tuples_set = tuples_set - to_remove
        return True

def add_to_dict_set(d: dict, to_add: tuple, i: int):
    if i not in d:
        d[i] = set()
    d[i].add(to_add)


if __name__ == "__main__":
    get_dominance("../resources/dataset.csv", naive_dominance)
