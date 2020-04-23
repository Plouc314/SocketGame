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

from time import time


def mean(array):
    total = 0
    for v in array:
        total += v
    return total/len(array)

class Counter:
    funcs = {'names':[], 'iterations':[],'time':[]}
    @classmethod
    def call(cls,func):
        cls.funcs['names'].append(func.__name__)
        cls.funcs['iterations'].append(0)
        cls.funcs['time'].append(0)
        index = len(cls.funcs['names'])-1
        
        def inner(*args, **kwargs):
            cls.funcs['iterations'][index] += 1
            st = time()
            r = func(*args, **kwargs)
            cls.funcs['time'][index] += time() - st
            return r
        
        return inner
    @classmethod
    def result(cls):
        print('Result:')
        for i in range(len(cls.funcs['names'])):
            name = cls.funcs['names'][i]
            iteration = cls.funcs['iterations'][i]
            time = cls.funcs['time'][i]
            try:
                performance = time/iteration
            except:
                performance = 0
            
            print(f'{name}: {iteration} mean: {performance:.4f} total:{time:.3f}')
    @classmethod
    def reset(cls):
        cls.funcs['time'] = [0 for _ in cls.funcs['names']]
        cls.funcs['iterations'] = [0 for _ in cls.funcs['names']]

