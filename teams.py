from base import TextBox, Button, InputText, Cadre, C, Font, dim
from helper import scale
from random import randint

E = lambda x: int(x*dim.f) 

DIM_TEAMY = E(80)
DIM_PY = E(70)


def get_y_decal(selected_teams):
        y_decal = 0
        for team in selected_teams:
            y_decal += team.cursor_y
        return y_decal

class Team:
    def __init__(self, pos, dim_x, color, n):
        self.dim = (dim_x, DIM_TEAMY)
        self.textbox = TextBox(self.dim,color, pos, f'  Team {n}',
                        marge=True, TEXT_COLOR=C.BLACK, centered=False)
        b_dx = int(1/5*dim_x)
        self.button_join = Button((b_dx,DIM_TEAMY),C.XLIGHT_GREY,(0,0),'Join',font=Font.f30)
        self.n = n
        self.pos = pos
        self.players = []
        self.color = color

    def create_player(self, username):
        y = 0
        new_player = PlayerBox((self.pos[0],y),self.dim[0],self.color,username)
        self.players.append(new_player)

    def set_pos(self, pos):
        self.pos = pos
        self.textbox.set_pos(pos)
        b_dx = int(1/5*self.dim[0])
        self.button_join.set_pos((pos[0]+self.dim[0]-b_dx,pos[1]))
        cursor_y = DIM_TEAMY
        for player in self.players:
            y = self.pos[1] + cursor_y
            player.textbox.set_pos((pos[0], y))
            cursor_y += DIM_PY
        return cursor_y

    def check_del_player(self, username):
        player_to_del = None
        for player in self.players:
            if player.username == username:
                player_to_del = player
                break
        if player_to_del != None:
            self.players.remove(player_to_del)

    def display(self):
        self.textbox.display()
        self.button_join.display()
        for player in self.players:
            player.display()

class PlayerBox:
    def __init__(self, pos, dim_x, color, username):
        self.pos = pos
        self.dim = (dim_x, DIM_PY)
        self.username = username
        self.textbox = TextBox(self.dim, color, pos, username,
                 font=Font.f50, marge=True, TEXT_COLOR=C.BLACK)

    def display(self):
        self.textbox.display()

class Teams:
    teams = []
    used_colors = []
    can_add_team = True
    n_team_limit = 3
    @classmethod
    def init(cls, pos, dim, client):
        cls.pos = pos
        cls.dim = dim
        cls.client = client
        cls.cadre = Cadre(dim, C.WHITE, pos)
        cls.button_newteam = Button((dim[0],DIM_TEAMY),C.XLIGHT_GREY, (0,0),'New Team')
        cls.create_team(0)
        cls.create_team(1)
        cls.n_team = 2
    
    @classmethod
    def set_players(cls):
        print('SET PLAYERS', cls.client.env_users)
        for username in cls.client.env_users:
            cls.teams[0].create_player(username)

    @classmethod
    def create_team(cls, n):
        color = C.WHITE
        new_team = Team((cls.pos[0],0),cls.dim[0],color,n)
        cls.teams.append(new_team)

    @classmethod
    def reset_pos(cls):
        y_decal = 0
        for team in cls.teams:
            cursor_y = team.set_pos((cls.pos[0],cls.pos[1]+y_decal))
            y_decal += cursor_y
        cls.button_newteam.set_pos((cls.pos[0],cls.pos[1]+y_decal))
    
    @classmethod
    def set_username(cls, username):
        cls.username = username
        cls.teams[0].create_player(username)

    @classmethod
    def react_events(cls, events, pressed):
        team_idx = None
        for i, team in enumerate(cls.teams):
            if team.button_join.pushed(events):
                team_idx = i
                # send to server the new team of the client
                cls.client.send_new_team(team.n)
                cls.change_team(cls.username, team_idx)
                    
        if cls.can_add_team:
            if cls.button_newteam.pushed(events):
                cls.client.create_team()

        cls.check_team_changes()

        cls.reset_pos()

    @classmethod
    def check_team_changes(cls):
        
        # check for player changing team
        for username, team_idx in cls.client.team_changes.items():
            cls.change_team(username, team_idx)
        cls.client.team_changes = {}
        
        # check for potential new team
        if cls.client.team_created:
            cls.create_team(cls.n_team)
            cls.client.team_created = False
            cls.n_team += 1
            if cls.n_team == cls.n_team_limit:
                    cls.can_add_team = False
        
        # check for potential new player
        for username in cls.client.new_env_players:
            cls.teams[0].create_player(username)
        cls.client.new_env_players = []

        # check for potential players left
        for username in cls.client.left_env_players:
            cls.change_team(username, -1)
        cls.client.left_env_players = []

    @classmethod
    def change_team(cls, username, new_team_idx):
        # fisrt del player from team
        for team in cls.teams:
            team.check_del_player(username)
        # then create player in another team
        if new_team_idx != -1: # in the case -1, just delete the player
            team_to_add = cls.get_team(new_team_idx)
            team_to_add.create_player(username)
        else:
            # delete player
            pass
            
    @classmethod
    def get_team(cls, n):
        for team in cls.teams:
            if team.n == n:
                return team

    @classmethod
    def reset(cls, keep_username=True):
        print('RESET')
        for team in cls.teams:
            team.players = []
        if keep_username:
            cls.teams[0].create_player(cls.username)

    @classmethod
    def display(cls):
        cls.cadre.display()
        for team in cls.teams:
            team.display()
        if cls.can_add_team:
            cls.button_newteam.display()

    