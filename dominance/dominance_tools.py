from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np
from ast import literal_eval

class NaiveDominance:

    def __init__(self):
        self.tuples_dict = dict()
        self.distance_matrix = None
        self.on_distance_dom = dict()

    def get_dominance(self, path: str, dominance_funct, HSs : dict):
        diff_mtx = DiffMatrix(path)
        diff_mtx.load()
        self.distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides(HSs['lhs'], HSs['rhs']))
        self.distance_matrix = dominance_funct(self.distance_matrix, HSs['lhs'], HSs['rhs'])
        return self.distance_matrix

    def naive_dominance(self, d_mtx: pnd.DataFrame, lhs: list, rhs: list) -> pnd.DataFrame:
        distance_values = list(set(np.asarray(d_mtx.iloc[:, rhs].values, dtype='int').flatten()))
        distance_values.sort(reverse=True)
        max_dist = max(distance_values)
        df_keys = list(self.distance_matrix.keys())
        df_keys.remove('RHS')
        for dist in distance_values:
            df_act_dist = d_mtx[d_mtx.RHS == dist]
            rows_to_add = dict()
            for index, row in df_act_dist[df_keys].iterrows():
                last_row = tuple(row.values.tolist())
                if len(self.tuples_dict) == 0 or self.check_dominance(last_row, dist):
                     rows_to_add[index] = last_row
            rows_to_add = self.clean_tuple_dict(rows_to_add)
            self.tuples_dict.update(rows_to_add)
        return d_mtx[d_mtx.index.map(lambda x: x in self.tuples_dict.keys())]

    def check_dominance(self, y: tuple, dist) -> bool:
        # X dominates X iff foreach x in X, foreach y in Y, x <= y <=> x - y <= 0
        if len(self.tuples_dict) == 0:
            return True
        for x in list(self.tuples_dict.keys()):
            diff = np.array(self.tuples_dict[x]) - np.array(y)
            if all(diff <= 0):  # X dominates Y
                return False
            elif all(diff >= 0):  # Y dominates X
                del self.tuples_dict[x]
        return True

    def clean_tuple_dict(self, rows_to_add: dict) -> dict:
        if len(rows_to_add) == 1:
            return rows_to_add
        row_index = list(rows_to_add.keys())
        for i in range(0, len(row_index)):
            if row_index[i] in rows_to_add:
                for j in range(i+1, len(row_index)):
                    if row_index[j] in rows_to_add:
                        diff = np.array(rows_to_add[row_index[i]]) - np.array(rows_to_add[row_index[j]])
                        if all(diff >= 0):
                            del rows_to_add[row_index[i]]
                            break
                        elif all(diff <= 0):
                            del rows_to_add[row_index[j]]
        return rows_to_add

    def __add_to_dict_set(self, to_add: set, i: int):
        if i not in self.on_distance_dom:
            self.on_distance_dom[i] = set()
        self.on_distance_dom[i] = self.on_distance_dom[i].union(to_add)


if __name__ == "__main__":
    import time
    nd = NaiveDominance()
    start = time.clock()
    print(nd.get_dominance("../resources/dataset.csv", nd.naive_dominance, {"lhs": [1, 2, 3], "rhs": [0]}))
    print("elapsed time: ", time.clock() - start)