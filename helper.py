import pygame

from time import time

def timer(func):
    def inner(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        print('{}: {:.2f}s'.format(func.__name__, time()-start))
        return result
    return inner

def split_list(delimiter, x):
    s_list = []
    cursor = 1
    for i, v in enumerate(x):
        if v == delimiter:
            if i != 0:
                new_list = x[cursor:i]
                s_list.append(new_list)
                cursor = i + 1
    last_list = x[cursor:]
    s_list.append(last_list)
    return s_list

class Delayed:
    '''
    Creates decorators,

    The decorated function should return True/False depending on whether or not it has been activated,
    if true, creates a delay in order to be spammed.
    '''
    wait = 0
    delayed = False
    def __init__(self, delay):
        self.delay = delay
        
    def __call__(self, func):
        def inner(*args, **kwargs):
            if self.delayed:
                self.wait += 1
                if self.wait == self.delay:
                    self.delayed = False
                    self.wait = 0
            else:
                # first argument if a boolean value of if the tested key was pressed
                executed = func(*args, **kwargs)
                if executed:
                    self.delayed = True
                return executed
        return inner

def cumsum(array, r, separator=''):
    lenght = len(array) - 1
    for i, v in enumerate(array):
        if i < lenght:
            r += v + separator
        else:
            r += v
    return r

def mean(array):
    total = 0
    for v in array:
        total += v
    return total/len(array)

def scale(x,factor):
    if type(x) == list or type(x) == tuple:
        x = list(x)
        for i in range(len(x)):
            x[i] = int(x[i]*factor)
    else:
        x = int(x*factor)
    return x
        

