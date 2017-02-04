import sys
import getopt
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery


usage = 'use python3 main.py -c <csv-file> -r [rhs_index] -l [lhs_indexes] -s [sep] -h [header] (-w)'


def main(args):
    c_sep, csv_file, has_header, semantic = extract_args(args)

    if hss is None:
        print(usage)
    if isinstance(hss, list):
        with ut.timeit_context("Whole time"):
            with ut.timeit_context("Distance time"):
                diff_mtx = DiffMatrix(csv_file, sep=c_sep, first_col_header=has_header, semantic=semantic)
            for combination in hss:
                comb_dist_mtx = diff_mtx.split_sides(combination)
                with ut.timeit_context("RFD Discover time for {}".format(str(combination))):
                    nd = RFDDiscovery(comb_dist_mtx)
                    print(nd.get_rfds(nd.standard_algorithm, combination))


def extract_args(args):
    # extraction
    try:
        csv_file, lhs, rhs, c_sep, has_header, semantic = '', [], [], '', None, False
        opts, args = getopt.getopt(args, "c:r:l:s:h:w:m:d")
        for opt, arg in opts:
            if opt == '-c':
                csv_file = arg
            elif opt == '-r':
                rhs = [int(arg)]
                if len(rhs) > 1:
                    print("You can specify at most 1 RHS attribute")
                    sys.exit(-1)
            elif opt == '-l':
                lhs = [int(_) for _ in arg.split(',')]
            elif opt == '-s':
                c_sep = arg
            elif opt == '-h':
                has_header = int(arg)
            elif opt == '-w':
                semantic = True
            elif opt == '-m':
                raise NotImplementedError("To implement")
                # TODO
            elif opt == '-d':
                raise NotImplementedError("To implement")
                # TODO
    except TypeError as t_err:
        print("Error while trying to convert a string to numeric: {}".format(str(t_err)))
        sys.exit(-1)
    except Exception as ex:
        print("Error while trying to extract arguments: {}".format(str(ex)))
        sys.exit(-1)
    # understanding
    try:
        c_sep, has_header = extract_sep_n_header(c_sep, csv_file, has_header)
        cols_count = ut.get_cols_count(csv_file, c_sep)
        global hss
        hss = extract_hss(cols_count, lhs, rhs)
    except Exception as ex:
        print("Error while trying to understand arguments: {}".format(str(ex)))
        sys.exit(-1)
    return c_sep, csv_file, has_header, semantic


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
        #hss['rhs'] = rhs
        #hss['lhs'] = cols_index[:rhs[0]] + cols_index[rhs[0] + 1:]
    else:
        hss = list()
        hss.append({'rhs': rhs, 'lhs': lhs})
    return hss


def extract_sep_n_header(c_sep, csv_file, has_header):
    if c_sep == '' and has_header is None:
        c_sep, has_header = ut.check_sep_n_header(csv_file)
    elif c_sep != '' and has_header is None:
        has_header = ut.check_sep_n_header(csv_file)[1]
    elif c_sep == '' and has_header is not None:
        c_sep = ut.check_sep_n_header(csv_file)[0]
    return c_sep, has_header


if __name__ == "__main__":
    main(sys.argv[1:])