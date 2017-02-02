from contextlib import contextmanager
import time
import csv


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {:.2f} ms'.format(name, elapsedTime * 1000))


def check_sep_n_header(csv_file):
    with open(csv_file) as csv_f:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csv_f.readline())
        csv_f.seek(0)
        has_header = sniffer.has_header(csv_f.readline())
        csv_f.seek(0)
    return dialect.delimiter, 0 if has_header else None


def get_hs_combination(col_len: int) -> list:
    col_list = list(range(col_len))
    combination = list()
    for i in range(0, len(col_list)):
        combination.append({'rhs': [col_list[i]], 'lhs': col_list[:i] + col_list[i + 1:]})
    return combination


def get_cols_count(csv_file, c_sep=';'):
    with open(csv_file) as csv_f:
        return len(csv_f.readline().split(c_sep))
