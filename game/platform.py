import pygame
from base import dim, screen, C, dim
from .weapons import M4
from .helper import Delayed, Counter, mean
from helper import scale
from random import randint


DIM_TOWER = (400,400)
E = lambda x: int(x*dim.f) 

COLORS = [C.BLUE, C.GREEN, C.PURPLE, C.YELLOW, C.RED]

get_color = lambda: COLORS[randint(0,4)]

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

class Item(Form):
    MARGE_WIDTH = E(4)
    func = None
    def __init__(self, dim, pos, color, img, obj,amplitude=4):
        super().__init__(dim, list(pos), color)
        self.img = img
        self.dh = 0
        self.increment = 1/4
        self.obj = obj
        self.amplitude = amplitude

    def update(self):
        self.dh += self.increment
        if abs(self.dh) == abs(self.amplitude):
            if self.dh < 0:
                self.increment = 1/4
            else:
                self.increment = -1/4
        
        self.pos[1] += int(self.dh)
        self.set_corners(self.pos, self.dim)
    
    def when_collide(self, player):
        self.func(self, player)

    def display(self):
        super().display()
        screen.blit(self.img, self.pos)

items = []

DIM_ITEM = (E(80), E(80))

img_m4 = pygame.image.load('game/imgs/m4.png')
img_m4 = pygame.transform.scale(img_m4, DIM_ITEM)

item1 = Item(DIM_ITEM, (E(400),E(1100)), C.LIGHT_GREY, img_m4, M4)

# set action of collision
def bonus_weapon(self, player):
    new_weapon = self.obj()
    new_weapon.player = player
    player.set_weapon(new_weapon)

# function that is executed when the item is touch
item1.func = bonus_weapon

items.append(item1)

DIM_B = E(100)

blocks = []

#1
d = (E(300),E(100))
p = (E(400),E(1300))
b = Form(d,p, get_color())
blocks.append(b)
#2
d = (E(200),E(100))
p = (E(0),E(1000))
b = Form(d,p, get_color())
blocks.append(b)
#3
d = (E(200),E(100))
p = (E(500),E(800))
b = Form(d,p, get_color())
blocks.append(b)
#4
d = (E(100),E(200))
p = (E(700),E(700))
b = Form(d,p, get_color())
blocks.append(b)
#5
d = (E(100),E(100))
p = (E(1300),E(1500))
b = Form(d,p, get_color())
blocks.append(b)
#6
d = (E(100),E(200))
p = (E(1400),E(1400))
b = Form(d,p, get_color())
blocks.append(b)
#7
d = (E(400),E(100))
p = (E(1700),E(500))
b = Form(d,p, get_color())
blocks.append(b)
#8
d = (E(100),E(100))
p = (E(1700),E(400))
b = Form(d,p, get_color())
blocks.append(b)
#9
d = (E(400),E(100))
p = (E(2500),E(800))
b = Form(d,p, get_color())
blocks.append(b)
#10
d = (E(700),E(500))
p = (E(2300),E(1100))
b = Form(d,p, get_color())
blocks.append(b)
#11
d = (E(200),E(100))
p = (E(700),E(400))
b = Form(d,p, get_color())
blocks.append(b)
#12
d = (E(300),E(100))
p = (E(1000),E(200))
b = Form(d,p, get_color())
blocks.append(b)
#13
d = (E(100),E(100))
p = (E(300),E(500))
b = Form(d,p, get_color())
blocks.append(b)
#14
d = (E(200),E(100))
p = (E(2800),E(500))
b = Form(d,p, get_color())
blocks.append(b)
#15
d = (E(300),E(100))
p = (E(2300),E(200))
b = Form(d,p, get_color())
blocks.append(b)
#16
d = (E(200),E(200))
p = (E(2000),E(1400))
b = Form(d,p, get_color())
blocks.append(b)
#17
d = (E(100),E(100))
p = (E(2200),E(1300))
b = Form(d,p, get_color())
blocks.append(b)