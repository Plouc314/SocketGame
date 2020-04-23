import pygame
import math
from base import screen, C, dim, Font
from .helper import Delayed, Counter 

fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'

char_1 = pygame.image.load(fpath+'c1.png')
char_2 = pygame.image.load(fpath+'unicorn.png')

chars = [char_1, char_2]

DIM_P = (160,160)
DIM_HB = (130, 20)

SMOUSEBUTTONDOWN = 0
SMOVELEFT = 1
SMOVERIGHT = 2
SJUMP = 3


class Player:
    orien = 0
    weapon = None
    SPEED = 15
    POWER_JUMP = 12
    POS_W = (50,100)
    dim = DIM_P
    SPAWN_POS = (100,100)
    dead = False
    client = None
    # gravity
    dh = 0
    can_jump = False
    # health bar
    health_surf = pygame.Surface(DIM_HB)
    health_surf.fill(C.GREEN)
    def __init__(self, char, pos, username, is_client=False):
        self.img = chars[char]
        self.img = pygame.transform.scale(self.img, self.dim)
        self.original_img = self.img
        self.username = username
        self.text_username = Font.f30.render(username,True,C.BLACK)
        self.pos = list(pos)
        self.health = 100
        self.set_corners()
        self.is_client = is_client

        # set delayer to jump
        deco_jump = Delayed(5)
        self.check_jump_client = deco_jump(self.check_jump_client)
        self.check_jump_server = deco_jump(self.check_jump_server)

    
    @property
    def x(self):
        return self.pos[0]
    
    @x.setter
    def x(self, value):
        self.pos[0] = value
        self.weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))
    
    @property
    def y(self):
        return self.pos[1]
    
    @y.setter
    def y(self, value):
        self.pos[1] = value
        self.weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))
    
    def set_weapon(self, weapon):
        self.weapon = weapon
        self.weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))

    def set_corners(self):
        self.TOPLEFT = self.pos
        self.TOPRIGHT = (self.pos[0]+self.dim[0],self.pos[1])
        self.BOTTOMLEFT = (self.pos[0], self.pos[1]+self.dim[1])
        self.BOTTOMRIGHT = (self.pos[0]+self.dim[0],self.pos[1]+self.dim[1])
        self.corners = (self.TOPLEFT, self.TOPRIGHT, self.BOTTOMLEFT, self.BOTTOMRIGHT)

    @Counter.call
    def react_events_client(self, pressed, events):
        self.orien = self.get_angle()
        fire, left, right, jump = 0,0,0,0
        self.weapon.rotate(self.orien)
        self.weapon.update()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.weapon.fire(self.orien, self.username)
                fire = 1
        if pressed[pygame.K_a]:
            self.move_left()
            left = 1
        elif pressed[pygame.K_d]:
            self.move_right()
            right = 1
        if pressed[pygame.K_SPACE]:
            jump = 1
        self.client.env_game(self.orien, fire, left, right, jump)
        self.check_jump_client(pressed)

    def react_events_server(self, angle, fire, left, right, jump):
        self.orien = angle
        self.weapon.rotate(self.orien)
        self.weapon.update()
        if fire:
            self.weapon.fire(self.orien, self.username)
        if left:
            self.move_left()
        elif right:
            self.move_right()
        self.check_jump_server(jump)
            
    def check_jump_client(self, pressed):
        if pressed[pygame.K_SPACE] and self.can_jump:
            self.dh = -self.POWER_JUMP
            self.can_jump = False
            return True
        return False

    def check_jump_server(self, jump):
        if jump and self.can_jump:
            self.dh = -self.POWER_JUMP
            self.can_jump = False
            return True
        return False

    def get_angle(self):
        mouse_pos = pygame.mouse.get_pos()
        weapon_pos = self.weapon.rect.center
        angle = -math.atan2(mouse_pos[1]-weapon_pos[1], mouse_pos[0]-weapon_pos[0])
        angle = 180/3.14 * angle
        return angle

    def move_left(self):
        self.x = self.pos[0] - self.SPEED
    
    def move_right(self):
        self.x = self.pos[0] + self.SPEED

    def collisions(self,platforms):
        self.set_corners()
        for platform in platforms:
            is_col, from_above, new_pos = platform.collision(self.corners)
            if is_col:
                self.x = new_pos[0]
                self.y = new_pos[1]
                # if was jumping -> stop the jump
                if self.dh < 0:
                    self.dh = 0
                if from_above:
                    # touch ground -> can jump
                    self.dh = 0
                    self.can_jump = True
                break
        
        self.collision_bordure()

    def update(self, Score):
        # gravity
        self.y = self.pos[1] + int(1/2*self.dh*abs(self.dh))
        self.dh += 1

        # check if player is dead
        if self.health <= 0:
            self.dead = True
            Score.is_dead(self)
            if not Score.have_lost(self):
                self.respawn()

    def collision_bordure(self):
        # check screen bordure
        if self.x < 0:
            self.x = 0
        elif self.x > dim.x - DIM_P[0]:
            self.x = dim.x - DIM_P[0]
        
        if self.y < 0:
            self.y = 0
        elif self.y > dim.y - DIM_P[1]:
            # touch ground -> can jump
            self.dh = 0
            self.can_jump = True
            self.y = dim.y - DIM_P[1]

    def touch_hitbox(self, pos):
        if pos[1] > self.TOPLEFT[1] and pos[1] < self.BOTTOMLEFT[1]:
            if pos[0] > self.TOPLEFT[0] and pos[0] < self.TOPRIGHT[0]:
                return True

    def display_health(self):
        # get red part
        x = int((100-self.health) * DIM_HB[0]/100)
        red_surf = pygame.Surface((x,DIM_HB[1]))
        red_surf.fill(C.RED)
        screen.blit(self.health_surf, (self.pos[0]+15,self.pos[1]-30))
        decal_x = DIM_HB[0] - x
        screen.blit(red_surf, ((self.pos[0]+15+decal_x,self.pos[1]-30)))

    def display_username(self):
        rect = self.text_username.get_rect()
        rect.center = (int(self.pos[0] + self.dim[0]/2), self.pos[1]- 50)
        screen.blit(self.text_username, rect)

    def display(self):
        screen.blit(self.img, self.pos)
        self.display_health()
        self.display_username()
        if self.weapon:
            self.weapon.display()

    def respawn(self):
        self.x = self.SPAWN_POS[0]
        self.y = self.SPAWN_POS[1]
        self.dead = False
        self.health = 100
