from contextlib import contextmanager
import time


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {:.2f} ms'.format(name, elapsedTime * 1000))
