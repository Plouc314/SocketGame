from .platform import Form
from .weapons import M4
from base import Font, C, dim, screen, E
import pygame
from random import choice

class Item(Form):
    MARGE_WIDTH = E(4)
    func = None
    client = None
    active = True
    as_send = False
    def __init__(self, dim, pos, color, img, obj, amplitude=4):
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

    def set_pos(self, pos):
        self.pos = list(pos)
        self.set_corners(list(pos), self.dim)

    def display(self):
        super().display()
        screen.blit(self.img, self.pos)

items = []

DIM_ITEM = (E(80), E(80))

img_m4 = pygame.image.load('game/imgs/m4.png')
img_m4 = pygame.transform.scale(img_m4, DIM_ITEM)

img_health = pygame.image.load('game/imgs/hospital.png')
img_health = pygame.transform.scale(img_health, DIM_ITEM)

item_m4 = Item(DIM_ITEM, (E(400),E(1100)), C.LIGHT_GREY, img_m4, M4)

# set action of collision
def bonus_weapon(self, player):
    new_weapon = self.obj()
    new_weapon.player = player
    player.set_weapon(new_weapon)

# function that is executed when the item is touch
item_m4.func = bonus_weapon
items.append(item_m4)

POS_HEALTHS = [(E(300),E(350)),(E(1400),E(1250)),(E(2400),E(50))]

item_health = Item(DIM_ITEM, POS_HEALTHS[1],C.WHITE, img_health, None)
setattr(item_health, 'pos_idx',1)

def extra_health(self, player):
    if not self.as_send:
        self.client.send_item_health(player.username, self.pos_idx)
    self.as_send = True

item_health.func = extra_health
items.append(item_health)

class ItemSystem:
    items = items
    item_health = item_health
    client = None

    @classmethod
    def check_item_confirmations(cls, Score):
        # check for potential confirmation of item touch
        for username, info in cls.client.item_confirmations.items():
            if info['confirmed']:
                if info['type'] == 'health':
                    player = Score.get_player(username)
                    player.health = 100
                    cls.item_health.set_pos(POS_HEALTHS[info['pos_idx']])
                    cls.item_health.as_send = False
            else:
                cls.item_health.as_send = False
        cls.client.item_confirmations = {}

    @classmethod
    def collision(cls, players):
        for player in players:
            for item in cls.items:
                if item.collision(player.corners, just_touch=True) and item.active:
                    item.when_collide(player)
                    
    @classmethod
    def update(cls, Score):
        cls.check_item_confirmations(Score)
        cls.collision(Score.players)
        cls.display()

    @classmethod
    def display(cls):
        for item in cls.items:
            if item.active:
                item.update()
                item.display()
    
    @classmethod
    def set_client(cls, client):
        cls.client = client
        cls.item_health.client = client