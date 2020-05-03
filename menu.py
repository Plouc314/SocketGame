from base import TextBox, Button, InputText, Cadre, C, Font, dim
from chat import Chat
from friends import Friends
from game.main import run_game, start_game
from helper import scale

center_x = 1500 # base to be rescaled

cposx = lambda pos: (dim.center_x - int(pos[0]/2))/dim.f # will be rescaled after
E = lambda x: int(x*dim.f) 

DIM_TITLE = scale((600,120), dim.f)
POS_TITLE = scale((cposx(DIM_TITLE), 150), dim.f)
DIM_MAIN_B = scale((200,100), dim.f)
DIM_LI_MAIN_B = scale((200,80), dim.f)
DIM_NB = scale((120,60), dim.f)
DIM_TEXTBL = scale((150, 100), dim.f)
Y_POS_TEXTBL = scale(400, dim.f)
Y_POS_TEXTBL2 = scale(550, dim.f)
X_POS_TEXTBL = scale(center_x - 250, dim.f)
X_POS_TEXTBL2 = scale(center_x - 200, dim.f)
DIM_LOGINP = scale((400,80), dim.f)
X_POS_LOGINP = scale(center_x, dim.f)
DIM_FAILT = scale((400,80), dim.f)
Y_POS_FAILT = scale(320, dim.f)
DIM_CHAT = scale((800,600), dim.f)
DIM_FR = scale((800,500), dim.f)
POS_BLOG = (scale(cposx(DIM_MAIN_B), dim.f),POS_TITLE[1]+2*DIM_MAIN_B[1])
POS_BSIGN = (scale(cposx(DIM_MAIN_B), dim.f),POS_TITLE[1]+4*DIM_MAIN_B[1])
POS_BDONE = scale((center_x+240, 750), dim.f)
POS_BBACK = scale((100,100), dim.f)
POS_BPLAY = (scale(cposx(DIM_MAIN_B), dim.f),POS_TITLE[1]+2*DIM_MAIN_B[1])
DIM_TEAMS = scale((400, 600), dim.f)
POS_TEAMS = scale((300,250), dim.f)
DIM_TWAIT = scale((500,60), dim.f)
POS_TWAIT = (scale(cposx(DIM_TWAIT), dim.f),POS_TITLE[1]+2*DIM_MAIN_B[1])
DIM_BEXIT = scale((200,80), dim.f)
POS_BEXIT = (dim.x - E(300), E(100))
MARGE = scale(100, dim.f)
LMARGE = scale(50, dim.f)

from teams import Teams

class Menu:
    play_pushed = False
    def __init__(self, client):
        self.client = client
        self.state = 'main'
        # state main
        self.title_main = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Title', font=Font.f100)

        self.button_login = Button(DIM_MAIN_B, C.LIGHT_BLUE,
                                POS_BLOG,'Log in')


        self.button_signup = Button(DIM_MAIN_B, C.LIGHT_BLUE,
                                POS_BSIGN,'Sign up') 

        # state login
        self.title_login = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Log in', font=Font.f100)

        self.text_logusername = TextBox(DIM_TEXTBL,C.WHITE,
                                (X_POS_TEXTBL, Y_POS_TEXTBL), 'Username:', font=Font.f30)

        self.text_password = TextBox(DIM_TEXTBL,C.WHITE,
                                (X_POS_TEXTBL, Y_POS_TEXTBL2), 'Password:', font=Font.f30)

        self.input_username = InputText(DIM_LOGINP, (X_POS_LOGINP, Y_POS_TEXTBL),C.WHITE)
        self.input_password = InputText(DIM_LOGINP, (X_POS_LOGINP, Y_POS_TEXTBL2),C.WHITE)
        self.button_done = Button(DIM_NB,C.LIGHT_BLUE, POS_BDONE, 'Done', font=Font.f30)
        self.button_back = Button(DIM_NB, C.LIGHT_BLUE, POS_BBACK,'Back', font=Font.f30)
        # state signup
        self.title_signup = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Sign up', font=Font.f100) 
        # state fail log
        self.text_faillog = TextBox(DIM_FAILT, C.WHITE, (X_POS_TEXTBL2, Y_POS_FAILT),
                                'Invalid username or password', font=Font.f25, TEXT_COLOR=C.RED)  
        # state fail sign
        self.text_failsign = TextBox(DIM_FAILT, C.WHITE, (X_POS_TEXTBL2, Y_POS_FAILT),
                                'Username already taken', font=Font.f25, TEXT_COLOR=C.RED)  
        # state logged
        self.title_logged = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Welcome', font=Font.f100)
        self.text_username = TextBox(DIM_LOGINP, C.WHITE, (LMARGE, LMARGE),'',marge=True)
        self.button_play = Button(DIM_MAIN_B, C.LIGHT_BLUE, 
                    POS_BPLAY, 'Play') 
        self.chat_logged = Chat(DIM_CHAT, (MARGE,dim.y-DIM_CHAT[1]-MARGE), self.client)
        self.friends = Friends(DIM_FR, (dim.x-DIM_FR[0]-MARGE, E(250)), self.client)
        self.button_disconn = Button(DIM_LI_MAIN_B, C.LIGHT_BLUE, (LMARGE, MARGE+DIM_LOGINP[1])
                        ,'Disconnect',font=Font.f30)
        # state env
        self.title_env = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Env', font=Font.f100)
        self.text_wating = TextBox(DIM_TWAIT,C.WHITE, POS_TWAIT,
                             'Waiting for the other players...', font=Font.f30)
        self.button_exit = Button(DIM_BEXIT, C.LIGHT_BLUE, POS_BEXIT, 'Exit', font=Font.f30)
        self.teams = Teams
        self.teams.init(POS_TEAMS,DIM_TEAMS, client)

    def display_main(self):
        self.title_main.display()
        self.button_login.display()
        self.button_signup.display()
    
    def display_login(self):
        self.title_login.display()
        self.text_logusername.display()
        self.text_password.display()
        self.input_username.display()
        self.input_password.display()
        self.button_back.display()
        self.button_done.display()
    
    def display_signup(self):
        self.title_signup.display()
        self.text_logusername.display()
        self.text_password.display()
        self.input_username.display()
        self.input_password.display()
        self.button_back.display()
        self.button_done.display()

    def display_logged(self):
        self.title_logged.display()
        self.text_username.display()
        self.button_disconn.display()
        self.button_play.display()
        self.chat_logged.display()
        self.friends.display()

    def display_env(self):
        self.title_env.display()
        self.text_username.display()
        if not self.play_pushed:
            self.button_play.display()
        else:
            self.text_wating.display()
        self.button_disconn.display()
        self.button_exit.display()
        self.chat_logged.display()
        self.friends.display()
        self.teams.display()

    def display_faillog(self):
        self.display_login()
        self.text_faillog.display()
    
    def display_failsign(self):
        self.display_signup()
        self.text_failsign.display()

    def react_events_main(self, events, pressed):
        if self.button_login.pushed(events):
            self.state = 'login'
        elif self.button_signup.pushed(events):
            self.state = 'signup'
    
    def react_events_login(self, events, pressed):
        self.input_username.run(events, pressed)
        self.input_password.run(events, pressed)
        if self.button_back.pushed(events):
            self.state = 'main'
        if self.button_done.pushed(events):
            username = self.input_username.text
            password = self.input_password.text
            if self.client.log(username, password):
                self.state = 'logged'
                self.text_username.set_text(username)
                self.teams.set_username(username)
                self.chat_logged.activate()
            else:
                self.state = 'fail log'

    def react_events_signup(self, events, pressed):
        self.input_username.run(events, pressed)
        self.input_password.run(events, pressed)
        if self.button_back.pushed(events):
            self.state = 'main'
        if self.button_done.pushed(events):
            username = self.input_username.text
            password = self.input_password.text
            if self.client == 1:
                self.state = 'logged'
            else:
                if self.client.sign_up(username, password):
                    self.state = 'logged'
                    self.text_username.set_text(username)
                    self.teams.set_username(username)
                    self.chat_logged.activate()
                else:
                    self.state = 'fail sign'
                
    def react_events_logged(self, events, pressed):
        self.chat_logged.react_events(events, pressed)
        if self.button_play.pushed(events):
            print('play')
        if self.button_disconn.pushed(events):
            self.disconn()
        self.friends.react_events(events, pressed)
        # check for env 
        if self.client.in_env:
            self.teams.set_players() # must have receive players connected from server (env)
            self.state = 'env'
        
    def react_events_env(self, events, pressed):
        self.chat_logged.react_events(events, pressed)
        self.teams.react_events(events, pressed)
        if self.button_disconn.pushed(events):
            self.disconn()
        self.friends.react_events(events, pressed)
        
        if not self.play_pushed:
            if self.button_play.pushed(events):
                self.client.env_play()
                self.play_pushed = True

        if self.button_exit.pushed(events):
            self.client.quit_game_or_env()

        self.check_env_quit_players()

        if self.client.in_game_session:
            start_game(self.client)
            self.state = 'in game'

    def disconn(self):
        self.client.disconn()
        self.state = 'main'
        self.input_password.text = ''
        self.input_username.text = ''
        self.chat_logged.reset()
        self.friends.reset()
        self.teams.reset(keep_username=False)

    def run(self, events, pressed):
        if self.state == 'in game':
            if not self.client.in_game_session:
                self.play_pushed = False
                if self.client.in_env:
                    self.state = 'env'
                else:
                    self.teams.reset()
                    self.state = 'logged'
            run_game(pressed, events)
        elif self.state == 'main':
            self.display_main()
            self.react_events_main(events, pressed)
        elif self.state == 'login':
            self.display_login()
            self.react_events_login(events, pressed)
        elif self.state == 'signup':
            self.react_events_signup(events, pressed)
            self.display_signup()
        elif self.state == 'logged':
            self.display_logged()
            self.react_events_logged(events, pressed)
        elif self.state == 'env':
            self.display_env()
            self.react_events_env(events, pressed)
            if not self.client.in_env:
                self.play_pushed = False
                self.teams.reset()
                self.state = 'logged'
        elif self.state == 'fail log':
            self.display_faillog()
            self.react_events_login(events, pressed)
        elif self.state == 'fail sign':
            self.display_failsign()
            self.react_events_signup(events, pressed)
        
    def check_env_quit_players(self):
        for quit_username in self.client.quit_env_players:
            self.teams.change_team(quit_username, -1)
        self.client.quit_env_players = []