#!python
#defining NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#cython: wraparound=False, nonecheck=False, optimize.use_switch=True, optimize.unpack_method_calls=True

cimport cython
import pandas as pnd
import numpy as np
cimport numpy as np
from nltk.corpus import wordnet as wn
import loader.levenshtein_wrapper as lw

pnd.set_option('display.width', 320)


cdef class DiffMatrix:
    """Class used to build the the difference matrix respect to a Relaxed Functional Dependencies RFD.

        It allows to load a matrix from a csv file, to split the data frame and build a difference matrix according to a
        given division in RHS and LHS for attributes.

        Args:
            path (str): path to a csv file containing a set of tuples.

        Attributes:
            path (str): the path where the CSV is stored.
            df (pandas.core.frame.DataFrame): data frame where the set of tuples will be stored.
            distance_df (pandas.core.frame.DataFrame): data frame containing distance matrix for each row
            synset_dic (dict): WordNet synset dictionary of the searched lemmas
            semantic_diff_dic dict): dictionary of the inverse path similarities computed
            datetime (Boolean or list): try to parse given columns indexes as pandas datetime
            sep (str): csv separator
            missing (str): string to be parse as missing value
            header (int or list): Row indexes to use as the column names
            index_col (int): column index to use as the row label
        """
    cdef object path
    cdef object df
    cdef object distance_df
    cdef cython.bint semantic
    cdef object sysnset_dic
    cdef object semantic_diff_dic
    cdef object datetime
    cdef object sep
    cdef object missing
    cdef object first_col_header

    def __init__(self, path, semantic=True, datetime=False, sep=';', missing='?', first_col_header=0, index_col=False):
        self.path = path
        self.df = None
        self.distance_df = None
        self.semantic = semantic
        self.sysnset_dic = {}
        self.semantic_diff_dic = {}
        self.datetime = datetime
        self.sep = sep
        self.missing = missing
        self.first_col_header = first_col_header
        self.__load(index_col=index_col)
        self.distance_df = self.__distance_matrix()
        self.df = None

    cdef object __load(self, index_col=False):
        """Load a pandas data frame from a csv file stored in the path df.
        """
        self.df = pnd.read_csv(self.path, sep=self.sep, header=self.first_col_header, index_col=index_col, engine='c',
                               na_values=['', self.missing], parse_dates=self.datetime)
        return self.df

    def split_sides(self, hss : dict) -> pnd.DataFrame:
        """Split the data frame according to the given RHS and LHS division.

            The Relaxed Functional Dependencies is in the form: lhs -> rhs

            Args:
                lhs (list): list of indices of attributes on the left hand side.
                rhs (int): right hand side attribute's index.
            Returns:
                dict: a dictionary containing two keys: 'lhs' containing the projection of the set of tuples on the lhs'
                attributes and 'rhs' containing the the projection of the set of tuples on the rhs' attributes.
        """
        df_to_split = self.distance_df
        cols = df_to_split.columns.tolist()
        lhs_keys = [cols[key] for key in hss['lhs']]
        rhs_keys = [cols[key] for key in hss['rhs']]
        ncols = rhs_keys + lhs_keys
        df_to_split = df_to_split[ncols].rename(columns={str(rhs_keys[0]): 'RHS'})
        return df_to_split

    cdef object __distance_matrix(self):
        """Build the distance matrix according to the given division in RHS and LHS in hss.

            Args:
                hss (dict): a dictionary representing the division in RHS and LHS
            Returns:
                pandas.DataFrame: a DataFrame containing, for each pair of rows, the distance on each attribute sorted
                according to RHS' distance value
        """
        cdef unsigned int n_row = self.df.shape[0]
        cdef unsigned int max_couples = int(n_row * (n_row - 1) / 2)
        cdef unsigned int k = 0
        cdef unsigned int i
        cdef unsigned int j

        ops = self.__map_types__()
        self.distance_df = pnd.DataFrame(columns=self.df.columns.tolist(),
                                         index=list(range(0, max_couples)), dtype=float)
        for i in range(0, n_row):
            df_i = self.df.iloc[i]
            for j in range(i+1, n_row):  # iterate on each pair of rows
                df_j = self.df.iloc[j]
                row = [np.absolute(fn(a, b))
                       for a, b, fn
                       in list(zip(*[np.array(df_i), np.array(df_j), ops]))]
                try:
                    self.__insert_in_df(k, row)
                except IndexError as iex:
                    print("Index ", k, " out of bound")
                    print(iex)
                k += 1
        # assign row names for the data frame
        self.distance_df = self.distance_df.drop_duplicates()
        return self.distance_df

    cdef void __insert_in_df(self, unsigned int k, object row):
        self.distance_df.iloc[k] = row

    cdef object __map_types__(self):
        """
        Perform a mapping for the dtypes of both RHS and LHS DataFrames with the corrisponding subtraction function.
        :param hss: dict of list of the RHS and LHS indexes
        :returns: an array of lists of subtraction functions [(RHS subtraction functions), (LHS subtraction functions)]
        """
        cdef unsigned int i
        if self.semantic:
            # iterate over columns
            types = np.array([self.__semantic_diff_criteria__(col_label, col)
                               for i, (col_label, col) in enumerate(self.df.iteritems())])
        else:
            types = np.array([self.__diff_criteria__(col_label, col)
                                for i, (col_label, col) in enumerate(self.df.iteritems())])
        return types.tolist()

    cdef object __diff_criteria__(self, str col_label, object col):
        """
        Takes in input a DataFrame and its label and returns the subtraction function.
        :param col_label: column name
        :param col: Dataframe
        :returns: subtraction function
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        if col.dtype in numeric:
            return __subnum__
        elif col.dtype in string:
            return __edit_dist__
        elif np.issubdtype(col.dtype, np.datetime64):
            return __date_diff__
        else:
            raise Exception("Unrecognized dtype")

    cdef object __semantic_diff_criteria__(self, str col_label, object col):
        """
        Takes in input a DataFrame and its label and returns the subtraction
        function taking into account the semantic difference where is possible.
        :param col_label: column name
        :param col: Dataframe
        :returns: subtraction function
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        if col.dtype in numeric:
            return __subnum__
        elif col.dtype in string:
            for val in col:
                if isinstance(val, float) and np.isnan(val):
                    continue
                if val not in self.sysnset_dic:
                    s = wn.synsets(val)
                    if len(s) > 0:
                        self.sysnset_dic[val] = s[0]  # NOTE terms added from later dropped columns are kept in dict
                    else:
                        return __edit_dist__
            return self.semantic_diff
        elif np.issubdtype(col.dtype, np.datetime64):
            return __date_diff__
        else:
            raise Exception("Unrecognized dtype")

    cpdef float semantic_diff(self, object a, object b):
        """
        Computes the semantic difference as (1 - path_similarity) and store the result in semantic_diff_dic
        :param a: first term
        :param b: comparation term
        :return: semantic difference
        """
        if isinstance(a, float) and np.isnan(a):
            return np.inf
        if isinstance(b, float) and np.isnan(b):
            return np.inf
        if a == b:
            return 0
        if (a, b) in self.semantic_diff_dic:
            return self.semantic_diff_dic[(a, b)]
        elif (b, a) in self.semantic_diff_dic:
            return self.semantic_diff_dic[(b, a)]
        else:
            t = wn.path_similarity(self.sysnset_dic[a], self.sysnset_dic[b])
            self.semantic_diff_dic[(a, b)] = 1 - t
            self.semantic_diff_dic[(b, a)] = 1 - t
            return 1 - t


cdef float __date_diff__(a: pnd.tslib.Timestamp, b: pnd.tslib.Timestamp):
    """
    Computes the aritmetic difference on given dates
    :param a: date in string
    :param b: date in string
    :return: difference in days
    """
    if a is pnd.NaT:
        return np.inf
    if b is pnd.NaT:
        return np.inf
    delta = a-b
    return int(delta / np.timedelta64(1, 'D'))


cdef float __edit_dist__(object a, object b):
    """
    Computes the Levenshtein distance between two terms
    :param a: first term
    :param b: second term
    :return: Levenshtein distance
    """
    if isinstance(a, float) and np.isnan(a):
        return np.inf
    if isinstance(b, float) and np.isnan(b):
        return np.inf
    if a == b:
        return 0
    return lw.lev_distance(str(a), str(b))


cdef float __subnum__(float a, float b):
    """
    Computes the aritmetic difference on given floats
    :param a: first number
    :param b: subtracting number
    :return: difference in float
    """
    if isinstance(a, float) and np.isnan(a):
        return np.inf
    if isinstance(b, float) and np.isnan(b):
        return np.inf
    return a - b
