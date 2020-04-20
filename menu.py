from interface import TextBox, Button, InputText, Cadre, C, Font, dim
from chat import Chat
from friends import Friends

cposx = lambda pos: dim.center_x - int(pos[0]/2)

DIM_TITLE = (600,120)
POS_TITLE = (cposx(DIM_TITLE), 150)
DIM_MAIN_B = (200,100)
DIM_LI_MAIN_B = (200,80)
DIM_NB = (120,60)
DIM_TEXTBL = (150, 100)
Y_POS_TEXTBL = 400
X_POS_TEXTBL = dim.center_x - 250
DIM_LOGINP = (400,80)
X_POS_LOGINP = dim.center_x
DIM_FAILT = (400,80)
Y_POS_FAILT = 320
DIM_CHAT = (800,600)
DIM_FR = (800,500)
MARGE = 100

class Menu:
    def __init__(self, client):
        self.client = client
        self.state = 'main'
        # state main
        self.title_main = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Title', font=Font.f100)

        self.button_login = Button(DIM_MAIN_B, C.LIGHT_BLUE,
                                (cposx(DIM_MAIN_B),POS_TITLE[1]+2*DIM_MAIN_B[1]),'Log in')


        self.button_signup = Button(DIM_MAIN_B, C.LIGHT_BLUE,
                                (cposx(DIM_MAIN_B),POS_TITLE[1]+4*DIM_MAIN_B[1]),'Sign up') 

        # state login
        self.title_login = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Log in', font=Font.f100)

        self.text_logusername = TextBox(DIM_TEXTBL,C.WHITE,
                                (X_POS_TEXTBL, Y_POS_TEXTBL), 'Username:', font=Font.f30)

        self.text_password = TextBox(DIM_TEXTBL,C.WHITE,
                                (X_POS_TEXTBL, Y_POS_TEXTBL+150), 'Password:', font=Font.f30)

        self.input_username = InputText(DIM_LOGINP, (X_POS_LOGINP, Y_POS_TEXTBL),C.WHITE)
        self.input_password = InputText(DIM_LOGINP, (X_POS_LOGINP, Y_POS_TEXTBL+150),C.WHITE)
        self.button_done = Button(DIM_NB,C.LIGHT_BLUE, (dim.center_x+2*DIM_NB[0], Y_POS_TEXTBL+350), 'Done', font=Font.f30)
        self.button_back = Button(DIM_NB, C.LIGHT_BLUE, (100,100),'Back', font=Font.f30)
        # state signup
        self.title_signup = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Sign up', font=Font.f100) 
        # state fail log
        self.text_faillog = TextBox(DIM_FAILT, C.WHITE, (X_POS_TEXTBL+50, Y_POS_FAILT),
                                'Invalid username or password', font=Font.f25, TEXT_COLOR=C.RED)  
        # state fail sign
        self.text_failsign = TextBox(DIM_FAILT, C.WHITE, (X_POS_TEXTBL+50, Y_POS_FAILT),
                                'Username already taken', font=Font.f25, TEXT_COLOR=C.RED)  
        # state logged
        self.title_logged = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Welcome', font=Font.f100)
        self.text_username = TextBox(DIM_LOGINP, C.WHITE, (50, 50),'',marge=True)
        self.button_play = Button(DIM_MAIN_B, C.LIGHT_BLUE, 
                    (cposx(DIM_MAIN_B),POS_TITLE[1]+2*DIM_MAIN_B[1]), 'Play') 
        self.chat_logged = Chat(DIM_CHAT, (MARGE,dim.y-DIM_CHAT[1]-MARGE), self.client)
        self.friends = Friends(DIM_FR, (dim.x-DIM_FR[0]-MARGE, MARGE), self.client)
        self.button_disconn = Button(DIM_LI_MAIN_B, C.LIGHT_BLUE, (50, MARGE+DIM_LOGINP[1])
                        ,'Disconnect',font=Font.f30)
        # state env
        self.title_env = TextBox(DIM_TITLE, C.WHITE, POS_TITLE,'Env', font=Font.f100)

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
        self.button_disconn.display()
        self.chat_logged.display()
        self.friends.display()

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
            self.state = 'env'

    def react_events_env(self, events, pressed):
        self.chat_logged.react_events(events, pressed)
        if self.button_disconn.pushed(events):
            self.disconn()
        self.friends.react_events(events, pressed)

    def disconn(self):
        self.client.disconn()
        self.state = 'main'
        self.input_password.text = ''
        self.input_username.text = ''
        self.chat_logged.reset()
        self.friends.reset()


    def run(self, events, pressed):
        if self.state == 'main':
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
        elif self.state == 'fail log':
            self.display_faillog()
            self.react_events_login(events, pressed)
        elif self.state == 'fail sign':
            self.display_failsign()
            self.react_events_signup(events, pressed)