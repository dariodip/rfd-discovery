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

"""Module containing the code used to create and manage the distance matrix"""

cdef class DiffMatrix:
    """
    Class used to build the difference matrix used to find Relaxed Functional Dependencies RFD from a dataset.
    It takes a path of a CSV file where the dataset is saved, loaded them and build a difference matrix,
    a matrix where each row is the difference between two rows from the starting dataset. You can specify
    some parameters if you want for example to specify some parameters about the CSV, like the data separator or the value used to notify a missing value, or
    if you want to use the semantic difference or if you want some column will be interpreted as a date.
    After the distance matrix is calculated, you can choose any splitting in lhs and rhs you want but the distance
    matrix will be calculated only one times.
    It use the lexical database WordNet to calculate the semantic difference between two string a and b. You can
    disable this functionality by setting the instance variable semantic, in that case the class will use the edit
    distance to calculate the distance between two string. When it calculate the difference between two attribute's
    value, if at least one of them is NaN(Not a Number) or NaT(Not a Timestamp), the distance between this values will
    be the value infinity.
    After the distance matrix is calculated, the memory area containing the dataset will be freed in order to save memory space.
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
    cdef object labels


    def __init__(self, path, semantic=True, datetime=False, sep=';', missing='?', first_col_header=0, index_col=False):
        """
        Load the dataset and build the distance matrix.
        For any dataset's column, it choose the property distance function according to the column's data type.
        :param path: path of a CSV file where the dataset is stored.
        :type path: str
        :param semantic: denote if we want to use the semantic difference. Its value is True if we want to use the semantic difference. Default behavior is as if set to False if no values is passed.
        :type semantic: bool
        :param datetime: denote if we want that some column in the dataset must be interpreted as a date. To indicate that columns, whe use a list of integers indexes, where each index represent a column of the dataset containing the dates. False value indicate that we do not have any column with date.  Default behavior is as if set to False if no value is passed.
        :type datetime: bool or list of int
        :param sep: the separator used to separate the values in the CSV file. Default behavior is as if set to ';' if no value is passed.
        :type sep: str
        :param missing: the character used to notify a missing value. Default behavior is as if set to '?' if no value is passed.
        :type missing: str
        :param first_col_header: row number(s) to use as column names, and the start of the data. Default behavior is as if set to 0 if no value is passed.
        :type first_col_header: int or list of int
        :param index_col: the column which contains the primary key of the dataset. Specifying it, this will not calculate as distance.
        :type index_col: int
        """
        self.path = path
        """Absolute or relative path where the dataset is stored"""
        self.df = None
        """Pandas data frame containing the dataset"""
        self.distance_df = None
        """Pandas data frame containing the distance matrix, set to None after the distance matrix is calculated"""
        self.semantic = semantic
        """Boolean value, True if we want to use the semantic difference from WordNet"""
        self.sysnset_dic = {}
        """Dict where each is (str, value) where str is a word and value is the more common value for this term"""
        self.semantic_diff_dic = {}
        """Dict where each couple (a, b) contain the semantic difference between a and b"""
        self.datetime = datetime
        """Boolean value, False if we do not have columns with date or a list of column's indexes instead"""
        self.sep = sep
        """Separator used in the CSV file to separate values"""
        self.missing = missing
        """Value used to notify missing value"""
        self.first_col_header = first_col_header
        """Row's index of the row's key in the CSV file"""
        self.__load(index_col=index_col)
        self.distance_df = self.__distance_matrix()
        self.df = None

    cdef object __load(self, index_col=False):
        """
        Load in a pandas' data frame the dataset memorized in a csv file located in the path stored in the instance variable path.
        The dataset's path must be valid. All the params about the CSV file specified in the constructor will be used here.
        The dataset will be memorized in the instance variable df.
        An empty string is interpreted as a missing value.
        :param index_col: the column which contains the primary key of the dataset. Specifying it, this will not calculate as distance. Default behavior is as if set to False if no values is passed.
        :type index_col: int or bool
        :return data frame containing the loaded dataset
        :rtype pandas.core.frame.DataFrame
        """
        self.df = pnd.read_csv(self.path, sep=self.sep, header=self.first_col_header, index_col=index_col, engine='c',
                               na_values=['', self.missing], parse_dates=self.datetime)
        self.labels = self.df.columns.values
        return self.df

    def split_sides(self, hss : dict) -> pnd.DataFrame:
        """
        Split the distance matrix according to the given RHS and LHS division. The lhs is represented with an integers indexes
        where each integer represent a valid column of the data frame. The rhs must be instead represented with an only one integer index.
        It returns a data frame containing only the column in the lhs and rhs, with the rhs' column renamed with the name 'RHS'
        :param hss: the given division lhs -> rhs
        :type hss: dict
        :return: the data frame containing the given division
        :rtype: pandas.core.frame.DataFrame
        """
        df_to_split = self.distance_df
        cols = df_to_split.columns.tolist()
        lhs_keys = [cols[key] for key in hss['lhs']]
        rhs_keys = [cols[key] for key in hss['rhs']]
        ncols = rhs_keys + lhs_keys
        df_to_split = df_to_split[ncols].rename(columns={str(rhs_keys[0]): 'RHS'})
        return df_to_split

    cdef object __distance_matrix(self):
        """
        Build the distance matrix from the given dataset. For each attribute, it will be used a difference
        function according to the attribute's type.
        In the distance matrix, every set of rows containing the same values will be collapsed in only one row.
        The distance matrix will be memorized in the instance variable distance_df
        :return the distance matrix
        :rtype: pandas.DataFrame
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
                row = [np.absolute(fn(a, b)) for a, b, fn in list(zip(*[np.array(df_i), np.array(df_j), ops]))]
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
        """
        Insert a new row in the distance matrix.
        :param k: the row's position in the distance matrix
        :type k: int
        :param row: row to add
        :type row: list
        """
        self.distance_df.iloc[k] = row

    cdef object __map_types__(self):
        """
        For each attribute, find a distance function according to its type. According to the value
        of the instance variable semantic, the function will use a appropriate mapping function.
        :returns: a list containing one distance function for each data frame's column
        :rtype: list
        """
        if self.semantic:
            # iterate over columns
            types = np.array([self.__semantic_diff_criteria__(col)
                               for col_label, col in self.df.iteritems()])
        else:
            types = np.array([self.__diff_criteria__(col)
                                for col_label, col in self.df.iteritems()])
        return types.tolist()

    cdef object __diff_criteria__(self, object col):
        """
        Given an attribute's column, check its type and return the appropriate distance function.
        The difference between __semantic_diff_criteria__ and this method is that this method will use the
        edit distance for strings.
        If the type of a function is an object, it will use the edit distance for this attribute.
        If the type of an attribute is not valid, the method will raise an exception.
        :param col_label: the column's label
        :type col_label: str
        :param col: the attribute's values
        :type col: pandas.core.series.Series
        :return: a distance function
        :rtype: method
        :raise: Exception, when the attribute's type is not valid
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

    cdef object __semantic_diff_criteria__(self, object col):
        """
        Given an attribute's column, check its type and return the appropriate distance function.
        The difference between __diff_criteria__ and this method is that this method will use the
        semantic difference for strings and the edit distance as fallback when the Wordnet lookup fails.
        If the type of a function is an object, it will use the semantic difference for this attribute.
        If the type of an attribute is not valid, the method will raise an exception.
        :param col: the attribute's values
        :type col: pandas.core.series.Series
        :return: a distance function
        :rtype: method
        :raise: Exception, when the attribute's type is not valid
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
        Computes the semantic difference, as 1 - path similarity, between two string.
        After calculated, the semantic difference will be stored in the dictionary semantic_diff_dic so when this distance is again requested it will
        not be calculated a second time.
        The path similarity is calculated by using WordNet.
        If one of the two parameter is NaN, the distance returned will be infinity.
        If both are NaN, the distance returned will be 0.
        :param a: first term
        :type a: str or float for NaN value
        :param b: second term
        :type b: str or float for NaN value
        :return: the semantic difference between a and b
        :rtype float
        """
        if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
            return 0
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

    cpdef object get_labels(self):
        return self.labels

cdef float __date_diff__(a: pnd.tslib.Timestamp, b: pnd.tslib.Timestamp):
    """
    Computes the aritmetic difference on given dates a and b.
    If one of the two parameter is NaT, the distance returned will be infinity.
    If both are NaT, the distance returned will be 0.
    :param a: first date
    :type a: pandas.tslib.Timestamp or float for NaN value
    :param b: comparison date
    :type b: pandas.tslib.Timestamp or float for NaN value
    :return: difference in days
    :rtype float
    """
    if (a is pnd.NaT) and (b is pnd.NaT):
        return 0
    if a is pnd.NaT:
        return np.inf
    if b is pnd.NaT:
        return np.inf
    delta = a-b
    return int(delta / np.timedelta64(1, 'D'))


cdef float __edit_dist__(object a, object b):
    """
    Computes the Levenshtein distance between two strings a and b.
    If one of the two parameter is NaN, the distance returned will be infinity.
    If both are NaN, the distance returned will be 0.
    :param a: first term
    :type a: str or float for NaN value
    :param b: second term
    :type b: str or float for NaN value
    :return: the edit distance between a and b
    :rtype float
    """
    if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
        return 0
    if isinstance(a, float) and np.isnan(a):
        return np.inf
    if isinstance(b, float) and np.isnan(b):
        return np.inf
    if a == b:
        return 0
    return lw.lev_distance(str(a), str(b))


cdef float __subnum__(float a, float b):
    """
    Computes the aritmetic difference on given floats a and b.
    If one of the two parameter is NaN, the distance returned will be infinity.
    If both are NaN, the distance returned will be 0.
    :param a: first term
    :type a: float
    :param b: second term
    :type b: float
    :return: difference in float
    :rtype float
    """
    if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
        return 0
    if isinstance(a, float) and np.isnan(a):
        return np.inf
    if isinstance(b, float) and np.isnan(b):
        return np.inf
    return a - b


