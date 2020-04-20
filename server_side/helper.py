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