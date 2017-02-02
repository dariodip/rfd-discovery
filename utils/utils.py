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
        has_header = sniffer.has_header(csv_f.read())
    return dialect.delimiter, 0 if has_header else None
