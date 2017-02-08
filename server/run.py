import sys
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery
from contextlib import contextmanager
import time
import json
import traceback


def main(csv_file, post_metadata):
    with Timer() as total:
        params = param_to_dict(post_metadata)
        args = {'sep': params['separator'],
            'semantic': params['semantic'],
            'missing': params['missing'],
            'datetime': params['datetime']
            }
        if 'header' in params:
            args['first_col_header'] = params['header']
        with Timer() as mtxtime:
            try:
                diff_mtx = DiffMatrix(csv_file, **args)
            except Exception as e:
                return {"error":str(e.__doc__)}
                #return {"error":str(traceback.format_exc())}
        cols_count = ut.get_cols_count(csv_file, params['separator'])
        hss = extract_hss(cols_count, params['lhs'], params['rhs'])
        response = {'mtxtime': "{:.2f}".format(mtxtime.interval), 'result': {}, 'timing': []}
        for combination in hss:
            with Timer() as c:
                comb_dist_mtx = diff_mtx.split_sides(combination)
                nd = RFDDiscovery(comb_dist_mtx)
                response['result'][json.dumps(combination)] = nd.get_rfds(nd.standard_algorithm, combination).to_csv(sep=params['separator'])
            response['timing'].append("{:.2f}".format(c.interval))
    response['total'] = "{:.2f}".format(total.interval)
    return response


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
        elif k == 'semantic':
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


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start