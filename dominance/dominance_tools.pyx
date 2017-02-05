#!python
#defining NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#cython: wraparound=False, nonecheck=False, optimize.use_switch=True, optimize.unpack_method_calls=True

cimport cython
import pandas as pnd
cimport numpy as np
import numpy as np
from libc.math cimport isnan

NAN_PH = str(np.nan)

cdef class RFDDiscovery(object):

    cdef object pool
    cdef object on_distance_dom
    cdef object min_vector
    cdef object on_minimum_df
    cdef object rfds
    cdef cython.bint print_res
    cdef object distance_matrix
    cdef cython.bint compiled
    cdef object rfd_to_add
    cdef unsigned int rfd_count

    def __init__(self, dist_matrix: pnd.DataFrame, print_res=False):
        self.compiled = cython.compiled
        self.pool = dict()
        self.on_distance_dom = dict()
        self.min_vector = None
        self.on_minimum_df = None
        self.rfds = None
        self.print_res = print_res
        self.distance_matrix = dist_matrix
        self.rfd_to_add = set()
        self.rfd_count = 0

    cpdef object get_rfds(self, object dominance_funct, hss: dict):
        # self.distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides(hss['lhs'], hss['rhs']))
        self.distance_matrix = dominance_funct(self.distance_matrix, hss['lhs'], hss['rhs'])
        return self.rfds

    cpdef object standard_algorithm(self, d_mtx: pnd.DataFrame, lhs : list, rhs : list):
        self.__initialize_var__(rhs, lhs, d_mtx.columns)
        selected_row = list()
        distance_values = list(set(np.asarray(d_mtx[d_mtx.columns[0]], dtype='int').flatten()))
        distance_values.sort(reverse=True)
        df_keys = list(self.distance_matrix.keys())
        df_keys.remove('RHS')
        cdef double dist = 0.0
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
            # add rows that pass the test
            pool_rows_to_add = clean_pool(pool_rows_to_add)  # clean pool
            selected_row = selected_row + list(pool_rows_to_add.keys())
            self.pool.update(pool_rows_to_add)  # add non-dominating rows into the pool
            # filter selected rows only
            df_distance_range_filtered = df_distance_range[df_distance_range.index.isin(selected_row)]
            self.__check_min(df_distance_range_filtered[df_keys], dist)  # create minimum on range vector
            # find effective rfd
            self.__find_rfd(self.on_minimum_df[self.on_minimum_df.RHS == dist][df_keys], dist, old_pool)

        if self.print_res:
            print("Minimum df \n", self.on_minimum_df)
            print("Pool:\n", self.pool)
            print("RFDS:\n", self.rfds)
            print("D_MTX:\n", d_mtx[d_mtx.index.isin(selected_row)])
        return self.rfds  # se una sola a nan è dip

    cpdef is_compiled(self):
        return self.compiled

    cdef void __check_min(self, df_act_dist: pnd.DataFrame, double dist):
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
            #vect = [False if not compare[i] else act_min[i] == row[i] for i in range(len(act_min))]
            #vect = [np.nan if not vect[i] else act_min[i] for i in range(len(act_min))]
            vect = [np.nan if not compare[i] or act_min[i] != row[i] else act_min[i] for i in range(len(act_min))]
            self.on_minimum_df.loc[index] = np.array([dist] + vect)
            if not all(np.isnan(vect)):
                self.__all_rfds(vect, dist)

    cdef __find_rfd(self, current_df: pnd.DataFrame, double dist, old_pool: dict):
        """
        Find RFDs for current distance.
        :param current_df: portion of the main data frame formed by the rows with
               distance is equal to dist
        :param dist: current distance
        :param old_pool: the pool before update
        """
        cdef unsigned int nan_count = 0
        for index, row in current_df.iterrows():
            #  case 1: all rfds or |nan| <= 1
            nan_count = sum(np.isnan(row))
            if nan_count <= 1:
                self.__all_rfds(row.tolist(), dist)
            # case 2:   2 <= |nan| < |LHS_ATTR|
            elif 2 <= nan_count < len(row):
                self.__any_rfds(row, dist, old_pool)
            # case 3:   |nan| == |LHS_ATTR|
            else:
                compl_row = self.__complement_nans(row)
                if self.__check_dominance_single(compl_row, old_pool, dist):  # check on single attributes
                    self.__add_rfd(compl_row)
        cdef object to_add
        for rfd in self.rfd_to_add:
            #k = self.rfds.shape[0]
            ta_rfd = [i if i != NAN_PH else np.nan for i in list(rfd)]
            to_add = [dist] + ta_rfd
            self.rfds.loc[self.rfd_count] = to_add  # add rfd to RFD's data frame
            self.rfd_count += 1
        self.rfd_to_add = set()

    cdef cython.bint __check_dominance(self, y: list, rows_to_delete: set):
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

    cdef cython.bint __check_dominance_single(self, y: np.array, old_pool: dict, double dist):
        """
        Check, for each single value (previously set to nan), if it dominates (is greater or equals) another value
         in the pool
        :param y: array for which it checks if its values dominate some value in the pool
        :param old_pool: the pool before update
        :return: True if at least one value in y dominates a value in the old pool's array
        """
        pool_keys = list(old_pool)
        cdef cython.bint flag = True
        cdef int i
        for i in range(len(pool_keys)):
            diff = y - np.array(old_pool[pool_keys[i]])
            new_y = np.array([np.nan if diff[j] > 0 else y[j] for j in range(len(y))])
            if not self.__check_dominance_pool_slice(new_y, old_pool, pool_keys[:i] + pool_keys[i+1:]):
                self.__add_rfd(new_y)
                flag = False
        return flag

    cdef cython.bint __check_dominance_pool_slice(self, y: np.array, pool: dict, sliced_pool_keys: list):
        """
        Recalling: X dominates Y (with NANs) iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0 || x - y == nan
        Check if y dominates at least one value in the pool (including NAN values)
        :param y: row to check
        :param pool: row's pool to analyze
        :param sliced_pool_keys: pool's key without the one used to create y
        :return: True if Y dominates at least one vector in the sliced pool
        """
        for x_p in sliced_pool_keys:
            diff = y - np.array(pool[x_p])
            if gt_or_nan(diff):
                return True
        return False

    cdef cython.bint __check_dominance_nan(self, y: np.array, old_pool: dict):
        """
        Recalling: X dominates Y (with NANs) iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0 || x - y == nan
        Check if y dominates at least one value in the pool (including NAN values)
        :return: True if Y dominates at least one vector in the pool
        """
        for x in list(old_pool.keys()):
            diff = np.array(y) - np.array(old_pool[x])
            if gt_or_nan(diff):  # this should return T if all >= 0 or nan, false otherwise
                return True
        return False

    cdef void __all_rfds(self, row: list, double dist):
        """
        Case [1]: All values are not NAN.
        Create a diagonal matrix containing the RFD in the main diagonal, then add this into RFD's data frame.
        :param row: the row containing RFD
        :param dist: the distance where RFD is located
        """
        diagonal_matrix = extract_diagonal(np.array(row))
        for i in range(diagonal_matrix.shape[1]):
            if all(np.isnan(diagonal_matrix[..., i])):  # this occurs when not all elements are not NAN
                continue
            self.__add_rfd(diagonal_matrix[..., i])

    cdef void __any_rfds(self, row: pnd.Series, double dist, old_pool: dict):
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
            self.__add_rfd(compl_row)

    cdef void __add_rfd(self, np.ndarray rfd):
        """
        Add a specific RFD into the data frame containing them using the required format.
        :param rfd: a discovered RFD
        :param dist: the distance where RFD is located
        """
        rfd_l = rfd.tolist()
        l_rfd = tuple(i if not np.isnan(i) else NAN_PH for i in rfd_l)
        self.rfd_to_add.add(l_rfd)

    cdef np.ndarray __complement_nans(self, row: pnd.Series):
        """
        Given an array (row), for each entry, if it is NAN, set it to its numeric value, if it is not nan, set it to nan
        :param row: array to complementary
        :return: the complementary array
        """
        coll_row = np.array([self.distance_matrix.loc[row.name][i+1]
                             if np.isnan(row[i])
                             else np.nan
                             for i in range(len(row))])
        return coll_row

    cpdef void __initialize_var__(self, rhs, lhs, cols):
        """
        Initialize variables. (just for readability)
        """
        self.on_minimum_df = pnd.DataFrame(columns=cols, dtype=float)
        self.min_vector = np.zeros(len(lhs))
        self.min_vector.fill(np.inf)
        self.rfds = pnd.DataFrame(columns=cols, dtype=float)

cpdef clean_pool(rows_to_add: dict):
    """
    Clean the rows to add's pool by removing values dominated by other
    :param rows_to_add: a dict containing rows to add into the pool
    :return: a clean subset of rows_to_add
    """
    if len(rows_to_add) == 1:
        return rows_to_add
    row_index = list(rows_to_add.keys())
    cdef int i
    cdef int j
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

cpdef np.ndarray extract_diagonal(np.ndarray[double] row):
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

cpdef cython.bint gt_or_nan(np.ndarray[double] to_check):
    """
    Check if each value is greater than zero or NAN (where NAN is np.nan)
            https://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html
    :param to_check: an array in which check
    :return: true if each value is greater than zero or NAN, false otherwise
    """
    cdef double i = 0.0
    for i in to_check:
        if i < 0 and not isnan(i):
            return False
    return True

cpdef cython.bint gte_or_nan(np.ndarray[double] to_check):
    """
    Check if each value is greater than zero or NAN (where NAN is np.nan)
            https://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html
    :param to_check: an array in which check
    :return: true if each value is greater than zero or NAN, false otherwise
    """
    cdef double i = 0.0
    for i in to_check:
        if i <= 0 and not isnan(i):
            return False
    return True
