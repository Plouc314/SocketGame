from time import time

def timer(func):
    def inner(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        print('{}: {:.5f}s'.format(func.__name__, time()-start))
        return result
    return inner

def cumsum(array, r, separator=''):
    if type(r) == str:
        f = lambda x: str(x)
    else:
        f = lambda x: x
    lenght = len(array) - 1
    for i, v in enumerate(array):
        if i < lenght:
            r += f(v) + separator
        else:
            r += f(v)
    return r

def filt(x):
    for i in range(len(x)):
        if x[i] == '':
            x.pop(i)
        else:
            x[i] = int(x[i])
    return x