import pygame

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

def get_pressed_key(pressed):
    if pressed[pygame.K_a]:
        return 'a'
    elif pressed[pygame.K_b]:
        return 'b'
    elif pressed[pygame.K_c]:
        return 'c'
    elif pressed[pygame.K_d]:
        return 'd'    
    elif pressed[pygame.K_e]:
        return 'e'
    elif pressed[pygame.K_f]:
        return 'f'
    elif pressed[pygame.K_g]:
        return 'g'
    elif pressed[pygame.K_h]:
        return 'h'
    elif pressed[pygame.K_i]:
        return 'i'
    elif pressed[pygame.K_j]:
        return 'j'
    elif pressed[pygame.K_k]:
        return 'k'
    elif pressed[pygame.K_l]:
        return 'l'
    elif pressed[pygame.K_m]:
        return 'm'
    elif pressed[pygame.K_n]:
        return 'n'
    elif pressed[pygame.K_o]:
        return 'o'
    elif pressed[pygame.K_p]:
        return 'p'
    elif pressed[pygame.K_q]:
        return 'q'
    elif pressed[pygame.K_r]:
        return 'r'
    elif pressed[pygame.K_s]:
        return 's'
    elif pressed[pygame.K_t]:
        return 't'
    elif pressed[pygame.K_u]:
        return 'u'
    elif pressed[pygame.K_v]:
        return 'v'
    elif pressed[pygame.K_w]:
        return 'w'
    elif pressed[pygame.K_x]:
        return 'x'
    elif pressed[pygame.K_y]:
        return 'y'
    elif pressed[pygame.K_z]:
        return 'z'
    elif pressed[pygame.K_1]:
        return '1'
    elif pressed[pygame.K_2]:
        return '2'
    elif pressed[pygame.K_3]:
        return '3'
    elif pressed[pygame.K_4]:
        return '4'
    elif pressed[pygame.K_5]:
        return '5'
    elif pressed[pygame.K_6]:
        return '6'
    elif pressed[pygame.K_7]:
        return '7'
    elif pressed[pygame.K_8]:
        return '8'
    elif pressed[pygame.K_9]:
        return '9'
    elif pressed[pygame.K_0]:
        return '0'
    elif pressed[pygame.K_SPACE]:
        return ' '
