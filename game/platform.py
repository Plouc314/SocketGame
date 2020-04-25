import pygame
from base import dim, screen, C, dim
from .helper import Delayed, Counter, mean
from helper import scale

fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'

DIM_TOWER = (400,400)
E = lambda x: int(x*dim.f) 


cursor_img = pygame.image.load('game/imgs/cursor.png')
cursor_img = pygame.transform.scale(cursor_img, (E(50),E(50)))

def display_cursor():
    mouse_pos = pygame.mouse.get_pos()
    rect = cursor_img.get_rect()
    rect.center = mouse_pos
    screen.blit(cursor_img, rect)

class Platform:
    def __init__(self, img, dim, pos, marge=(0,0)):
        self.img = img
        self.dim = dim
        self.pos = pos
        self.marge = marge
        self.set_corners(pos, dim)
    
    def set_corners(self, pos, dim):
        self.TOPLEFT = (pos[0] + self.marge[0], pos[1] + self.marge[1])
        self.TOPRIGHT = (pos[0] + dim[0] - self.marge[0],pos[1] + self.marge[1])
        self.BOTTOMLEFT = (pos[0] + self.marge[0], pos[1] + dim[1] - self.marge[1])
        self.BOTTOMRIGHT = (pos[0] + dim[0] - self.marge[0],pos[1] + dim[1] - self.marge[1])
        self.corners = (self.TOPLEFT, self.TOPRIGHT, self.BOTTOMLEFT, self.BOTTOMRIGHT)

    def collision(self, corners, just_touch=False):
        union = {'x':False, 'y':False}
        d = {'x':0, 'y':0}
        # check the y
        if corners[2][1] > self.TOPLEFT[1] and corners[0][1] < self.BOTTOMLEFT[1]:
            union['y'] = True
            if corners[2][1] < self.BOTTOMLEFT[1]:
                d['y'] = corners[2][1] - self.TOPLEFT[1]
            else:
                if corners[0][1] < self.TOPLEFT[1]:
                    d['y'] = self.dim[1]
                else:
                    d['y'] = self.BOTTOMLEFT[1] - corners[0][1]

        # check the x
        if corners[1][0] > self.TOPLEFT[0] and corners[0][0] < self.TOPRIGHT[0]:
            union['x'] = True
            if corners[1][0] < self.TOPRIGHT[0]:
                d['x'] = corners[1][0] - self.TOPLEFT[0]
            else:
                if corners[0][0] < self.TOPLEFT[0]:
                    d['x'] = self.dim[0]
                else:
                    d['x'] = self.TOPRIGHT[0] - corners[0][0]
        
        if just_touch:
            if union['x'] and union ['y']:
                
                return True
            return False

        if union['x'] and union ['y']:
            from_above = False
            dim_x = corners[1][0] -corners[0][0]
            dim_y = corners[2][1] -corners[0][1]
            if d['y'] > d['x']: # re-pos in x
                # check if left or right
                if abs(self.TOPLEFT[0] - corners[1][0]) > abs(self.TOPRIGHT[0] - corners[0][0]):
                    # player going from right to left
                    pos = (self.TOPRIGHT[0]+E(5), corners[0][1])
                else:
                    # player going from left to right
                    pos = (self.TOPLEFT[0]-dim_x-E(5), corners[0][1])
            else: # re-pos in y
                # check if up or down
                if abs(self.TOPLEFT[1] - corners[2][1]) > abs(self.BOTTOMLEFT[1] - corners[0][1]):
                    # player going from down to up
                    pos = (corners[0][0], self.BOTTOMLEFT[1])
                else:
                    # player going from up to down
                    pos = (corners[0][0], self.TOPLEFT[1] - dim_y)
                    from_above = True
            return True, from_above, pos
        return False, None, None

    def display(self):
        screen.blit(self.img, self.pos)


#tower0 = Platform(tower_img, DIM_TOWER, (200,1500), marge=(70,0))
#tower1 = Platform(tower_img, DIM_TOWER, (600,1400), marge=(70,0))
#tower2 = Platform(tower_img, DIM_TOWER, (1000,1300), marge=(70,0))
#
#towers = [tower0, tower1, tower2]

class Form(Platform):
    screen = screen
    MARGE_WIDTH = E(20)
    def __init__(self, dim, pos, color, hitbox_marge=(0,0)):
        super().__init__(None, dim, pos, hitbox_marge)
        self.surf = pygame.Surface(dim)
        self.surf.fill(color)
        self.dim = dim
        self.COLOR = color
        self.set_highlight_color()
        self.MARGE_COLOR = self.high_color
    
    def set_color(self, color, marge=False):
        self.surf.fill(color)
        self.COLOR = color
        if marge:
            self.set_highlight_color()
            self.MARGE_COLOR = self.high_color

    def set_highlight_color(self):
        light_color = []
        for i in range(3):
            if self.COLOR[i] <= 235:
                light_color.append(self.COLOR[i] + 20)
            else:
                light_color.append(255)
        dark_color = []
        for i in range(3):
            if self.COLOR[i] >= 20:
                dark_color.append(self.COLOR[i] - 20)
            else:
                dark_color.append(0)
        if mean(self.COLOR) < 130:
            self.high_color = light_color
        else:
            self.high_color = dark_color

    def display_margin(self):
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPLEFT, self.TOPRIGHT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPLEFT, self.BOTTOMLEFT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPRIGHT, self.BOTTOMRIGHT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.BOTTOMLEFT, self.BOTTOMRIGHT, self.MARGE_WIDTH)

    def display(self):
        self.screen.blit(self.surf, self.pos)
        self.display_margin()

DIM_B = E(100)

blocks = []

block = Form((5*DIM_B, DIM_B),(E(1000),E(1400)),C.RED)
blocks.append(block)


block = Form((3*DIM_B,DIM_B),(E(1700),E(1200)),C.RED)
blocks.append(block)

block = Form((DIM_B,2*DIM_B),(E(500),E(1400)),C.GREEN)
blocks.append(block)

