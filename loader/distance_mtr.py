import pandas as pnd
import numpy as np
import operator as op
import nltk
from nltk.corpus import wordnet as wn
from utils.utils import deprecated

pnd.set_option('display.width', 320)


class DiffMatrix:
    """Class used to build the the difference matrix respect to a Relaxed Functional Dependencies RFD.

        It allows to load a matrix from a csv file, to split the data frame and build a difference matrix according to a
        given division in RHS and LHS for attributes.

        Args:
            path (str): path to a csv file containing a set of tuples.

        Attributes:
            path (str): the path where the CSV is stored.
            df (pandas.core.frame.DataFrame): data frame where the set of tuples will be stored.
            distance_df (pandas.core.frame.DataFrame): data frame containing distance matrix for each row
            synset_dic WordNet synset dictionary of the searched lemmas
            semantic_diff_dic dictionary of the inverse path similarity computed
        """
    def __init__(self, path, semantic=False, datetime=False, sep=';', missing='?', first_col_header=0, index_col=False):
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
        self.distance_df = self.distance_matrix()
        self.df = None

    def __load(self, index_col=False) -> pnd.DataFrame:
        """Load a pandas data frame from a csv file stored in the path df.
        """
        self.df = pnd.read_csv(self.path, sep=self.sep, header=self.first_col_header, index_col=index_col, engine='c',
                               na_values=['', self.missing], parse_dates=self.datetime)
        self.df = self.df.replace(np.nan, np.inf)
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

    def distance_matrix(self) -> pnd.DataFrame:
        """Build the distance matrix according to the given division in RHS and LHS in hss.

            Args:
                hss (dict): a dictionary representing the division in RHS and LHS
            Returns:
                pandas.DataFrame: a DataFrame containing, for each pair of rows, the distance on each attribute sorted
                according to RHS' distance value
            Todo:
                * algorithm for an efficient build of the difference matrix"""

        ops = self.__map_types__()
        shape_0 = self.df.shape[0]
        max_couples = int(shape_0 * (shape_0 - 1) / 2)
        self.distance_df = pnd.DataFrame(columns=self.df.columns.tolist(),
                                         index=list(range(0, max_couples)), dtype=float)
        k = 0
        n_row = self.df.shape[0]
        for i in range(0, n_row):
            for j in range(i+1, n_row):  # iterate on each pair of rows
                df_i = self.df.iloc[i]
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
        return self.distance_df

    def __insert_in_df(self, k, row):
        self.distance_df.iloc[k] = row

    def __map_types__(self) -> list:
        """
        Perform a mapping for the dtypes of both RHS and LHS DataFrames with the corrisponding subtraction function.
        :param hss: dict of list of the RHS and LHS indexes
        :returns: an array of lists of subtraction functions [(RHS subtraction functions), (LHS subtraction functions)]
        """
        if self.semantic:
            # iterate over columns
            types =  np.array([self.__semantic_diff_criteria__(col_label, col)
                               for i, (col_label, col) in enumerate(self.df.iteritems())])
        else:
            types =  np.array([self.__diff_criteria__(col_label, col)
                                for i, (col_label, col) in enumerate(self.df.iteritems())])
        return types.tolist()

    def __diff_criteria__(self, col_label: str, col: pnd.DataFrame):
        """
        Takes in input a DataFrame and its label and returns the subtraction function.
        :param col_label: column name
        :param col: Dataframe
        :returns: subtraction function
        TODO: maybe handle unicode strings (dtype:basestring)
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        datetime = {np.dtype('<M8[ns]')} # TODO check
        # TODO all numeric: dtype = np.number
        if col.dtype in numeric:
            return op.sub
        elif col.dtype in string:
            return self.__edit_dist__
        elif col.dtype in datetime:
            return self.__date_diff__
        else:
            raise Exception("Unrecognized dtype")

    def __semantic_diff_criteria__(self, col_label: str, col: pnd.DataFrame):
        """
        Takes in input a DataFrame and its label and returns the subtraction
        function taking into account the semantic difference where is possible.
        :param col_label: column name
        :param col: Dataframe
        :returns: subtraction function
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        datetime = {np.datetime64(),pnd.tslib.Timestamp,np.dtype('<M8[ns]')}

        if col.dtype in numeric:
            return op.sub
        elif col.dtype in datetime:
            return self.__date_diff__
        elif col.dtype in string:
            for val in col:
                if val not in self.sysnset_dic:
                    s = wn.synsets(val)
                    if len(s) > 0:
                        self.sysnset_dic[val] = s[0]  # NOTE terms added from later dropped columns are kept in dict
                    else:
                        return self.__edit_dist__
            return self.semantic_diff
        else:
            raise Exception("Unrecognized dtype")

    def semantic_diff(self, a: str, b: str) -> float:
        """
        Computes the semantic difference as (1 - path_similarity) and store the result in semantic_diff_dic
        :param a: first term
        :param b: comparation term
        :return: semantic difference
        """
        if a == np.inf or b == np.inf:
            return np.inf
        if (a, b) in self.semantic_diff_dic:
            return self.semantic_diff_dic[(a, b)]
        else:
            t = wn.path_similarity(self.sysnset_dic[a], self.sysnset_dic[b])
            self.semantic_diff_dic[(a, b)] = 1 - t
            return 1 - t

    @staticmethod
    @deprecated
    def __row_names__(rhs: pnd.DataFrame, lhs: pnd.DataFrame) -> dict:
        """
        Place 'r' or 'l' before name data frame's keys, in order to discriminate RHS attributes and LHS attributes
        :param rhs: a pandas' DataFrame containing RHS attributes
        :param lhs: a pandas' DataFrame containing LHS attributes
        :return: a dict having 'r_keys' and 'l_keys' as keys, respectively for RHS' keys and LHS' keys, with
        'r_' and 'l_' as prefix
        """
        r_keys = ["r_" + str(rk) for rk in rhs.keys()]
        l_keys = ["l_" + str(lk) for lk in lhs.keys()]
        return {"r_keys": r_keys, "l_keys": l_keys}

    @staticmethod
    def __date_diff__(a: pnd.tslib.Timestamp, b: pnd.tslib.Timestamp) -> float:
        """
        Computes the aritmetic difference on given dates
        :param a: date in string
        :param b: date in string
        :return: difference in days
        """
        delta = a-b
        return int(delta / np.timedelta64(1, 'D'))
        # try:
        #     return (parser.parse(a)-parser.parse(b)).days
        # except Exception as ex:
        #     print("error parsing date: ", str(ex))

    @staticmethod
    def __edit_dist__(a: str, b: str) -> float:
        """
        Computes the Levenshtein distance between two terms
        :param a: first term
        :param b: second term
        :return: Levenshtein distance
        """
        if a == np.inf or b == np.inf:
            return np.inf
        return nltk.edit_distance(a, b)

        #   WILD IDEAS
        #   preprocessare la matrice per vedere se wordnet conosce le parole
        #   valutare: scartare row quando non definito
        #   eseguire l'algoritmo su ciò che wordnet conosce e poi generare una func di interpolazione per i
        # termini sconosciuti (e.g. edit distance sul termine più vicino)
