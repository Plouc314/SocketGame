import pygame
from base import screen, Font, C, dim
from helper import scale, timer
from time import sleep

fpath = '/home/alexandre/Documents/python/socket/game/game/imgs/'
heart_img = pygame.image.load('game/imgs/blood.png')
heart_img = pygame.transform.scale(heart_img, scale((50,50), dim.f))

E = lambda x: int(x*dim.f) 
POS_SC = scale((100,100), dim.f)

class Score:
    pos = POS_SC
    font = Font.f50
    winner = 0
    client_player = None
    client = None
    ended = False

    @classmethod
    def set_teams(cls, teams):
        cls.teams = {}
        cls.players = []
        for i, players in teams.items():
            lives = [3 for player in players]
            have_losts = [False for player in players]
            d = {'players':players,'lives':lives, 'have_losts':have_losts}
            cls.teams[i] = d
            cls.players.extend(players)
        cls.n_team = len(cls.teams)
        cls.losts = [False for _ in range(cls.n_team)]

    @classmethod
    def display_lives(cls):
        dy = 0
        for u, team in cls.teams.items():
            text = cls.font.render(f'Team {u}',True,C.BLACK)
            screen.blit(text, (POS_SC[0],POS_SC[1]+dy))
            dy += E(100)
            for i, player in enumerate(team['players']):
                text = cls.font.render(player.username,True,C.BLACK)
                screen.blit(text, (POS_SC[0],POS_SC[1]+dy))
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
                    cls.winner = i
                    cls.ended = True
        
    @classmethod
    def get_player(cls, username):
        for player in cls.players:
            if player.username == username:
                return player

    @classmethod
    def react_events(cls):
        cls.check_confirmed_death()
        for comm in cls.client.game_msgs:
            username = comm['username']
            player = cls.get_player(username)
            player.react_events_server(comm)
        cls.client.game_msgs = []

    @classmethod
    def display_end(cls):
        font = Font.f100
        text = font.render(f'Winner Team {cls.winner}',True,C.BLACK)
        screen.blit(text, (dim.center_x-500,dim.center_y-200))


        
