import os
import sys
sys.path.append(os.path.abspath(".."))
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery
import pandas as pnd
import time
import json

"""
This module contain the code used for receive the user's parameters and execute the algorithm.
"""

def main(csv_file, post_metadata):
    """
    Given a valid CSV file's path and a series of parameters given by the user via the web gui, execute the algorithm on
    the given input. If some of the parameters are not valid, the method return an error string message.
    Return the output of the standard_algorithm in a dict where each element is the output of the algorithm
    for each combination given as input and with the combination itself as a key in JSON format.
    :param csv_file: valid path to a CSV file
    :type csv_file: str
    :param post_metadata: dict containing the user's parameters
    :type post_metadata: werkzeug.datastructures.ImmutableMultiDict
    :return: a dict containing the output of each combination or with an error message
    :rtype: dict
    """
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
                labels = diff_mtx.get_labels()
            except Exception as e:
                return {"error":str(e.__doc__)}
                #return {"error":str(traceback.format_exc())}
        cols_count = ut.get_cols_count(csv_file, params['separator'])
        hss = extract_hss(cols_count, params['lhs'], params['rhs'])
        response = {'mtxtime': "{:.2f}".format(mtxtime.interval), 'result': {}, 'timing': []}
        for combination in hss:
            with Timer() as c:
                try:
                    comb_dist_mtx = diff_mtx.split_sides(combination)
                    nd = RFDDiscovery(comb_dist_mtx)
                    r = nd.get_rfds(nd.standard_algorithm, combination)
                    rhs = r[[0]]
                    lhs = r.drop([r.columns[0]], axis=1)
                    result_df = pnd.concat([lhs, rhs], axis=1)
                    response['result'][json.dumps(name_combination(labels, combination))] = result_df.to_csv(sep=params['separator'])
                except Exception as e:
                    return {"error": str(e.__doc__)}
            response['timing'].append("{:.2f}".format(c.interval))
    response['total'] = "{:.2f}".format(total.interval)
    return response

def name_combination(names, comb):
    return {'lhs': list(names[comb['lhs']]), 'rhs': list(names[comb['rhs']])}

def param_to_dict(p):
    """
    Given the user's parameters in a flask ImmutableMultiDict, covert it in a simple dict
    :param p: ImmutableMultiDict containing the user's parameter
    :type p: werkzeug.datastructures.ImmutableMultiDict
    :return: dictionary containing the user's parameter
    :rtype: dict
    """
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
    """
    Given the lhs and rhs from the command line parameters, and the column's number of the dataset,
    it creates various combinations of rhs and lhs according to the format of this two parameters.
    If the format of this two parameters is not accordant with the possible combination on rhs and lhs in the
    command line arguments described by the README, the program will print an error message and it will end.
    The program return a list of dict, where each dict contains the indexes of the attributes on the lhs with the key
    'lhs' and the index of the attribute on the rhs with the key 'rhs'.
    :param cols_count: the column's number
    :type cols_count: int
    :param lhs: list of a valid columns' indexes containing the dataset's attributes positioned in the lhs
    :type lhs: list
    :param rhs: list of a valid column's index containing the dataset's attribute positioned in the rhs
    :type rhs: list
    :return: one or more combination of attribute in the rhs and lhs
    :rtype: list
    """
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
    """
    Measure the time of the block of code included into a with statement
    :return: Time object
    """
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start