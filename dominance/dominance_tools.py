from loader.distance_mtr import DiffMatrix
import pandas as pnd


def get_dominance(path: str):
    diff_mtx = DiffMatrix(path)
    diff_mtx.load()
    distance_matrix = diff_mtx.distance_matrix(diff_mtx.split_sides([1, 2, 3], [0]))
    naive_dominance(distance_matrix, [1, 2, 3], [0])


def naive_dominance(d_mtx: pnd.DataFrame, lhs: list, rhs: list):
    list_of_dominance_set = list()
    current_distance = d_mtx.iloc[rhs][d_mtx.keys()[0]][0]  # max distance
    previous_distance = current_distance + 1  # it does not exists
    for col in d_mtx:
        current_distance = d_mtx.iloc[rhs][col][0]
        print(current_distance)
        print(d_mtx[col][lhs].tolist())


if __name__ == "__main__":
    get_dominance("../resources/dataset.csv")