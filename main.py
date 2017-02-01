from dominance.dominance_tools import RFDDiscovery
from loader.distance_mtr import DiffMatrix
import utils.utils as ut

hss = {"lhs": [1, 2, 3], "rhs": [0]}

if __name__ == "__main__":
    with ut.timeit_context("Whole time"):
        with ut.timeit_context("Distance time"):
            diff_mtx = DiffMatrix("resources/dataset.csv", {})
            diff_mtx.load()
            dist_mtx = diff_mtx.distance_matrix(hss)
            diff_mtx = None     # for free unused memory
        with ut.timeit_context("RFD Discover time"):
            nd = RFDDiscovery(dist_mtx)
            print(nd.get_rfds(nd.standard_algorithm, hss))
