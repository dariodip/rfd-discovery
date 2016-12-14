import pandas as pnd


class DiffMatrix:

    def __init__(self, path):
        self.path = path
        self.df = None

    def load(self):
        self.df = pnd.read_csv(self.path, sep=';',header=0, index_col=0)

    def diffmatrix(self, lhs: list, rhs: int):
        lhskeys = [key for key in self.df.keys() if key in lhs]
        rhskeys = [key for key in self.df.keys() if key in rhs]
