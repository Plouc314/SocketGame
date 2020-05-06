from base import Font, C, dim, TextBox, Button, Cadre, E
from helper import scale

DIM_NAME = scale((220, 60), dim.f)
DIM_BOX = scale((140, 60), dim.f)
DIM_SCORETX = E(500)
DIM_PLAYER = scale((500, 60), dim.f)
DIM_PLAYERY = E(60)

LTCOLORS = [C.LIGHT_BLUE, C.LIGHT_GREEN, C.LIGHT_PURPLE] 

class PlayerResult:
    def __init__(self, pos, username, kill_count, lives, team_idx):
        self.pos = pos
        self.username = username
        self.kill_count = kill_count
        self.lives = lives
        self.team_idx = team_idx
        self.cadre = Cadre(DIM_PLAYER, C.WHITE, pos, set_transparent=True)
        self.text_username = TextBox(DIM_NAME, LTCOLORS[team_idx], pos, username, font=Font.f30)
        self.text_kills = TextBox(DIM_BOX, C.WHITE, (DIM_NAME[0] + pos[0], pos[1]), str(self.kill_count), font=Font.f30)
        self.text_deaths = TextBox(DIM_BOX, C.WHITE, (DIM_NAME[0] + DIM_BOX[0] + pos[0], pos[1]), str(3-lives),font=Font.f30)
    
    def display(self):
        self.text_username.display()
        self.text_kills.display()
        self.text_deaths.display()
        self.cadre.display() # display in last to have proper marge

class TeamTable:
    def __init__(self, pos, info, team_idx):
        self.pos = pos
        self.text_username = TextBox(DIM_NAME, C.WHITE, pos, 'username', font=Font.f30)
        self.text_kills = TextBox(DIM_BOX, C.WHITE, (DIM_NAME[0] + pos[0], pos[1]), 'kill(s)', font=Font.f30)
        self.text_deaths = TextBox(DIM_BOX, C.WHITE, (DIM_NAME[0] + DIM_BOX[0] + pos[0], pos[1]), 'death(s)',font=Font.f30)
        self.players_results = []
        dy = DIM_PLAYERY
        for i in range(len(info['lives'])):
            pos = [self.pos[0], self.pos[1] + dy]
            username = info['players'][i].username
            kill_count = info['kill_count'][i]
            lives = info['lives'][i]
            new_player_res = PlayerResult(pos, username, kill_count, lives, team_idx)
            self.players_results.append(new_player_res)
            dy += DIM_PLAYERY

    def display(self):
        self.text_username.display()
        self.text_deaths.display()
        self.text_kills.display()
        for player_r in self.players_results:
            player_r.display()

class ScoreTable:

    @classmethod
    def init(cls, pos, Score):
        cls.pos = list(pos)
        cls.teams = Score.teams
        cls.team_tables = []
        dx = 0
        for team_idx, info in cls.teams.items():
            pos = [cls.pos[0] + dx, cls.pos[1]]
            new_table = TeamTable(pos, info, team_idx)
            cls.team_tables.append(new_table)
            dx += DIM_SCORETX
    
    @classmethod
    def display(cls):
        for team_t in cls.team_tables:
            team_t.display()