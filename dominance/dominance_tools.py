from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np


class NaiveDominance:

    def __init__(self):
        self.tuples_set = set()
        self.distance_matrix = None
        self.on_distance_dom = dict()

    def get_dominance(self, path: str, dominance_funct, HSs : dict):
        diff_mtx = DiffMatrix(path)
        diff_mtx.load()
        self.distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides(HSs['lhs'], HSs['rhs']))
        return dominance_funct(self.distance_matrix, HSs['lhs'], HSs['rhs'])

    def naive_dominance(self, d_mtx: pnd.DataFrame, lhs: list, rhs: list) -> pnd.DataFrame:
        distance_values = list(set(np.asarray(d_mtx.iloc[:, rhs].values, dtype='int').flatten()))
        distance_values.sort(reverse=True)
        max_dist = max(distance_values)
        df_keys = list(self.distance_matrix.keys())
        df_keys.remove('RHS')
        for dist in distance_values:
            df_act_dist = d_mtx[d_mtx.RHS == dist]
            rows_to_add = set()
            for index, row in df_act_dist[df_keys].iterrows():
                last_row = tuple(row.values.tolist())
                if len(self.tuples_set) == 0 or self.check_dominance(last_row, dist):
                    rows_to_add.add(last_row)
            rows_to_add = self.clean_tuple_set(rows_to_add)
            self.tuples_set = self.tuples_set.union(rows_to_add)
            self.__add_to_dict_set(rows_to_add, dist)
        return self.on_distance_dom

    def check_dominance(self, y: tuple, dist) -> bool:
        # X dominates X iff foreach x in X, foreach y in Y, x <= y <=> x - y <= 0
        to_remove = set()
        if len(self.tuples_set) == 0:
            return True
        for x in self.tuples_set:
            diff = np.array(x) - np.array(y)
            if all(diff <= 0):  # X dominates Y
                if len(to_remove) == 0:
                    return False
                else:
                    break
            elif all(diff >= 0):  # Y dominates X
                to_remove.add(x)
        if len(to_remove) == 0:
            return True
        else:
            self.tuples_set = self.tuples_set - to_remove
            return True

    def clean_tuple_set(self, rows_to_add: set) -> set:
        if len(rows_to_add) == 1:
            return rows_to_add
        l_rows = list(rows_to_add)
        for i in range(0, len(l_rows)):
            for j in range(i+1, len(l_rows)):
                diff = np.array(l_rows[i]) - np.array(l_rows[j])
                if all(diff >= 0):
                    if l_rows[j] in rows_to_add:
                        rows_to_add.remove(l_rows[j])
                elif all(diff <= 0):
                    if l_rows[i] in rows_to_add:
                        rows_to_add.remove(l_rows[i])
        return rows_to_add

    def __add_to_dict_set(self, to_add: set, i: int):
        if i not in self.on_distance_dom:
            self.on_distance_dom[i] = set()
        self.on_distance_dom[i] = self.on_distance_dom[i].union(to_add)


if __name__ == "__main__":
    nd = NaiveDominance()
    print(nd.get_dominance("../resources/dataset.csv", nd.naive_dominance, {'lhs': [1, 2, 3], 'rhs': [0]}))
