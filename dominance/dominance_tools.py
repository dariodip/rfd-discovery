from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np
import utils.utils as ut


class NaiveDominance:
    def __init__(self):
        self.pool = dict()
        self.distance_matrix = None
        self.on_distance_dom = dict()
        self.min_vector = None
        self.on_minimum_df = None
        self.rfds = None

    def get_dominance(self, path: str, dominance_funct, hss: dict):
        diff_mtx = DiffMatrix(path)
        diff_mtx.load()
        self.distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides(hss['lhs'], hss['rhs']))
        self.distance_matrix = dominance_funct(self.distance_matrix, hss['lhs'], hss['rhs'])
        return self.distance_matrix

    def __initialize_var__(self, rhs, lhs, cols):
        self.on_minimum_df = pnd.DataFrame(columns=cols)
        self.min_vector = np.zeros(len(lhs))
        self.min_vector.fill(np.inf)
        self.rfds = pnd.DataFrame(columns=cols)

    def naive_dominance(self, d_mtx: pnd.DataFrame, lhs: list, rhs: list) -> pnd.DataFrame:
        self.__initialize_var__(rhs, lhs, d_mtx.columns)
        selected_row = list()
        distance_values = list(set(np.asarray(d_mtx[d_mtx.columns[0]], dtype='int').flatten()))
        distance_values.sort(reverse=True)
        df_keys = list(self.distance_matrix.keys())
        df_keys.remove('RHS')

        for dist in distance_values:  # iterate on each different distance
            pool_rows_to_delete = set()  # rows to delete from the pool
            pool_rows_to_add = dict()  # row to add into the pool
            # filter the DF taking all rows into a specific distance range
            df_distance_range = d_mtx[d_mtx.RHS == dist]
            if df_distance_range.empty:
                continue
            for index, row in df_distance_range[df_keys].iterrows():  # extract a row from distance range
                # convert row in tuple in order to preserve ordering TODO maybe to remove
                current_range_row = tuple(row.values.tolist())
                if len(self.pool) == 0 or self.check_dominance(current_range_row, pool_rows_to_delete):  # dom. check
                    pool_rows_to_add[index] = current_range_row  # if the row passes the test then add it in the pool
            old_pool = self.pool.copy()  # copy the pool in order to use it into __find_rfd
            for key in pool_rows_to_delete:  # remove dominating rows from the pool
                del self.pool[key]
            # add rows that pass the test TODO converting in DF
            selected_row = selected_row + list(pool_rows_to_add.keys())
            pool_rows_to_add = self.clean_pool(pool_rows_to_add)  # clean pool
            self.pool.update(pool_rows_to_add)  # add non-dominating rows into the pool
            # filter selected rows only
            df_distance_range_filtered = df_distance_range[df_distance_range.index.isin(selected_row)]

            self.check_min(df_distance_range_filtered[df_keys], dist)  # create minimum on range vector
            # find effective rfd
            self.__find_rfd(self.on_minimum_df[self.on_minimum_df.RHS == dist][df_keys], dist, old_pool)

        print("Minimum df \n", self.on_minimum_df)
        print("Pool:\n", self.pool)
        print("RFDS:\n", self.rfds)
        print(selected_row)
        return d_mtx[d_mtx.index.isin(selected_row)]

    def __find_rfd(self, current_df, dist: int, old_pool: dict):
        for index, row in current_df.iterrows():
            #  case 1: all rfds or |nan| <= 1
            if all(~ np.isnan(np.array(row))):
                self.__all_rfds(row, dist)
                continue
            nan_count = sum(np.isnan(row))
            if nan_count == 1:
                self.__all_rfds(row, dist)
            # case 2:   2 <= |nan| <= |LHS_ATTR|
            elif 2 <= nan_count < len(row):
                self.__any_rfds(row, dist)

    def __any_rfds(self, row: pnd.Series, dist: int):
        pass  # TODO continue here

    def __all_rfds(self, row: pnd.Series, dist: int):
        # create a diagonal matrix, fill it with NANs, set all the elements in the diagonal to 1,
        # then set all the elements in the diagonal to dependency values
        diag_matrix = np.zeros((len(row), len(row)))
        diag_matrix.fill(np.nan)
        np.fill_diagonal(diag_matrix, 0)
        diag_matrix = diag_matrix + np.diag(np.array(row))
        for i in range(diag_matrix.shape[-1]):
            if all(np.isnan(diag_matrix[..., i])):  # this occurs when non all elements are notNAN
                continue
            rfds_to_add = [dist] + list(diag_matrix[..., i])
            self.rfds.loc[self.rfds.shape[0]] = rfds_to_add  # add rfd to RFD's data frame

    def check_dominance(self, y: tuple, rows_to_delete: set) -> bool:
        # X dominates Y iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0
        if len(self.pool) == 0:
            return True
        for x in list(self.pool.keys()):
            diff = np.array(self.pool[x]) - np.array(y)
            if all(diff <= 0):  # Y dominates X
                return False
            elif all(diff >= 0):  # X dominates Y
                rows_to_delete.add(x)
        return True

    def clean_pool(self, rows_to_add: dict) -> dict:
        if len(rows_to_add) == 1:
            return rows_to_add
        row_index = list(rows_to_add.keys())
        for i in range(0, len(row_index)):
            if row_index[i] in rows_to_add:
                for j in range(i + 1, len(row_index)):
                    if row_index[j] in rows_to_add:
                        diff = np.array(rows_to_add[row_index[i]]) - np.array(rows_to_add[row_index[j]])
                        if all(diff >= 0):
                            del rows_to_add[row_index[i]]
                            break
                        elif all(diff <= 0):
                            del rows_to_add[row_index[j]]
        return rows_to_add

    def check_min(self, df_act_dist: pnd.DataFrame, dist: int):
        act_min = df_act_dist.min()
        compare = act_min < self.min_vector
        self.min_vector = np.array([self.min_vector[i] if not compare[i] else act_min[i] for i in range(len(act_min))])
        for index, row in df_act_dist.iterrows():
            vect = [False if not compare[i] else act_min[i] == row[i] for i in range(len(act_min))]
            vect = [np.nan if not vect[i] else act_min[i] for i in range(len(act_min))]
            self.on_minimum_df.loc[index] = np.array([dist] + vect)

    def __add_to_dict_set(self, to_add: set, i: int):
        if i not in self.on_distance_dom:
            self.on_distance_dom[i] = set()
        self.on_distance_dom[i] = self.on_distance_dom[i].union(to_add)
