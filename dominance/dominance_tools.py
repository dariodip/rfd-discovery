from loader.distance_mtr import DiffMatrix
import pandas as pnd


def get_dominance(path: str):
    diff_mtx = DiffMatrix(path)
    diff_mtx.load()
    distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides([1,2,3], [0]))
    naive_dominance(distance_matrix, [1, 2, 3], [0])

def naive_dominance(d_mtx: pnd.DataFrame, lhs: list, rhs: list):
    h_distance_row = d_mtx.loc[d_mtx.index[rhs]]
    print(h_distance_row)


if __name__ == "main":
    get_dominance("../resources/dataset.csv")