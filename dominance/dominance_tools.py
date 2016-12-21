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
        dominance_funct(self.distance_matrix, HSs['lhs'], HSs['rhs'])

    def naive_dominance(self, d_mtx: pnd.DataFrame, lhs: list, rhs: list):
        distance_values = list(set(np.asarray(d_mtx.iloc[:, rhs].values, dtype='int').flatten()))
        distance_values.sort(reverse=True)
        max_dist = max(distance_values)
        for dist in distance_values:
            df_act_dist = d_mtx[d_mtx.RHS == dist]
            rows_to_add = set()
            for index, row in df_act_dist[lhs].iterrows():
                last_row = tuple(row.values.tolist())
                if len(self.tuples_set) == 0 or self.check_dominance(last_row):
                    rows_to_add.add(last_row)
                self.__add_to_dict_set(rows_to_add, dist)
            self.tuples_set = self.tuples_set.union(rows_to_add)
            print(self.tuples_set)
        print(self.on_distance_dom)
        # print(len(previous))

    def check_dominance(self, y: tuple) -> bool:
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

    def __add_to_dict_set(self, to_add: set, i: int):
        if i not in self.on_distance_dom:
            self.on_distance_dom[i] = set()
        self.on_distance_dom[i] = self.on_distance_dom[i].union(to_add)


if __name__ == "__main__":
    nd = NaiveDominance()
    nd.get_dominance("../resources/dataset.csv", nd.naive_dominance, {'lhs': [1, 2, 3], 'rhs': [0]})
