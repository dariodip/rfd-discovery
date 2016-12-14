import pandas as pnd


class DiffMatrix:

    def __init__(self, path):
        self.path = path
        self.df = None

    def load(self):
        self.df = pnd.read_csv(self.path, sep=';', header=0, index_col=0)

    def split_sides(self, lhs: list, rhs: int) -> dict:
        lhskeys = [self.df.keys()[key] for key in lhs]
        rhskeys = [self.df.keys()[key] for key in rhs]
        return({
            'lhs': self.df[lhskeys],
            'rhs': self.df[rhskeys]
        })

    def distance_matrix(self, split_df: dict):
        pass
