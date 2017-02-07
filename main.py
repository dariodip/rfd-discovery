import sys
import getopt
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery


def main(args):
    c_sep, csv_file, has_header, semantic, has_dt, missing, index_col = extract_args(args)
    try:
        check_correctness(has_header, has_dt, hss, index_col)
    except getopt.GetoptError as gex:
        usage()
        print(str(gex))
        sys.exit(1)
    except AssertionError as aex:
        usage()
        print(str(aex))
        sys.exit(1)

    if hss is None:
        usage()
    if isinstance(hss, list):
        with ut.timeit_context("Whole time"):
            with ut.timeit_context("Distance time"):
                if isinstance(has_header, int) and not has_header:
                    diff_mtx = DiffMatrix(csv_file,
                                          sep=c_sep,
                                          index_col=index_col,
                                          semantic=semantic,
                                          missing=missing,
                                          datetime=has_dt)
                else:
                    diff_mtx = DiffMatrix(csv_file,
                                      sep=c_sep,
                                      first_col_header=has_header,
                                      semantic=semantic,
                                      index_col=index_col,
                                      missing=missing,
                                      datetime=has_dt)
            for combination in hss:
                comb_dist_mtx = diff_mtx.split_sides(combination)
                with ut.timeit_context("RFD Discover time for {}".format(str(combination))):
                    nd = RFDDiscovery(comb_dist_mtx)
                    print(nd.get_rfds(nd.standard_algorithm, combination))


def extract_args(args):
    # extraction
    try:
        # Default values
        c_sep, has_header, semantic, has_dt, missing, ic = '', None, False, False, None, False
        csv_file = ''
        lhs = []
        rhs = []
        opts, args = getopt.getopt(args, "c:r:l:s:hm:d:vi:", ["semantic", "help"])
        for opt, arg in opts:
            if opt == '-v':
                print("rdf-discovery version 0.0.1")
                sys.exit(0)
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
                has_header = 0
            elif opt == '--semantic':
                semantic = True
            elif opt == '-m':
                missing = arg
            elif opt == '-d':
                has_dt = [int(_) for _ in arg.split(',')]
            elif opt == '-i':
                ic = int(arg)
            elif opt == '--help':
                usage()
                sys.exit(0)
            else:
                assert False, "unhandled option"
    except getopt.GetoptError as getopt_err:
        print(getopt_err)
        usage()
        sys.exit(2)
    except TypeError as t_err:
        print("Error while trying to convert a string to numeric: {}".format(str(t_err)))
        sys.exit(-1)
    except Exception as ex:
        print("Error while trying to extract arguments: {}".format(str(ex)))
        sys.exit(-1)
    # understanding
    try:
        c_sep_ , has_header_ = extract_sep_n_header(c_sep, csv_file, has_header)
        if c_sep == '':
            c_sep = c_sep_
        if has_header is None:
            has_header = has_header_
        cols_count = ut.get_cols_count(csv_file, c_sep)
        global hss
        hss = extract_hss(cols_count, lhs, rhs)
    except Exception as ex:
        print("Error while trying to understand arguments: {}".format(str(ex)))
        sys.exit(-1)
    return c_sep, csv_file, has_header, semantic, has_dt, missing, ic


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


def extract_sep_n_header(c_sep, csv_file, has_header):
    if c_sep == '' and has_header is None:
        c_sep, has_header = ut.check_sep_n_header(csv_file)
    elif c_sep != '' and has_header is None:
        has_header = ut.check_sep_n_header(csv_file)[1]
    elif c_sep == '' and has_header is not None:
        c_sep = ut.check_sep_n_header(csv_file)[0]
    return c_sep, has_header


def check_correctness(has_header, has_dt, hss, index_col):
    max_index = max(hss[0]['rhs'] + hss[0]['lhs'])
    unique_index_count = sum([1 for i in set(hss[0]['rhs'] + hss[0]['lhs'])])
    # check has header
    if index_col:
        if index_col < 0:
            raise AssertionError("Index of a column cannot be less than 0")
        if index_col > max_index and len(hss[0]['lhs']) >= 1:
            raise getopt.GetoptError("Index col is out of bound")
    # check date
    if has_dt is not False:
        if max(has_dt) > max_index and len(hss[0]['lhs']) >= 1:
            raise getopt.GetoptError("Datetime index is out of bound")
    # check non repeated index
    index_count = sum([1 for i in hss[0]['rhs'] + hss[0]['lhs']])
    if index_count != unique_index_count:
        raise AssertionError("Repeated index error")


def usage():
    usage_str = """
    python {} -c <csv-file> [options]

    -c <your-csv>: is the path of the dataset on which you want to discover RFDs;
    Options:

    -v : display version number;
    -s <sep>: the separation char used in your CSV file. If you don't provide this, rfd-discovery tries to infer it for you;
    -h: Indicate that CSV file has the header row. If you don't provide this, rdf-discovery tries to infer it for you.
    -r <rhs_index>: is the column number of the RHS attribute. It must be a valid integer.
            You can avoid to specify it only if you don't specify LHS attributes (we'll find RFDs using each attribute as RHS and the remaining as LHS);
    -l <lhs_index_1, lhs_index_2, ...,lhs_index_k>: column index of LHS' attributes indexes separated by commas (e.g. 1,2,3). You can avoid to specify them:
            if you don't specify RHS' attribute index we'll find RFDs using each attribute as RHS and the remaining as LHS;
            if you specify a valid RHS index we'll assume your LHS as the remaining attributes;
    -i <index_col>: the column which contains the primary key of the dataset.
            Specifying it, this will not calculate as distance. NOTE: index column should contains unique values;
    -d <datetime columns>: a list of columns, separated by commas, which values are in datetime format.
            Specifying this, rfd-discovery can depict distance between two date in time format (e.g. ms, sec, min);
    --semantic: use semantic distance on Wordnet for string; For more info here.
    --help: show help. \n
    """
    print(usage_str.format(sys.argv[0]))


if __name__ == "__main__":
    main(sys.argv[1:])
