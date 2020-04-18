def cumsum(array, r, separator=''):
    lenght = len(array) - 1
    for i, v in enumerate(array):
        if i < lenght:
            r += v + separator
        else:
            r += v
    return r

def filt(x):
    for v in x:
        if v == '':
            x.remove(v)
    return x