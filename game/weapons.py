import pygame
import math
from base import dim, screen, C
from .helper import Delayed, Counter
from helper import scale

E = lambda x: int(x*dim.f) 

DIM_W = scale((140,140), dim.f)

fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'

ak = pygame.image.load('game/imgs/ak.png')
m4 = pygame.image.load('game/imgs/m4.png')
sniper = pygame.image.load('game/imgs/sniper.png')
bazooka = pygame.image.load('game/imgs/bazooka.png')
explosion = pygame.image.load('game/imgs/explosion.png')

class Weapon:
    pos = None
    state = True
    delayed = False
    delay = 0

    def set_pos(self, pos):
        self.pos = pos
        self.rect.center = pos

    @Counter.call
    def rotate(self, angle):
        if abs(angle)<90 and self.state:
            self.original_img = pygame.transform.flip(self.original_img, 0, 1)
            self.img = self.original_img
            self.state = False
        elif abs(angle)>90 and not self.state:
            self.original_img = pygame.transform.flip(self.original_img, 0, 1)
            self.img = self.original_img
            self.state = True

        self.img = pygame.transform.rotate(self.original_img, angle+180)
        # set same center to keep same position
        x, y = self.rect.center
        self.rect = self.img.get_rect()
        self.rect.center = (x, y) 

    def fire(self, orien, username, from_server=False):
        if not self.delayed or from_server:
            new_bullet = Bullet(self.s_bullets, self.rect.center, self.v_bullets, orien,
                     username=username, damage=self.damage)
            BulletSystem.bullets.append(new_bullet)
            self.delayed = True
            return 1 
        return 0 # the return statement is useful to know if the client player could shot (for the server)
    
    def update(self):
        if self.delayed:
            self.delay += 1
            if self.delay == self.firing_rate:
                self.delayed = False
                self.delay = 0

    def display(self):
        screen.blit(self.img, self.rect)

class AK(Weapon):
    original_img = pygame.transform.scale(ak, DIM_W)
    img = original_img
    rect = img.get_rect()
    v_bullets = 80
    s_bullets = scale((10,10), dim.f)
    damage = 15
    firing_rate = 3
    def __init__(self):
        super().__init__()
    

class M4(Weapon):
    original_img = pygame.transform.scale(m4, DIM_W)
    img = original_img
    rect = img.get_rect()
    v_bullets = 80
    s_bullets = scale((10,10), dim.f)
    damage = 15
    firing_rate = 3
    def __init__(self):
        super().__init__()

class Sniper(Weapon):
    original_img = pygame.transform.scale(sniper, DIM_W)
    img = original_img
    rect = img.get_rect()
    v_bullets = 100
    s_bullets = scale((15, 15), dim.f)
    damage = 60
    firing_rate = 30
    def __init__(self):
        super().__init__()

class Bazooka(Weapon):
    original_img = pygame.transform.scale(bazooka, DIM_W)
    img = original_img
    rect = img.get_rect()
    v_bullets = 30
    s_bullets = scale((30, 30), dim.f)
    damage = 100
    firing_rate = 30
    def __init__(self):
        super().__init__()


class Explosion:
    to_remove = False
    def __init__(self, pos, dim, duration):
        self.img = pygame.transform.scale(explosion, dim)
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.duration = duration
        self.live_time = 0
    
    def display(self):
        screen.blit(self.img, self.rect)
        self.live_time += 1
        if self.live_time == self.duration:
            self.to_remove = True

class BulletSystem:
    # store all the bullets
    bullets = []
    explosions = []
    @classmethod
    def update(cls, platforms, players):
        for bullet in cls.bullets:
            if bullet.in_dim():
                bullet.update()
                bullet.display()
            else:
                try:
                    cls.bullets.remove(bullet)
                except:
                    print('[ERROR] BulletSystem Error')

            # check for collision
            for platform in platforms:
                if platform.collision(bullet.corners, just_touch=True):
                    cls.touch(bullet)
        
            for player in players:
                if not player.dead: # check that the player is alive
                    if player.username != bullet.username: # check that bullet don't tuch player who fired it
                        if player.touch_hitbox(bullet.rect.center): # bullet touch player
                            # decrease health of player
                            player.health -= bullet.damage
                            cls.touch(bullet)

        for expl in cls.explosions:
            expl.display()
            if expl.to_remove:
                cls.explosions.remove(expl)

    @classmethod
    def touch(cls, bullet):
        # create an explosion of 5 frame
        size = 5* bullet.dim[0]
        new_expl = Explosion(bullet.rect.center,(size,size),10)
        cls.explosions.append(new_expl)
        cls.bullets.remove(bullet)

class Bullet(pygame.sprite.Sprite):
    
    def __init__(self, dim, pos, v, orien, username='', damage=0):
        self.username = username
        self.damage = damage
        self.dim = dim
        self.surf = pygame.Surface(dim)
        self.surf.fill(C.RED)
        self.rect = self.surf.get_rect()
        self.rect.center = pos
        angle = -(3.14/180*orien)
        self.dx = math.cos(angle)*v
        self.dy = math.sin(angle)*v
        self.corners = [pos for _ in range(4)]

    def update(self):
        # move the bullet
        x =  self.dx + self.rect.center[0]
        y =  self.dy + self.rect.center[1]
        self.corners = [(x,y) for _ in range(4)]
        self.rect.center = (x,y)

    def display(self):
        screen.blit(self.surf, self.rect)
    
    def in_dim(self):
        x, y = self.rect.center
        if not 0 < x < dim.x:
            return False
        if not 0 < y < dim.y:
            return False
        return True
    
