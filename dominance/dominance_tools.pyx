#!python
#defining NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#cython: wraparound=False, nonecheck=False, optimize.use_switch=True, optimize.unpack_method_calls=True

cimport cython
import pandas as pnd
cimport numpy as np
import numpy as np
from libc.math cimport isnan

NAN_PH = str(np.nan)

"""Module with the class implementing the algorithm used to find the Relaxed Functionals Dependencies"""

cdef class RFDDiscovery(object):
    """
    Class used to find the Relaxed Functional Dependencies RFDs of a given distance matrix. It allow to use different algorithm.
    It take a pandas' data frame containing a distance matrix obtained from other sources, like the class DiffMatrix in the module loader.
    Currently it contain an approximated version of the algorithm, called standard_algorithm, used to find the RFDs that besides return the found RFDs,
    it allow to print the results on the standard output. It work on the distance matrix by dividing it in range, where the range i
    contain all the row with value on the RHS equals to i. Another important structure is the pool. Each range i contain a pool,
    with an important property: each row in the pool does not dominate any row with distance on the RHS major or equal to i.
    """
    cdef object pool
    cdef object on_distance_dom
    cdef object min_vector
    cdef object on_minimum_df
    cdef public object rfds
    cdef cython.bint print_res
    cdef object distance_matrix
    cdef cython.bint compiled
    cdef object rfd_to_add
    cdef unsigned int rfd_count
    cdef object median_df
    np.seterr(all='ignore')


    def __init__(self, dist_matrix: pnd.DataFrame, print_res=False):
        """
        Initialize the parameters necessary to execute the algorithm. It takes a distance matrix as input and a boolean
        value that allow to print the results or not.
        :param dist_matrix: distance matrix from where we want to find the RFDs.
        :type dist_matrix: pandas.core.frame.DataFrame
        :param print_res: boolean value, True if we want to print the result in the standard output, False otherwise. Default behavior is as if set to False if no values is passed.
        :type print_res: bool
        """
        self.compiled = cython.compiled
        """Boolean value, True if the code was compiled with Cython, False otherwise"""
        self.pool = dict()
        """Dictionary containing the row's pool"""
        self.min_vector = None
        """List containing for each attribute the global minimun value"""
        self.on_minimum_df = None
        """
        Pandas' data frame containing, for each range, the refined version where each row in the range has on its attributes the value NaN if the attribute's
        value is not equal to the attribute's local minimun it found up to this range, the original value otherwise.
        """
        self.rfds = None
        """Data frame containing the found RFDs"""
        self.print_res = print_res
        """Boolean value, True if we want to print the result in the standard output, False otherwise."""
        self.distance_matrix = dist_matrix
        """The distance matrix from where we want to find the RFDs"""
        self.rfd_to_add = set()
        """Buffer containing unique RFDs discovered for a given distance."""
        self.rfd_count = 0
        """Number of found RFD"""
        self.median_df = dist_matrix.median(axis=0, numeric_only=True)
        """Attributes containing the attribute's values threshold"""


    cpdef object get_rfds(self, object dominance_funct, hss: dict):
        """
        This method called the dominance function given as parameter on the given division on rhs and lhs.
        :param dominance_funct: dominance function used to find the RFDs on the distance matrix
        :type dominance_funct: function
        :param hss: dictionary containing the division on rhs and lhs of the attribute. It contain two key 'lhs' and 'rhs', where 'lhs' contains valid columns indexes of attribute to put on the lhs and
        'rhs' contain a valid index of an attribute to put on the rhs.
        :type hss: dict
        :return: the found RFDs
        :rtype: pandas.core.frame.DataFrame
        """
        self.distance_matrix = dominance_funct(self.distance_matrix, hss['lhs'], hss['rhs'])
        return self.rfds

    cpdef object standard_algorithm(self, d_mtx: pnd.DataFrame, lhs : list, rhs : list):
        """
        This method execute the approximated algorithm on the given distance matrix. First of all, the algorithm takes all the rows
        with distance on the RHS greater than the threshold and, considering them as belonging to a single range, create the initial pool.
        After this initial step, it starts to find the RFDs from rows with distance on the RHS minor or equal to the threshold. It use an iterative method where
        for each iteration it work on a particular range i. During one iteration, it update the pool, refine the range i and
        find the RFDs on the current range. If the value of the instance attribute print_res is True, at the end of the algorithm
        it will print on the standard output the data frame containing the RFDs, the pool of the range 0 containing only rows that
        does not dominate any other rows in the distance matrix and the distance matrix's rows that during an iteration on the
        relative range, they were selected to be inserted in the pool.
        It is important to put on lhs and rhs the valid attributes' indexes used on the lhs and rhs on the distance matrix, because they are used to
        initialize correctly the instance variables min_vector and on_minimun_df.
        :param d_mtx: the distance matrix from where the RFDs must be found
        :type d_mtx: pandas.core.frame.DataFrame
        :param lhs: list of valid columns indexes of attributes positioned on the lhs of the distance matrix
        :type lhs: list
        :param rhs: list of valid column index of an attribute positioned on the rhs of the distance matrix
        :type rhs: list
        :return: the data frame containing the found RFDs
        :rtype: pandas.core.frame.DataFrame
        """
        self.__initialize_var__(rhs, lhs, d_mtx.columns) # initialize variables
        selected_row = list()  # list of non-dominating tuples

        distance_values = list(set(np.asarray(d_mtx[d_mtx['RHS'] <= self.median_df['RHS']]['RHS'], dtype='int').flatten()))  # all unq distances
        distance_values.sort(reverse=True)  # sort distances

        distance_gt = d_mtx[d_mtx['RHS'] > self.median_df['RHS']]

        df_keys = list(self.distance_matrix.keys())
        df_keys.remove('RHS')  # extract lhs keys
        cdef double dist = 0.0

        for index, row in distance_gt[df_keys].iterrows():
            pool_rows_to_delete = set()  # rows to delete from the pool
            pool_rows_to_add = dict()  # row to add into the pool
            current_range_row = row.values.tolist()
            if len(self.pool) == 0 or self.__check_dominance(current_range_row, pool_rows_to_delete):  # dom. check
                pool_rows_to_add[index] = current_range_row  # if the row passes the test then add it in the pool
            for pool_key in pool_rows_to_delete:  # remove dominating rows from the pool
                del self.pool[pool_key]
            pool_rows_to_add = clean_pool(pool_rows_to_add)  # clean pool
            self.pool.update(pool_rows_to_add)  # add non-dominating rows into the pool
        self.min_vector = np.array(pnd.DataFrame.from_dict(self.pool, orient='index').min().tolist())
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
            if not df_distance_range_filtered.empty:
                df_distance_range_filtered = df_distance_range_filtered[df_keys]\
                   .apply(self.clean_on_median, axis=1, raw=True, args=(df_keys,self.median_df))
                for index, row in df_distance_range_filtered[df_keys].iterrows():
                    current_range_row = row.values.tolist()
                    if self.__check_dominance_nan(current_range_row, old_pool):  # dom. check
                        df_distance_range_filtered[index] = None
                self.__check_min(df_distance_range_filtered[df_keys], dist)  # create minimum on range vector
                # find effective rfd
                self.__find_rfd(self.on_minimum_df[self.on_minimum_df.RHS == dist][df_keys], dist, old_pool)

        if self.print_res:
            print("Minimum df \n", self.on_minimum_df)
            print("Pool:\n", self.pool)
            print("RFDS:\n", self.rfds)
            print("D_MTX:\n", d_mtx[d_mtx.index.isin(selected_row)])
        return self.rfds  # se una sola a nan è dip

    @staticmethod
    cdef object clean_on_median(object x, object df_keys, object median_df):
        # diff = x - m > 0 <=> x > m => np.nan
        diff = x - median_df[df_keys]
        return np.array([np.nan if diff[i] > 0 else x[i] for i in range(len(x))])

    cpdef is_compiled(self):
        """
        Return the value of the instance variable compiled.
        :return: True if the code is compiled, False if it was interpreted
        :rtype: bool
        """
        return self.compiled

    cdef void __check_min(self, df_act_dist: pnd.DataFrame, double dist):
        """
        On a range dist, it calculate the refined version and add it on the data frame
        on_minimun_df. Recalling, for each range, check whether one of its rows' values is minimum on row's pool.
        Add that minimum in self.min_vector and in self.on_minimum_df
        :param df_act_dist: portion of the distance matrix corresponding to the distance dist
        :type df_act_dist: pandas.core.frame.DataFrame
        :param dist: current distance
        :type dist: double
        """
        act_min = df_act_dist.min()  # range minumum
        compare = act_min < self.min_vector  # which components of rm are lt global mimimum?
        #update global minimum
        self.min_vector = np.array([self.min_vector[i] if not compare[i] else act_min[i] for i in range(len(act_min))])
        min_vect = [np.nan if not compare[i] else act_min[i] for i in range(len(act_min))]
        # for each row in current range
        for index, row in df_act_dist.iterrows():
            # giving an array row in current range
            # create a list having np.nan in i if row[i] does not contribute in global minimum
            vect = [np.nan if not compare[i] or act_min[i] != row[i] else act_min[i] for i in range(len(act_min))]
            # add vect to df of processed arrays
            self.on_minimum_df.loc[index] = np.array([dist] + vect)
        # add elements that contribute to global minimum as RFDs
        if not all(np.isnan(min_vect)):
            self.__all_rfds(min_vect, dist)

    cdef __find_rfd(self, current_df: pnd.DataFrame, double dist, old_pool: dict):
        """
        Given the refined range for the distance dist, the pool before being upgraded with the non dominant row found on distance dist
        and the current distance dist, it find the RFDs associated to this distance. For each row, check the number of NaN values in
        that row, and according to this number choose one of the three path of the algorithm.
        :param current_df: portion of the data frame formed by the rows in the refined range with distance equal to dist
        :type current_df: pandas.core.frame.DataFrame
        :param dist: current distance
        :type dist: double
        :param old_pool: the pool before the upgrade with the non dominant row found on distance dist
        :type old_pool: dict
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
        # here self.rfd_to_add contains all the RFDs discovered for this distance, let's add them in the rfd's df
        cdef object to_add
        for rfd in self.rfd_to_add:
            ta_rfd = [i if i != NAN_PH else np.nan for i in list(rfd)]  # remove nan placeholder
            to_add = [dist] + ta_rfd  # create rfd row
            self.rfds.loc[self.rfd_count] = to_add  # add rfd to RFD's data frame
            self.rfd_count += 1
        self.rfd_to_add = set()  # empty rfd_to_add

    cdef cython.bint __check_dominance(self, y: list, rows_to_delete: set):
        """
        Given a row y, this method check if y dominate any row in the pool. When it find
        some row x that dominate y, it will be added to the set rows_to_delete containing the
        pool's rows which must be removed.
        Recalling: X dominates Y iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0
        :param y: current row to check
        :type y: list
        :param rows_to_delete: a set containing pool's row to be removed
        :type rows_to_delete: set
        :return: True if Y does not dominate any row in the pool, False otherwise.
        :rtype: cython.bint
        """
        if len(self.pool) == 0: # empty pool, no dominance possible
            return True
        for x in list(self.pool.keys()):    # for each array in pool
            diff = np.array(self.pool[x]) - np.array(y) # compute difference
            if any(np.isnan(diff)):
                np.place(diff, np.isnan(diff), np.inf)
            if all(diff <= 0):  # Y dominates X
                return False
            elif all(diff >= 0):  # X dominates Y
                rows_to_delete.add(x)
        return True # no dominance found

    cdef cython.bint __check_dominance_single(self, y: np.array, old_pool: dict, double dist):
        """
        Check, for each single value (previously set to nan), if it dominates another value
        in the pool old_pool. For each row x in the old pool, create a new row called new_y with
        value on attribute j set to NaN if y[j] > x[j], y[j] otherwise. If new_y does not dominate
        any row in the old_pool excluding x, add new_y as RFD.
        :param y: row for which it checks if its values dominate some value in the pool
        :type y: numpy.array
        :param old_pool: the pool before update
        :param dist: current distance
        :type dist: double
        :return: True if at least one value in y dominates a row in the old pool's array
        """
        pool_keys = list(old_pool) # pool as list (in order to fix an ordering and do slice)
        cdef cython.bint flag = True
        cdef int i
        for i in range(len(pool_keys)):  # for each row in pool
            diff = y - np.array(old_pool[pool_keys[i]]) # get difference
            new_y = np.array([np.nan if diff[j] > 0 else y[j] for j in range(len(y))])  # create y_p
            # check for each other arrays in the pool if new_y dominates one of them
            if not self.__check_dominance_pool_slice(new_y, old_pool, pool_keys[:i] + pool_keys[i+1:]):
                self.__add_rfd(new_y)
                flag = False  # no dominance found, don't add rfd for y!
        return flag

    cdef cython.bint __check_dominance_pool_slice(self, y: np.array, pool: dict, sliced_pool_keys: list):
        """
        Given a row y, this method check if y dominate any row in the pool given as parameter, excluded the row used to create y.
        When it find some row x that is dominated by y, the method return False.
        Recalling: X dominates Y (with NANs) iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0 || x - y == nan
        Check if y dominates at least one value in the pool (including NAN values)
        :param y: current row to check
        :type y: list
        :param pool: row's pool to analyze
        :type pool: dict
        :param sliced_pool_keys: pool rows' key without the one used to create y
        :type sliced_pool_keys: list
        :return: True if Y does not dominate any row in the sliced pool, False otherwise.
        :rtype: cython.bint
        """
        for x_p in sliced_pool_keys:
            diff = y - np.array(pool[x_p])
            if gt_or_nan(diff): # this should return T iff all >= 0 or nan, false otherwise
                return True
        return False

    cdef cython.bint __check_dominance_nan(self, y: np.array, old_pool: dict):
        """
        Given a row y, this method check if y dominate any row in the pool old_pool. When it find some row x
        that is dominated by y, the method return False.
        Recalling: X dominates Y (with NANs) iff foreach x in X, foreach y in Y, x >= y <=> x - y >= 0 || x - y == nan
        Check if y dominates at least one value in the pool (including NAN values)
        :param y: current row to check
        :type y: numpy.array
        :param old_pool: pool to analyze
        :type old_pool: dict
        :return: True if Y dominates at least one row in the pool
        :rtype cython.bint
        """
        for x in list(old_pool.keys()):
            diff = np.array(y) - np.array(old_pool[x])
            if gt_or_nan(diff):  # this should return T iff all >= 0 or nan, false otherwise
                return True
        return False

    cdef void __all_rfds(self, row: list, double dist):
        """
        Given a row, add for each row's value an RFD with lhs given by the row's value and as
        rhs the distance dist. It implement the case of __find_rfd where all row's value ar not NaN.
        Create a diagonal matrix containing the RFDs in the main diagonal, then add this into the RFDs' data frame.
        :param row: the row containing RFDs
        :type row: list
        :param dist: the distance where RFDs is located
        :type dist: double
        """
        diagonal_matrix = extract_diagonal(np.array(row))
        for i in range(diagonal_matrix.shape[1]):
            if all(np.isnan(diagonal_matrix[..., i])):  # this occurs when not all elements are not NAN
                continue
            self.__add_rfd(diagonal_matrix[..., i])

    cdef void __any_rfds(self, row: pnd.Series, double dist, old_pool: dict):
        """
        This function implement the case two of __find_rfd, where the number of row's value set to NaN is in
        the interval [2, number of attribute). In that case, he create a complement row compl_row where each value of this row is
        equal to NaN if the corresponding attribute on row is not NaN, the original value in the distance matrix otherwise.
        If compl_row dominate some value on the old_pool he does not find any RFD. If not, he check the presence
        of RFD on the single attribute of compl_row. If it does not find any RFD in this way, he add compl_row as RFD.
        :param row: the row that can containing RFDs
        :type row: pandas.core.series.Series
        :param dist: the distance where RFDs are located
        :type dist: double
        :param old_pool: the pool before update
        :type old_pool: dict
        """
        compl_row = self.__complement_nans(row)
        if self.__check_dominance_nan(compl_row, old_pool):  # compl_row dominantes at least one row: case 6
            return
        elif self.__check_dominance_single(compl_row, old_pool, dist):  # check on single attributes
            self.__add_rfd(compl_row)

    cdef void __add_rfd(self, np.ndarray rfd):
        """
        Add a specific RFD rfd into the data frame rfds using the required format.
        :param rfd: a discovered RFD
        :type rfd: np.ndarray
        """
        rfd_l = rfd.tolist()  # convert to list
        # convert in tuple (immutable) and remove np.nan (because np.nan != np.nan), using NAN_PH
        l_rfd = tuple(i if not np.isnan(i) else NAN_PH for i in rfd_l)
        self.rfd_to_add.add(l_rfd) # add processed string in the buffer

    cdef np.ndarray __complement_nans(self, row: pnd.Series):
        """
        Given an row called row, for each entry, if it is NaN, set it to its numeric value memorized in the distance matrix,
        if it is not NaN, set it to NaN.
        :param row: row to be complementary
        :type pandas.core.series.Series
        :return: the complemented row
        :rtype: numpy.ndarray
        """
        coll_row = np.array([self.distance_matrix.loc[row.name][i+1]
                             if np.isnan(row[i])
                             else np.nan
                             for i in range(len(row))])
        return coll_row

    cpdef void __initialize_var__(self, rhs, lhs, cols):
        """
        Initialize the instance variables on_minimun_df, min_vector and rfds using the
        columns' name and the division on rhs and lhs given as input
        :param rhs: integer index of the column positioned on the rhs of the distance matrix
        :type rhs: list
        :param lhs: integers indexes of the columns positioned on the lhs of the distance matrix
        :type lhs: list
        :param cols: columns' header for on_minimun_df and rfds data frames
        :type cols: list
        """
        self.on_minimum_df = pnd.DataFrame(columns=cols, dtype=float)
        self.min_vector = np.zeros(len(lhs))
        self.min_vector.fill(np.inf)
        self.rfds = pnd.DataFrame(columns=cols, dtype=float)

cpdef clean_pool(rows_to_add: dict):
    """
    Give a dictionary of rows to add into the pool, clean that dictionary by removing rows that dominate other
    rows into the dict
    :param rows_to_add: a dict containing rows to add into the pool
    :type rows_to_add: dict
    :return: a clean subset of rows_to_add, where each row does not dominate any other rows into the dict
    :rtype: dict
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
    Create a diagonal matrix having row's value into its diagonal.
    This is used to fast insert RFDs into the data frame.
    :param row: matrix's diagonal
    :type row: numpy.ndarray[double]
    :return: a diagonal matrix having row's value into the diagonal
    :rtype: numpy.ndarray
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
    Check for each value in to_check if it is greater or equal to zero or NaN.
    :param to_check: the row to check
    :type to_check: numpy.ndarray[double]
    :return: True if each value is greater o equal than zero or NaN, False otherwise
    :rtype: cython.bint
    """
    cdef double i = 0.0
    for i in to_check:
        if i < 0 and not isnan(i):
            return False
    return True

cpdef cython.bint gte_or_nan(np.ndarray[double] to_check):
    """
    Check for each value in to_check if it is greater to zero or NaN.
    :param to_check: the row to check
    :type to_check: numpy.ndarray[double]
    :return: True if each value is greater than zero or NaN, False otherwise
    :rtype: cython.bint
    """
    cdef double i = 0.0
    for i in to_check:
        if i <= 0 and not isnan(i):
            return False
    return True
