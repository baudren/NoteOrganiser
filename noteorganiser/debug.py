from time import time


def timeit(func):
    def wrapped(*args):
        t1 = time()
        r = func(*args)
        t2 = time()
        print("%s took %g" % (func.__name__, t2-t1))
        return r
    return wrapped
