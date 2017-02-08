from contextlib import contextmanager
import time
import csv
from functools import wraps
from warnings import simplefilter, warn

"""This module contain utility code used all over the project"""

@contextmanager
def timeit_context(name):
    """
    Return the time of a block of code included into a with statement
    :param name: name of the block of code
    :type name: str
    :return: the time elapset
    :rtype: str
    """
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {:.2f} ms'.format(name, elapsedTime * 1000))


def check_sep_n_header(csv_file):
    """
    Given a valid path to a CSV file, it deduce the separator and the presence or not of the header
    :param csv_file: a valid path to a CSV file
    :type csv_file: str
    :return: a tuple with the CSV delimiter and 0 if the CSV file has an header, None otherwise
    :rtype: tuple
    """
    with open(csv_file) as csv_f:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csv_f.readline())
        csv_f.seek(0)
        has_header = sniffer.has_header(csv_f.readline())
        csv_f.seek(0)
    return dialect.delimiter, 0 if has_header else None


def get_hs_combination(col_len: int) -> list:
    """
    Given a number of column, it generate all the combination of lhs and rhs
    :param col_len: column's number
    :type col_len: int
    :return: list of dict where each element containing a combination
    :rtype: list
    """
    col_list = list(range(col_len))
    combination = list()
    for i in range(0, len(col_list)):
        combination.append({'rhs': [col_list[i]], 'lhs': col_list[:i] + col_list[i + 1:]})
    return combination


def get_cols_count(csv_file, c_sep=';'):
    """
    Given a valid CSV file's path and the relative separator, it return the columns' number of the CSV file.
    :param csv_file: valid path to a CSV file
    :type csv_file: str
    :param c_sep: separator used to separated the values in the CSV. Default behavior is as if set to False if no values is passed.
    :return: the CSV column's number
    :rtype: int
    """
    with open(csv_file) as csv_f:
        return len(csv_f.readline().split(c_sep))


def deprecated(func):
    """
    This is a decorator used to mark functions as deprecated. When the decorated function is called, it will launch a
    warning.
    :param func: the decorated function
    :type func: function
    """
    def new_funct(*args, **kwargs):
        simplefilter('always', DeprecationWarning)
        warn('Call to deprecated function {}'.format(func.__name__), category=DeprecationWarning, stacklevel=2)
        simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)
    return new_funct
