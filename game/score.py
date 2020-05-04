import pygame
from base import screen, Font, C, dim, TextBox, Button
from helper import scale, timer
from time import sleep

fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'
heart_img = pygame.image.load('game/imgs/blood.png')
heart_img = pygame.transform.scale(heart_img, scale((50,50), dim.f))

E = lambda x: int(x*dim.f) 
cposx = lambda pos: (dim.center_x - int(pos[0]/2))/dim.f # will be rescaled after
cposy = lambda pos: (dim.center_y - int(pos[1]/2))/dim.f # will be rescaled after

TCOLORS = [C.BLUE, C.GREEN, C.PURPLE]

POS_SC = scale((100,100), dim.f)
DIM_TEXTEND = scale((800, 120), dim.f)
POS_TEXTEND = scale((cposx(DIM_TEXTEND),cposy(DIM_TEXTEND)), dim.f)
DIM_BBACK = scale((200,100), dim.f)
POS_BBACK = (dim.x - E(300), E(100))
DIM_TTEAM = scale((400,80), dim.f)
DIM_TP = scale((300,60), dim.f)
DIM_TLEFT = scale((200, 200), dim.f)
POS_TLEFT = (dim.x - E(300),E(220))

LEFT_MSG_LIFETIME = 60

class Score:
    text_end = TextBox(DIM_TEXTEND,C.WHITE, POS_TEXTEND,'', font=Font.f100, marge=True)
    button_back = Button(DIM_BBACK, C.LIGHT_BLUE, POS_BBACK, 'Exit')
    text_team = TextBox(DIM_TTEAM, C.LIGHT_BROWN, (0,0),'',
                font=Font.f70, marge=True)
    text_player = TextBox(DIM_TP, C.LIGHT_BROWN, (0,0),'',
                font=Font.f50, centered=False, marge=True)
    text_left = TextBox(DIM_TLEFT, C.WHITE, POS_TLEFT, '',font=Font.f30)
    winner = 0
    client_player = None
    client = None
    ended = False
    left_players = {} # dict: username:lifetime

    @classmethod
    def set_teams(cls, teams):
        cls.teams = {}
        cls.players = []
        cls.team_idxs = []
        for i, players in teams.items():
            cls.team_idxs.append(i)
            lives = [3 for player in players]
            have_losts = [False for player in players]
            d = {'players':players,'lives':lives, 'have_losts':have_losts}
            cls.teams[i] = d
            cls.players.extend(players)
        cls.n_team = len(cls.teams)
        cls.losts = [False for _ in range(cls.n_team)]

    @classmethod
    def display_lives(cls):
        cls.display_left_players()
        dy = 0
        for u, team in cls.teams.items():
            cls.text_team.set_text(f'Team {u}')
            cls.text_team.set_color(TCOLORS[u], marge=True)
            cls.text_team.set_pos((POS_SC[0],POS_SC[1]+dy))
            cls.text_team.display()
            dy += E(100)
            for i, player in enumerate(team['players']):
                cls.text_player.set_text(player.username)
                cls.text_player.set_color(TCOLORS[u], marge=True)
                cls.text_player.set_pos((POS_SC[0],POS_SC[1]+dy))
                cls.text_player.display()
                for e in range(team['lives'][i]):
                    screen.blit(heart_img, (POS_SC[0]+E(100)+e*E(60),POS_SC[1]+E(5)+dy))
                dy += E(80)
    
    @classmethod
    def is_dead(cls, other_player):
        for team in cls.teams.values():
            for i, player in enumerate(team['players']):
                if player is other_player:
                    cls.client.game_dead_player(player.username)
                    
    @classmethod
    def check_confirmed_death(cls):
        for username in cls.client.dead_players:
            dead_player = cls.get_player(username)
            for team in cls.teams.values():
                for i, player in enumerate(team['players']):
                    if player is dead_player:
                        player.dead = True
                        team['lives'][i] -= 1
                        if team['lives'][i] == 0:
                            team['have_losts'][i] = True
                        else:
                            player.respawn()
                        
        cls.client.dead_players = []

    @classmethod
    def check_confirmed_hit(cls):
        for info in cls.client.hit_players:
            hit_player = cls.get_player(info['username'])
            hit_player.health -= info['damage']

        cls.client.hit_players = []

    @classmethod
    def check_leaving_players(cls):
        for username in cls.client.ingame_quit_players:
            team_idx, idx = cls.get_index(username)
            # change leaving player state to 'have lost'
            cls.teams[team_idx]['have_losts'][idx] = True
            cls.teams[team_idx]['lives'][idx] = 0
            cls.left_players[username] = LEFT_MSG_LIFETIME
        cls.client.ingame_quit_players = []

    @classmethod
    def have_lost(cls, other_player):
        for team in cls.teams.values():
            for i, player in enumerate(team['players']):
                if player is other_player:
                    return team['have_losts'][i]
    
    @classmethod
    def check_win(cls):
        # update teams status
        for u, team in cls.teams.items():
            lost = True
            for i in range(len(team['players'])):
                if not team['have_losts'][i]:
                    lost = False
            if lost:
                cls.losts[u] = True
        
        # check for one winner
        n_loser = cls.losts.count(True)
        if n_loser == cls.n_team - 1:
            # get the winner
            for i, v in enumerate(cls.losts):
                if v == False:
                    cls.winner = cls.team_idxs[i]
                    cls.ended = True
                    cls.text_end.set_text(f'Winner Team {cls.winner}')
                    # set color
                    if cls.winner == cls.client_team:
                        cls.text_end.set_color(C.LIGHT_GREEN, marge=True)
                    else:
                        cls.text_end.set_color(C.LIGHT_RED, marge=True)
        
    @classmethod
    def get_player(cls, username):
        for player in cls.players:
            if player.username == username:
                return player

    @classmethod
    def react_events(cls):
        cls.check_leaving_players()
        cls.check_confirmed_hit()
        cls.check_confirmed_death()
        for comm in cls.client.game_msgs:
            username = comm['username']
            player = cls.get_player(username)
            if not cls.client_player is player:
                try:
                    player.react_events_server(comm)
                except: print("[ERROR] Can't react to server frame message")
        cls.client.game_msgs = []

    @classmethod
    def run_end(cls, events, pressed):
        cls.react_events_end(events, pressed)
        cls.display_end()

    @classmethod
    def react_events_end(cls, events, pressed):
        if cls.button_back.pushed(events):
            cls.client.in_game = False
            cls.client.in_game_session = False
            cls.client.quit_game_or_env()
            pygame.mouse.set_visible(True)

    @classmethod
    def display_end(cls):
        cls.text_end.display()
        cls.button_back.display()

    @classmethod
    def display_left_players(cls):
        text = ''
        to_pop = []
        for username in cls.left_players.keys():
            cls.left_players[username] -= 1
            if cls.left_players[username] == 0:
                to_pop.append(username)
            else:
                text += f"{username} left game\n"
        
        # remove old left players
        for username in to_pop:
            cls.left_players.pop(username)

        if text != '':
            # update and display text
            cls.text_left.set_text(text)
            cls.text_left.display()

    @classmethod
    def get_index(cls, username):
        ''' Return the index of the team and the index of the player in the team (u, i)'''
        for u, team in cls.teams.items():
            for i, player in enumerate(team['players']):
                if player.username == username:
                    return (u, i)

    @classmethod
    def reset(cls):
        cls.winner = 0
        cls.client_player = None
        cls.client = None
        cls.ended = False
        cls.teams = {}
        cls.players = []

