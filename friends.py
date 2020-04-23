from base import TextBox, InputText, Button, Cadre, C, Font
import pygame

DIM_DFR_B = (100,60)

class FriendDemand:
    def __init__(self, x_dim, pos, username):
        self.pos = pos
        self.username = username
        text = f'Friend demand: {username}'
        self.text = TextBox((x_dim-200,60),C.LIGHT_GREY,pos,text,font=Font.f30)
        self.button_yes = Button(DIM_DFR_B,C.LIGHT_GREEN,(pos[0]+x_dim-200,pos[1]),'Yes',font=Font.f30)
        self.button_no = Button(DIM_DFR_B,C.LIGHT_RED,(pos[0]+x_dim-100,pos[1]),'No',font=Font.f30)

    def display(self):
        self.text.display()
        self.button_yes.display()
        self.button_no.display()

class Invitation:
    def __init__(self, x_dim, pos, username):
        self.pos = pos
        self.username = username
        text = f'Invitation from: {username}'
        self.text = TextBox((x_dim-200,60),C.LIGHT_GREY,pos,text,font=Font.f30)
        self.button_yes = Button(DIM_DFR_B,C.LIGHT_GREEN,(pos[0]+x_dim-200,pos[1]),'Yes',font=Font.f30)
        self.button_no = Button(DIM_DFR_B,C.LIGHT_RED,(pos[0]+x_dim-100,pos[1]),'No',font=Font.f30)

    def display(self):
        self.text.display()
        self.button_yes.display()
        self.button_no.display()

class Friend:
    CTEXT = C.GREEN
    CBUTTON = C.LIGHT_GREEN
    def __init__(self, dim, pos, username, connected):
        self.pos = pos
        self.username = username
        self.connected = connected
        self.set_colors()
        self.text = TextBox((int(5/8*dim[0]),dim[1]),self.CTEXT, pos, username, font=Font.f30,marge=True)
        self.button_invite = Button((int(1/4*dim[0]),dim[1]),self.CBUTTON,
                            (pos[0]+int(5/8*dim[0]),pos[1]),'Invite',font=Font.f30)
        self.button_delete = Button((int(1/8*dim[0]),dim[1]),C.LIGHT_GREY,
                            (pos[0]+int(7/8*dim[0]),pos[1]),'Del',font=Font.f30)


    def set_colors(self):
        if self.connected:
            self.CTEXT = C.GREEN
            self.CBUTTON = C.LIGHT_GREEN
        else:
            self.CTEXT = C.RED
            self.CBUTTON = C.LIGHT_RED

    def display(self):
        self.set_colors()
        self.text.set_color(self.CTEXT, marge=True)
        self.button_invite.set_color(self.CBUTTON, marge=True)
        self.text.display()
        self.button_invite.display()
        self.button_delete.display()

NORMAL = 0
ADD_FR = 1
DIM_B = (120,60)

class Friends:
    state = NORMAL
    decal_y = 0
    fr_demands = []
    invs = []
    def __init__(self, dim, pos, client):
        self.dim = dim
        self.pos = (pos[0],pos[1]+60) # update pos to don't care about 'add friend' button
        self.client = client
        self.usernames = []
        self.obj_friends = []
        self.DIM_FR = (dim[0],60)
        self.cadre = Cadre((dim[0],dim[1]-60), C.WHITE, (pos[0],pos[1]+60))
        # state normal
        self.button_add = Button((200,60),C.LIGHT_BLUE,
            (pos[0]+dim[0]-200,pos[1]),'Add friend',font=Font.f30)
        # state add fr
        POS_TEXT = (self.pos[0]+20,self.pos[1]+40)
        self.text_add = TextBox((400,80),C.WHITE, POS_TEXT,
                    'Send demand to someone',font=Font.f30)
        self.textin_add = TextBox((300, 80), C.WHITE, (POS_TEXT[0],POS_TEXT[1]+100),
                    'Enter username:',font=Font.f30)
        self.input_add = InputText((400, 80), (POS_TEXT[0]+300,POS_TEXT[1]+100),C.WHITE)
        self.button_done = Button(DIM_B, C.LIGHT_BLUE, 
                    (self.pos[0]+self.dim[0]-140,self.pos[1]+self.dim[1]-140),'Done',font=Font.f30)
        self.button_cancel = Button(DIM_B, C.LIGHT_BLUE, 
                    (self.pos[0]+20,self.pos[1]+self.dim[1]-140),'Cancel',font=Font.f30)
        

    def add_friend(self, username, connected):
        i = len(self.obj_friends)
        new_friend = Friend(self.DIM_FR,(self.pos[0],self.pos[1]+i*60),username, connected)
        self.obj_friends.append(new_friend)

    def check_connected(self):
        self.client.check_friend()
        # check for connected/disconnected friends
        for username, is_conn in self.client.friends.items():
            if username in self.usernames:
                index = self.usernames.index(username)
                self.obj_friends[index].connected = is_conn
            else:
                self.usernames.append(username)
                self.add_friend(username, is_conn)
        
        # get potential new friends demands
        new_friend_demands = self.client.get_demand_fr()
        for fr_d in new_friend_demands:
            current_fr_d = FriendDemand(self.dim[0],
                    (self.pos[0],self.decal_y*60+self.pos[1]+self.dim[1]-60),fr_d)
            self.decal_y += 1
            self.fr_demands.append(current_fr_d)
        
        # if a friend deleted you, reset friend
        if self.client.get_del_friend():
            self.obj_friends = []
            self.usernames = []
        
        # get potential invitation from friends
        for username in self.client.get_invs():
            new_inv = Invitation(self.dim[0],
                    (self.pos[0],self.decal_y*60+self.pos[1]+self.dim[1]-60),username)
            self.decal_y += 1
            self.invs.append(new_inv)


    def react_events(self, events, pressed):
        self.check_connected()
        if self.state == NORMAL:
            self.react_events_normal(events, pressed)
        elif self.state == ADD_FR:
            self.react_events_addfr(events, pressed)

    def react_events_normal(self, events, pressed):
        self.react_events_frd(events, pressed)
        self.react_events_invs(events, pressed)
        if self.button_add.pushed(events):
            self.state = ADD_FR
        for friend in self.obj_friends:
            if friend.button_delete.pushed(events):
                self.del_friend(friend)
            if friend.button_invite.pushed(events):
                self.client.invite_friend(friend.username)

    def react_events_addfr(self, events, pressed):
        self.input_add.run(events, pressed)
        if self.button_cancel.pushed(events):
            self.state = NORMAL
            self.input_add.text = ''
        if self.button_done.pushed(events):
            username = self.input_add.text
            self.client.demand_friend(username)
            self.state = NORMAL

    def react_events_frd(self, events, pressed):
        for frd in self.fr_demands:
            if frd.button_yes.pushed(events):
                self.client.return_friend_demand(frd.username,True)
                self.fr_demands.remove(frd)
                self.decal_y -= 1
            if frd.button_no.pushed(events):
                self.client.return_friend_demand(frd.username,False)
                self.fr_demands.remove(frd)
                self.decal_y -= 1

    def react_events_invs(self, events, pressed):
        for inv in self.invs:
            if inv.button_yes.pushed(events):
                self.client.return_inv_fr(inv.username)
                self.invs.remove(inv)
                self.decal_y -= 1
            if inv.button_no.pushed(events):
                self.invs.remove(inv)
                self.decal_y -= 1

    def del_friend(self, friend):
        self.obj_friends = []
        self.usernames = []
        self.client.del_friend(friend.username)

    def reset(self):
        self.usernames = []
        self.obj_friends = []
        self.fr_demands = []

    def display(self):
        self.cadre.display()
        if self.state == NORMAL:
            self.display_normal()
        elif self.state == ADD_FR:
            self.display_addfr()

    def display_normal(self):
        self.button_add.display()
        for friend in self.obj_friends:
            friend.display()
        
        for frd in self.fr_demands:
            frd.display()
        
        for inv in self.invs:
            inv.display()
        
    def display_addfr(self):
        self.text_add.display()
        self.textin_add.display()
        self.input_add.display()
        self.button_done.display()
        self.button_cancel.display()
    
    def get_obj_friend(self, username):
        for obj in self.obj_friends:
            if obj.username == username:
                return obj
