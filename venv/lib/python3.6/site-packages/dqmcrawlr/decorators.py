import time
from functools import wraps


def time_measured(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print("\t{0:.2f}s".format(end - start))

    return decorated
