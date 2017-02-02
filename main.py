import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery

hss = {"lhs": [1, 2, 3], "rhs": [0]}

if __name__ == "__main__":

    csv_file = "resources/dataset.csv"
    c_sep, has_header = ut.check_sep_n_header(csv_file)

    with ut.timeit_context("Whole time"):
        with ut.timeit_context("Distance time"):
            diff_mtx = DiffMatrix(csv_file, {}, sep=c_sep, first_col_header=has_header)
            diff_mtx.load()
            dist_mtx = diff_mtx.distance_matrix(hss)
            diff_mtx = None     # for free unused memory
        with ut.timeit_context("RFD Discover time"):
            nd = RFDDiscovery(dist_mtx)
            print(nd.get_rfds(nd.standard_algorithm, hss))
