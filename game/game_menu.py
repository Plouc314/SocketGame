from base import TextBox, Button, C, Font, dim
from .player import Player
from .weapons import AK, M4, Sniper, Bazooka
from random import randint
from helper import scale
from time import sleep
import pygame

E = lambda x: int(x*dim.f) 
cposx = lambda pos: (dim.center_x - int(pos[0]/2))/dim.f

DIM_TITLE = scale((1200,120), dim.f)
POS_TITLE = scale((cposx(DIM_TITLE), 150), dim.f)
DIM_MAIN_B = scale((200,100), dim.f)
DIM_TEXT = scale((800, 80), dim.f)
POS_TW = scale((cposx(DIM_TEXT),300), dim.f)
POS_BSTART = scale((cposx(DIM_MAIN_B), 800), dim.f)
DIM_BCHOOSEW = scale((200,200), dim.f)
POS_BCWY = scale(400, dim.f)
POS_BCWX = dim.center_x - E(550)


fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'

img_ak = pygame.image.load('game/imgs/ak.png')
img_m4 = pygame.image.load('game/imgs/m4.png')
img_sniper = pygame.image.load('game/imgs/sniper.png')
img_bazooka = pygame.image.load('game/imgs/bazooka.png')

class GameMenu:
    ready = False
    chosen_weapon = None
    character = randint(0,1) # choose randomly between ninja and unicorn
    as_chosen = False
    ready_pushed = False
    players = []
    
    @classmethod
    def init(cls, client, Score):
        cls.client = client
        cls.Score = Score
        cls.text_weapons = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Choose your weapon:', font=Font.f100)
        cls.button_ready = Button(DIM_MAIN_B, C.LIGHT_BLUE, POS_BSTART,'Ready')
        cls.text_are_ready = TextBox(DIM_TEXT, C.WHITE, POS_TW, '0/n players ready', font=Font.f50)
        cls.button_ak = Button(DIM_BCHOOSEW, C.LIGHT_GREEN, (POS_BCWX, POS_BCWY),'',
                            font=Font.f70,image=img_ak)
        cls.button_m4 = Button(DIM_BCHOOSEW, C.LIGHT_GREEN, (POS_BCWX+E(300), POS_BCWY),'',
                            font=Font.f70,image=img_m4)
        cls.button_sniper = Button(DIM_BCHOOSEW, C.LIGHT_GREEN, (POS_BCWX+E(600), POS_BCWY),'',
                            font=Font.f70,image=img_sniper)
        cls.button_bazooka = Button(DIM_BCHOOSEW, C.LIGHT_GREEN, (POS_BCWX+E(900), POS_BCWY),'',
                            font=Font.f70,image=img_bazooka)
        cls.n_players = cls.client.n_env_users
        # now the scope cursor is diplayed
        pygame.mouse.set_visible(False)


    @classmethod
    def run(cls, pressed, events):
        cls.display()
        cls.update()
        cls.react_events(pressed, events)

    @classmethod
    def create_player(cls, username, char, weapon, team):
        is_client = False
        if username == cls.client.username:
            is_client = True
        player = Player(char, username, team,is_client=is_client)
        if weapon == 'ak':
            player.set_weapon(AK())
        elif weapon == 'm4':
            player.set_weapon(M4())
        elif weapon == 'sniper':
            player.set_weapon(Sniper())
        elif weapon == 'bazooka':
            player.set_weapon(Bazooka())

        cls.players.append({'player':player,'team':team})

    @classmethod
    def set_ready(cls):
        # check if the player selected a weapon
        if not cls.as_chosen:
            weapons = ['ak','m4','sniper','bazooka']
            cls.chosen_weapon = weapons[randint(0,3)] # choose weapon randomly
        
        username = cls.client.username
        cls.create_player(username, cls.character, cls.chosen_weapon, cls.client.team)
        cls.client.env_ready(cls.chosen_weapon, cls.character)
        cls.Score.client_player = cls.players[-1]['player']
        cls.Score.client_player.client = cls.client # player must have access to client to send movements
        cls.Score.client_team = cls.client.team

    @classmethod
    def update(cls):
        # check for ready users
        for user in cls.client.ready_users:
            # create new player
            cls.create_player(user['username'],user['char'],user['weapon'],user['team'])
            cls.client.ready_users = []

        # check if everyone is ready
        if len(cls.players) == cls.n_players:
            # wait a little bit to let the server do what it has to do
            sleep(.1)
            cls.ready = True
            cls.client.in_game = True
            teams = cls.set_teams()
            cls.Score.set_teams(teams)

        # update player ready text
        new_text = f'{len(cls.players)}/{cls.n_players} players are ready'
        cls.text_are_ready.set_text(new_text)

    @classmethod
    def set_teams(cls):
        teams = {}
        for player in cls.players:
            if not player['team'] in teams:
                teams[player['team']] = [player['player']]
            else:
                teams[player['team']].append(player['player'])
        return teams

    @classmethod
    def react_events(cls, pressed, events):
        if not cls.ready_pushed:
            if cls.button_ready.pushed(events):
                cls.set_ready()
                cls.ready_pushed = True

        if not cls.as_chosen:
            if cls.button_ak.pushed(events):
                cls.chosen_weapon = 'ak'
                cls.button_ak.set_color(C.BLUE, marge=True)
                cls.as_chosen = True
            elif cls.button_m4.pushed(events):
                cls.chosen_weapon = 'm4'
                cls.button_m4.set_color(C.BLUE, marge=True)
                cls.as_chosen = True
            elif cls.button_sniper.pushed(events):
                cls.chosen_weapon = 'sniper'
                cls.button_sniper.set_color(C.BLUE, marge=True)
                cls.as_chosen = True
            elif cls.button_bazooka.pushed(events):
                cls.chosen_weapon = 'bazooka'
                cls.button_bazooka.set_color(C.BLUE, marge=True)
                cls.as_chosen = True

    @classmethod
    def display(cls):
        cls.text_weapons.display()
        cls.text_are_ready.display()
        cls.button_ak.display()
        cls.button_m4.display()
        cls.button_sniper.display()
        cls.button_bazooka.display()
        if not cls.ready_pushed:
            cls.button_ready.display()

    @classmethod
    def reset(cls):
        cls.ready = False
        cls.chosen_weapon = None
        cls.character = randint(0,1)
        cls.as_chosen = False
        cls.ready_pushed = False
        cls.players = []
