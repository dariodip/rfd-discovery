import sys
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery
from contextlib import contextmanager
import time
import json


def main(csv_file, params):
    diff_mtx = DiffMatrix(csv_file,
                          sep=params['separator'],
                          first_col_header=params['header'],
                          semantic=params['semantic'],
                          missing=params['missing'],
                          datetime=params['datetime'])
    cols_count = ut.get_cols_count(csv_file, params['separator'])
    hss = extract_hss(cols_count, params['lhs'], params['rhs'])
    result = {}
    for combination in hss:
        comb_dist_mtx = diff_mtx.split_sides(combination)
        nd = RFDDiscovery(comb_dist_mtx)
        result[json.dumps(combination)] = nd.get_rfds(nd.standard_algorithm, combination).to_csv(sep=params['separator'])
    return result


def param_to_dict(p):
    dic = {}
    for k in p:
        if k == 'datetime':
            if not p.get(k):
                dic[k] = False
            else:
                dic[k] = list(map(lambda x: int(x), p.get(k).split(',')))
        elif k == 'rhs' or k == 'lhs':
            if not p.get(k):
                dic[k] = []
            else:
                dic[k] = list(map(lambda x : int(x), p.get(k).split(',')))
        elif k == 'header':
            if p.get(k) == 'true':
                dic[k] = 0
            else:
                dic[k] = False
        elif k == 'semantic' :
            if not p.get(k) or p.get(k) == 'false':
                dic[k] = False
            else:
                dic[k] = True
        else:
            dic[k] = p.get(k)
    return dic


def extract_hss(cols_count, lhs, rhs):
    # You cannot have len(rhs) > 1, don't check it
    if rhs == [] and lhs == []:  # each combination case
        hss = ut.get_hs_combination(cols_count)
    elif rhs == [] and not lhs == []:  # error case
        print("You have to specify at least one RHS attribute")
        sys.exit(-1)
    elif not rhs == [] and lhs == []:  # only rhs specified case
        cols_index = list(range(cols_count))
        if not rhs[0] in cols_index:
            print("RHS index is out of bound. Specify a valid value")
            sys.exit(-1)
        hss = list()
        hss.append({'rhs': rhs, 'lhs': cols_index[:rhs[0]] + cols_index[rhs[0] + 1:]})
    else:
        hss = list()
        hss.append({'rhs': rhs, 'lhs': lhs})
    return hss


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    return '[{}] finished in {:.2f} ms'.format(name, elapsedTime * 1000)