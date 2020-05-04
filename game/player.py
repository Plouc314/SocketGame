import pygame
import math
from base import screen, C, dim, Font, TextBox
from .helper import Delayed, Counter, cal_angle 
from helper import scale
E = lambda x: int(x*dim.f) 
fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'

char_1 = pygame.image.load('game/imgs/c1.png')
char_2 = pygame.image.load('game/imgs/unicorn.png')

chars = [char_1, char_2]

DIM_P = scale((160,160), dim.f)
DIM_HB = scale((130, 20), dim.f)
DIM_TNAME = scale((140, 35), dim.f)

TCOLORS = [C.DARK_BLUE, C.DARK_GREEN, C.DARK_PURPLE]
LTCOLORS = [C.LIGHT_BLUE, C.LIGHT_GREEN, C.LIGHT_PURPLE] 

SMOUSEBUTTONDOWN = 0
SMOVELEFT = 1
SMOVERIGHT = 2
SJUMP = 3
SPAWN_POSITIONS = [(0,E(1300)),(E(2800),E(900)), (E(1200),E(200))]

class Player:
    orien = 0
    SPEED = E(15)
    POWER_JUMP = math.sqrt(150)
    POS_W = scale((50,100), dim.f)
    dim = DIM_P
    dead = False
    client = None
    # gravity
    dh = 0
    can_jump = False
    # health bar
    health_surf = pygame.Surface(DIM_HB)
    health_surf.fill(C.GREEN)
    # delay check pos
    delay = 0
    DTIME = 100
    def __init__(self, char, username, team_idx, is_client=False, base_weapon=None):
        self.img = chars[char]
        self.img = pygame.transform.scale(self.img, self.dim)
        self.original_img = self.img
        self.base_weapon = base_weapon
        self.active_weapon = base_weapon
        self.username = username
        self.team_idx = team_idx
        self.SPAWN_POS = SPAWN_POSITIONS[team_idx]
        self.text_username = TextBox(DIM_TNAME, TCOLORS[team_idx],[0,0],username,
                            font=Font.f30, marge=True, TEXT_COLOR=C.WHITE)
        self.pos = list(self.SPAWN_POS)
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
        self.active_weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))
    
    @property
    def y(self):
        return self.pos[1]
    
    @y.setter
    def y(self, value):
        self.pos[1] = value
        self.active_weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))
    
    def set_weapon(self, weapon):
        self.active_weapon = weapon
        self.active_weapon.set_pos((self.pos[0]+self.POS_W[0], self.pos[1]+self.POS_W[1]))

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
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                as_shot = self.active_weapon.fire(self.orien, self.team_idx)
                fire = as_shot

        if pressed[pygame.K_a]:
            left = 1
            self.move_left()

        if pressed[pygame.K_d]:
            right = 1
            self.move_right()

        if pressed[pygame.K_SPACE] and self.can_jump:
            jump = 1

        # check if player is moving
        if not left and not right and self.dh in [0,1]:
            pos = scale(self.pos, 1/dim.f) # standartize coord
        else:
            pos = None

        self.client.env_game(self.orien, fire, left, right, jump, pos)
        self.active_weapon.rotate(self.orien)
        self.active_weapon.update()
        self.check_jump_client(pressed)

    def react_events_server(self, comm):
        if 'angle' in comm.keys():
            self.orien = comm['angle']
            self.active_weapon.rotate(self.orien)
            self.active_weapon.update()
        
        if 'fire' in comm.keys():
            self.active_weapon.fire(self.orien, self.team_idx, from_server=True)
        
        if comm['left']:
            self.move_left()
        if comm['right']:
            self.move_right()
        
        self.check_jump_server(comm)

        # check for a potential position update
        if 'x' in comm.keys():
            self.x = E(comm['x'])
            self.y = E(comm['y'])
        

    def check_jump_client(self, pressed):
        if pressed[pygame.K_SPACE] and self.can_jump:
            self.dh = -self.POWER_JUMP
            self.can_jump = False
            return True
        return False

    def check_jump_server(self, comm):
        if 'jump' in comm.keys() and self.can_jump:
            self.dh = -self.POWER_JUMP
            self.can_jump = False
            return True
        return False

    def get_angle(self):
        mouse_pos = pygame.mouse.get_pos()
        weapon_pos = self.active_weapon.rect.center
        angle = cal_angle(mouse_pos, weapon_pos)
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
        self.y = self.pos[1] + E(int(1/2*self.dh*abs(self.dh)))
        self.dh += 1

        # check if player is dead
        if self.health <= 0:
            self.health = 1 # temporary set a health -> waiting for the death confirmation
            Score.is_dead(self)

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
        screen.blit(self.health_surf, (self.pos[0]+E(15),self.pos[1]-E(30)))
        decal_x = DIM_HB[0] - x
        screen.blit(red_surf, (self.pos[0]+E(15)+decal_x,self.pos[1]-E(30)))

    def display_username(self):
        rect = self.text_username.surf.get_rect()
        new_pos = (int(self.pos[0] + self.dim[0]/2), self.pos[1] - E(60))
        self.text_username.set_pos(new_pos, center=True)
        self.text_username.display()

    def display(self):
        screen.blit(self.img, self.pos)
        self.display_health()
        self.display_username()
        self.active_weapon.display()

    def respawn(self):
        self.x = self.SPAWN_POS[0]
        self.y = self.SPAWN_POS[1]
        self.dead = False
        self.health = 100
