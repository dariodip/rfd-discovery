import pandas as pnd


class DiffMatrix:
    """Class used to build the the difference matrix respect to a Relaxed Functional Dependencies RFD.

        It allows to load a matrix from a csv file, to split the dataframe and build a difference matrix according to a given RFD.

        Args:
            path (str): path to a csv file containing a set of tuples.

        Attributes:
            path (str): the path where the dataframe is stored.
            df (pandas.core.frame.DataFrame): dataframe where the sets of tuples will be stored.
        """
    def __init__(self, path):
        self.path = path
        self.df = None

    def load(self):
        """Load a pandas dataframe from a csv file stored in the path df.

        """
        self.df = pnd.read_csv(self.path, sep=';', header=0, index_col=0)

    def split_sides(self, lhs: list, rhs: int) -> dict:
        """Split the dataframe according to the given RFD.

            The Relaxed Functional Dependencies is in the form: lhs -> rhs

            Args:
                lhs (list): list of indices of attributes on the left hand side.
                rhs (int): right hand side attribute's index.
            Returns:
                dict: a dictionary containing two keys: 'lhs' containing the projection of the set of tuples on the lhs' attributes
                and 'rhs' containing the the projection of the set of tuples on the rhs' attributes.
        """
        lhskeys = [self.df.keys()[key] for key in lhs]
        rhskeys = [self.df.keys()[key] for key in rhs]
        return({
            'lhs': self.df[lhskeys],
            'rhs': self.df[rhskeys]
        })

    def distance_matrix(self, split_df: dict):
        """Build the distance matrix according to the given RFD.

            Args:
                split_df (dict): a dictionary representing the RFD returned by split_sides

            Todo:
                * algoritm for an efficient build of the difference matrix"""
        pass
