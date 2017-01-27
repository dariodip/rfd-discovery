import pandas as pnd
import numpy as np
import operator as op
import utils.utils as ut
import nltk
from nltk.corpus import wordnet as wn
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
    def __init__(self, path):
        self.path = path
        self.df = None
        self.distance_df = None
        self.sysnset_dic = {}
        self.semantic_diff_dic = {}

    def load(self) -> pnd.DataFrame:
        """Load a pandas data frame from a csv file stored in the path df.

        """
        self.df = pnd.read_csv(self.path, sep=';', header=0, index_col=0, engine='c')
        return self.df

    def split_sides(self, lhs: list, rhs: list) -> dict:
        """Split the data frame according to the given RHS and LHS division.

            The Relaxed Functional Dependencies is in the form: lhs -> rhs

            Args:
                lhs (list): list of indices of attributes on the left hand side.
                rhs (int): right hand side attribute's index.
            Returns:
                dict: a dictionary containing two keys: 'lhs' containing the projection of the set of tuples on the lhs'
                attributes and 'rhs' containing the the projection of the set of tuples on the rhs' attributes.
        """
        lhs_keys = [self.df.keys()[key] for key in lhs]
        rhs_keys = [self.df.keys()[key] for key in rhs]
        return({
            'lhs': self.df[lhs_keys],
            'rhs': self.df[rhs_keys]
        })

    def distance_matrix(self, hss: dict) -> pnd.DataFrame:
        """Build the distance matrix according to the given division in RHS and LHS in hss.

            Args:
                hss (dict): a dictionary representing the division in RHS and LHS
            Returns:
                pandas.DataFrame: a DataFrame containing, for each pair of rows, the distance on each attribute sorted
                according to RHS' distance value
            Todo:
                * algorithm for an efficient build of the difference matrix"""

        split_df = self.split_sides(hss['lhs'], hss['rhs'])
        lhs = split_df['lhs']
        rhs = split_df['rhs']
        if lhs.shape[0] == rhs.shape[0]:  # check if the num of rows in lhs are equals to the num of rows in rhs
            n_row = lhs.shape[0]
        else:
            raise Exception("Different number of rows in LHS and RHS")

        [ops_rhs, ops_lhs] = self.__preprocess_map_types__(hss)
        #[ops_rhs, ops_lhs] = self.__map_types__(rhs, lhs)
        col_names = self.__row_names__(rhs, lhs)
        col_names = ['RHS'] + col_names['l_keys']  # retrieve row names (RHS and LHS)
        self.distance_df = pnd.DataFrame(columns=col_names)
        for i in range(1, n_row):
            for j in range(i+1, n_row+1):  # iterate on each pair of rows
                index_t = (i, j)
                # absolute difference between rows i and j (both for rhs and lhs) in order to get distance between them
                rhs_dist = [np.absolute(fn(a, b)) for a, b, fn in list(zip(*[np.array(rhs.loc[i]), np.array(rhs.loc[j]), ops_rhs]))]
                lhs_dist = [np.absolute(fn(a, b)) for a, b, fn in list(zip(*[np.array(lhs.loc[i]), np.array(lhs.loc[j]), ops_lhs]))]
                row = np.concatenate([rhs_dist, lhs_dist], axis=0)  # todo check axis 0
                self.distance_df.loc[str(index_t)] = row.tolist()
                # insert a row containing distances into the distance data frame
        # assign row names for the data frame
        self.distance_df.sort_values(by=['RHS'], axis=0, inplace=True, ascending=False)  # sort data frame by r_keys
        return self.distance_df

    def __map_types__(self, rhs: pnd.DataFrame, lhs: pnd.DataFrame) -> list:
        """
        Perform a mapping for the dtypes of both RHS and LHS DataFrames with the corrisponding subtraction function.
        :param rhs: a pandas' DataFrame containing RHS attributes
        :param lhs: a pandas' DataFrame containing LHS attributes
        :returns: an array of lists of subtraction functions [(RHS subtraction functions), (LHS subtraction functions)]
        """
        rhs_types = list(map(self.__diff_criteria__, rhs.dtypes))
        lhs_types = list(map(self.__diff_criteria__, lhs.dtypes))
        return [rhs_types, lhs_types]

    def __preprocess_map_types__(self, hss: dict) -> list:
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float')}
        string = {np.dtype('string_'), np.dtype('object')}

        ops = np.array(list(map(lambda el: op.sub if el in numeric else None, self.df.dtypes))) #init() ops array with op.sub and None
        string_columns = self.df.select_dtypes(include=['object'])
        # iterate over columns
        for i, (col_label, col) in enumerate(string_columns.iteritems()):
            for val in col:
                s = wn.synsets(val)
                if len(s) > 0:
                    if val not in self.sysnset_dic:
                        self.sysnset_dic[val] = s[0]  # NOTE terms added from later dropped columns are kept in dict
                        ops[i] = self.semantic_diff
                else:
                    ops[i] = nltk.edit_distance
                    break
        return [ops[hss['rhs']], ops[hss['lhs']]]

    def semantic_diff(self, a: str, b: str) -> float:
        #return wn.path_similarity(self.terms[a],self.terms[b])
        if (a, b) in self.semantic_diff_dic:
            return self.semantic_diff_dic[(a, b)]
        else:
            t = wn.path_similarity(self.sysnset_dic[a], self.sysnset_dic[b])
            self.semantic_diff_dic[(a, b)] = 1 - t
            return 1 - t

    @staticmethod
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
    def __diff_criteria__(dtype):
        """
        Takes in input a numpy dtype and returns the subtraction function.
        :param dtype: numpy dtype
        :returns: subtraction function
        TODO: maybe handle unicode strings (dtype:basestring)
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float')}
        string = {np.dtype('string_'), np.dtype('object')}
        if dtype in numeric:
            return op.sub
        elif dtype in string:
            return nltk.edit_distance
        else:
            raise Exception("Unrecognized dtype")

        #   WILD IDEAS
        #   preprocessare la matrice per vedere se wordnet conosce le parole
        #   valutare: scartare quando non definito
        #   eseguire l'algoritmo su ciò che wordnet conosce e poi generare una func di interpolazione per i termini sconosciuti (e.g. edit distance sul termine più vicino)

