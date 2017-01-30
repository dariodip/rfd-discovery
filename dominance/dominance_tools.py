from loader.distance_mtr import DiffMatrix
import pandas as pnd
import numpy as np


class RFDDiscovery:

    def __init__(self, print_res=False):
        self.pool = dict()
        self.distance_matrix = None
        self.on_distance_dom = dict()
        self.min_vector = None
        self.on_minimum_df = None
        self.rfds = None
        self.print_res = print_res

    def get_dominance(self, path: str, dominance_funct, hss: dict, options: dict):
        diff_mtx = DiffMatrix(path,options)
        diff_mtx.load()
        # self.distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides(hss['lhs'], hss['rhs']))
        self.distance_matrix = diff_mtx.distance_matrix(hss)
        self.distance_matrix = dominance_funct(self.distance_matrix, hss['lhs'], hss['rhs'])
        return self.rfds

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
                current_range_row = row.values.tolist()
                if len(self.pool) == 0 or self.__check_dominance(current_range_row, pool_rows_to_delete):  # dom. check
                    pool_rows_to_add[index] = current_range_row  # if the row passes the test then add it in the pool
            old_pool = self.pool.copy()  # copy the pool in order to use it into __find_rfd
            for pool_key in pool_rows_to_delete:  # remove dominating rows from the pool
                del self.pool[pool_key]
            # add rows that pass the test TODO converting in DF
            pool_rows_to_add = self.__clean_pool(pool_rows_to_add)  # clean pool
            selected_row = selected_row + list(pool_rows_to_add.keys())
            self.pool.update(pool_rows_to_add)  # add non-dominating rows into the pool
            # filter selected rows only
            df_distance_range_filtered = df_distance_range[df_distance_range.index.isin(selected_row)]

            self.__check_min(df_distance_range_filtered[df_keys], dist)  # create minimum on range vector
            # find effective rfd
            self.__find_rfd(self.on_minimum_df[self.on_minimum_df.RHS == dist][df_keys], dist, old_pool)

        self.rfds.drop_duplicates(subset=df_keys, inplace=True)
        self.rfds.reset_index(inplace=True)
        if self.print_res:
            print("Minimum df \n", self.on_minimum_df)
            print("Pool:\n", self.pool)
            print("RFDS:\n", self.rfds)
            print("D_MTX:\n", d_mtx[d_mtx.index.isin(selected_row)])
        return self.rfds  # se una sola a nan è dip

    def __check_min(self, df_act_dist: pnd.DataFrame, dist: int) -> None:
        """
        For each range, check whether one of its rows' values is minimum on row's pool.
        Add that minimum in self.min_vector and in self.on_minimum_df
        :param df_act_dist: current main data frame range
        :param dist: current distance
        :return: None
        """
        act_min = df_act_dist.min()
        compare = act_min < self.min_vector
        self.min_vector = np.array([self.min_vector[i] if not compare[i] else act_min[i] for i in range(len(act_min))])
        for index, row in df_act_dist.iterrows():
            vect = [False if not compare[i] else act_min[i] == row[i] for i in range(len(act_min))]
            vect = [np.nan if not vect[i] else act_min[i] for i in range(len(act_min))]
            self.on_minimum_df.loc[index] = np.array([dist] + vect)
            if not all(np.isnan(vect)):
                self.__all_rfds(vect, dist)

    def __find_rfd(self, current_df, dist: int, old_pool: dict) -> None:
        """
        Find RFDs for current distance.
        :param current_df: portion of the main data frame formed by the rows with
               distance is equal to dist
        :param dist: current distance
        :param old_pool: the pool before update
        """
        for index, row in current_df.iterrows():
            #  case 1: all rfds or |nan| <= 1
            nan_count = sum(np.isnan(row))
            if nan_count <= 1:
                self.__all_rfds(row.tolist(), dist)
            # case 3:   2 <= |nan| <= |LHS_ATTR|
            elif 2 <= nan_count:
                self.__any_rfds(row, dist, old_pool) # TODO se tutti nan

    def __check_dominance(self, y: list, rows_to_delete: set) -> bool:
        """
        Recalling: X dominates Y iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0
        Check for each row in the current pool, if (1) one of this is dominated by Y or if (2) this row dominates Y.
        Case (1):
                Return false (Do nothing)
        Case (2):
                Add the array who dominate into a data structure containing values to be removed
        :param y: current array to check
        :param rows_to_delete: a set containing values to be removed
        :return: True if Y is not dominated, False if Y is dominated
        """
        if len(self.pool) == 0:
            return True
        for x in list(self.pool.keys()):
            diff = np.array(self.pool[x]) - np.array(y)
            if all(diff <= 0):  # Y dominates X
                return False
            elif all(diff >= 0):  # X dominates Y
                rows_to_delete.add(x)
        return True

    def __check_dominance_single(self, y: np.array, old_pool: dict, dist: int) -> bool:
        """
        Check, for each single value (previously set to nan), if it dominates (is greater or equals) another value
         in the pool
        :param y: array for which it checks if its values dominate some value in the pool
        :param old_pool: the pool before update
        :return: True if at least one value in y dominates a value in the old pool's array
        """
        pool_keys = list(old_pool)
        for i in range(len(pool_keys)):
            diff = y - np.array(old_pool[pool_keys[i]])
            new_y = np.array([np.nan if diff[j] > 0 else y[j] for j in range(len(y))])
            print("----------------------------------")
            print("Y:\n", y)
            print("Old Pool:\n", old_pool)
            print("Selected Pool:\n", old_pool[pool_keys[i]])
            print("Sliced Pool:\n", pool_keys[:i] + pool_keys[i+1:])
            print("New Y:\n", new_y)
            print("----------------------------------")
            if self.__check_dominance_pool_slice(new_y, old_pool, pool_keys[:i] + pool_keys[i+1:]):
                print("*******new Y to add", new_y)
                self.__add_rfd(new_y, dist)
                return False
        return True

    def __check_dominance_pool_slice(self, y: np.array, pool: dict, sliced_pool_keys: list) -> bool:
        """
        TODO change pool's name

        :param y:
        :param pool:
        :param sliced_pool_keys:
        :return: True if Y dominates at least one vector in the sliced pool
        """
        for x_p in sliced_pool_keys:
            diff = y - np.array(pool[x_p])
            if not self.__gte_or_nan(diff):
                return True
        return False

    def __check_dominance_nan(self, y: np.array, old_pool: dict) -> bool:
        """
        Recalling: X dominates Y (with NANs) iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0 || x - y == nan
        Check if y dominates at least one value in the pool (including NAN values)
        :return: True if Y dominates at least one vector in the pool
        """
        for x in list(old_pool.keys()):
            diff = np.array(y) - np.array(old_pool[x])
            if self.__gt_or_nan(diff):  # this should return T if all >= 0 or nan, false otherwise
                return True
        return False

    def __all_rfds(self, row: list, dist: int) -> None:
        """
        Case [1]: All values are not NAN.
        Create a diagonal matrix containing the RFD in the main diagonal, then add this into RFD's data frame.
        :param row: the row containing RFD
        :param dist: the distance where RFD is located
        """
        diagonal_matrix = self.__extract_diagonal(row)
        for i in range(diagonal_matrix.shape[1]):
            if all(np.isnan(diagonal_matrix[..., i])):  # this occurs when not all elements are not NAN
                continue
            self.__add_rfd(diagonal_matrix[..., i], dist)

    def __any_rfds(self, row: pnd.Series, dist: int, old_pool: dict) -> None:
        """
        Case [2]: Some value is not NAN.
        Check the 2 sub-cases:
            1) row dominates at least one array in the old pool (no rfd)
            2) row (as it is) not dominates some array in the old pool:
            check on single value, then
                2.1) if a single value dominates one value in the old pool -> add to rfd
                2.2) otherwise no rfd is discovered
        :param row: the row containing RFD
        :param dist: the distance where RFD is located
        :param old_pool: the pool before update
        """
        compl_row = self.__complement_nans(row)
        if self.__check_dominance_nan(compl_row, old_pool):  # compl_row dominantes at least one row: case 6
            return
        elif self.__check_dominance_single(compl_row, old_pool, dist):  # check on single attributes
            self.__add_rfd(compl_row, dist)

    def __add_rfd(self, rfd, dist) -> None:
        """
        Add a specific RFD into the data frame containing them using the required format.
        :param rfd: a discovered RFD
        :param dist: the distance where RFD is located
        """
        rfds_to_add = [dist] + list(rfd)
        self.rfds.loc[self.rfds.shape[0]] = rfds_to_add  # add rfd to RFD's data frame

    def __complement_nans(self, row: pnd.Series) -> np.array:
        """
        Given an array (row), for each entry, if it is NAN, set it to its numeric value, if it is not nan, set it to nan
        :param row: array to complementary
        :return: the complementary array
        """
        coll_row = np.array([self.distance_matrix.loc[row.name][i+1]  # TODO check if it works
                             if np.isnan(row[i])
                             else np.nan
                             for i in range(len(row))])
        return coll_row

    def __initialize_var__(self, rhs, lhs, cols):
        """
        Initialize variables. (just for readability)
        """
        self.on_minimum_df = pnd.DataFrame(columns=cols)
        self.min_vector = np.zeros(len(lhs))
        self.min_vector.fill(np.inf)
        self.rfds = pnd.DataFrame(columns=cols)

    @staticmethod
    def __clean_pool(rows_to_add: dict) -> dict:
        """
        Clean the rows to add's pool by removing values dominated by other
        :param rows_to_add: a dict containing rows to add into the pool
        :return: a clean subset of rows_to_add
        """
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

    @staticmethod
    def __extract_diagonal(row: np.array) -> np.ndarray:
        """
        Create a diagonal matrix having row's value in its diagonal.
         This is used to fast insert RFDs into the data frame.
        :param row: matrix's diagonal
        :return: a diagonal matrix having row as diagonal
        """
        # create a diagonal matrix, fill it with NANs, set all the elements in the diagonal to 1,
        # then set all the elements in the diagonal to the dependency values
        diag_matrix = np.zeros((len(row), len(row)))
        diag_matrix.fill(np.nan)
        np.fill_diagonal(diag_matrix, 0)
        diag_matrix = diag_matrix + np.diag(np.array(row))
        return diag_matrix

    @staticmethod
    def __gt_or_nan(to_check):
        """
        Check if each value is greater than zero or NAN (where NAN is np.nan)
                https://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html
        :param to_check: an array in which check
        :return: true if each value is greater than zero or NAN, false otherwise
        """
        for i in to_check:
            if i < 0:
                return False
        return True

    @staticmethod
    def __gte_or_nan(to_check):
        """
        Check if each value is greater than zero or NAN (where NAN is np.nan)
                https://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html
        :param to_check: an array in which check
        :return: true if each value is greater than zero or NAN, false otherwise
        """
        for i in to_check:
            if i <= 0:
                return False
        return True
