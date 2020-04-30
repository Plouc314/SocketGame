from interaction import Interaction
from env import Env
from comm import send, receive_msg
from data import Data, store_user_data
from time import sleep

DISCONNECT_MESSAGE = "!DISCONNECT"
VERSION = '1.1'

clients = []

class Client:
    in_env = False
    team = None
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True
        self.logged = False
        self.chat_current_msg = None
        self.env_msgs = None
        self.game_dead_players = {}
        self.current_demand = None
        self.current_pos = None
    
    def log(self, username, password):
        # check for valide username and password
        select_name_index = Data.users[Data.users['username'] == username].index
        if len(select_name_index) == 0:
            send(self.conn, 'false')
            return
        index = select_name_index[0]
        if Data.users.iloc[index,1] == password.strip():
            send(self.conn, 'logged')
            sleep(.1) # let the time to the client to start the separated thread
            self.on_log(username)
        else:
            send(self.conn, 'false')

    def sign(self, username, password):
        select_name_index = Data.users[Data.users['username'] == username].index
        if len(select_name_index) != 0:
            send(self.conn, 'taken')
            return
        else:
            Data.users = Data.users.append({'username':username,'password':password.strip(),'friends':[],'demands':[]}, ignore_index=True)
            store_user_data()
            send(self.conn, 'signed')
            sleep(.1) # let the time to the client to start the separated thread
            self.on_log(username)
            
    def on_log(self, username):
        self.logged = True
        Interaction.clients.append(self)
        self.username = username
        line = Data.users[Data.users['username'] == username]
        self.friends = line['friends'].values[0]
        self.index = line.index[0]
        Interaction.manage_friends(self)
        self.look_for_fr_request()

    def look_for_fr_request(self):
        demands = Data.users[Data.users['username'] == self.username]['demands'].values[0]
        for index in demands:
            username = Data.users.loc[index, 'username']
            send(self.conn, f'dfr|{username}')

    def add_friend(self, username):
        other_index = Data.users[Data.users['username'] == username].index[0]
        # add friend to data
        Data.users.loc[self.index,'friends'].append(other_index)
        Data.users.loc[other_index,'friends'].append(self.index)
        # remove other from demands
        Data.users.loc[self.index,'demands'].remove(other_index)
        store_user_data()
        Interaction.manage_friends(self)
        # if other is connected, update his friends
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            Interaction.manage_friends(other_client)

    def del_friend(self, username):
        # update data
        other_index = Data.users[Data.users['username'] == username].index[0]
        Data.users.loc[self.index, 'friends'].remove(other_index)
        Data.users.loc[other_index, 'friends'].remove(self.index)
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            send(other_client.conn, f'delfr|{self.username}')

    def reject_demand(self, username):
        other_index = Data.users[Data.users['username'] == username].index[0]
        Data.users[Data.users['username']==self.username]['demands'].values[0].remove(other_index)

    def invite_friend(self, username):
        # check if friend is conn
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            send(other_client.conn, f'inv|{self.username}')

    def create_env(self, username):
        # check other is conn
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            self.env = Env((self, other_client),(self.username, other_client.username))
            other_client.env = self.env
            Interaction.inform_inenv(other_client.username)
            other_client.in_env = True
            self.in_env = True

    def check_env_rinv(self, username):
        # check other is conn
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            # check if other client is already in env
            if other_client.in_env:
                other_client.env.add_client(self)
                self.in_env = True
                self.env = other_client.env
            else:
                self.create_env(username)
            Interaction.inform_inenv(self.username)

    def run(self):
        while self.connected:
            msg = receive_msg(self.conn)
            if msg:
                
                if msg == DISCONNECT_MESSAGE:
                        # disconnect
                        if self.in_env:
                            if self.env.in_game:
                                self.env.stop_game(self.username)
                            else:
                                self.env.quit(self.username)
                        self.connected = False
                        if self.logged:
                            Interaction.disconn_friend(self)
                        print(f"[{self.addr}] {msg}")
                        break

                if not self.logged:
                    print(f"[{self.addr}] {msg}")
                    # update file asking for the game version: to update game if needed
                    if msg == 'version': 
                        send(self.conn, VERSION)
                    else:
                        state, username, password = msg.split('|')
                        if state == 'log':
                            self.log(username, password)
                        elif state == 'sign':
                            self.sign(username, password)
                else:
                    if self.in_env:
                        if not self.env.in_game:
                            print(f'[{self.username}] {msg}')
                    else:
                        print(f'[{self.username}] {msg}')
    
                    msg = msg.split('|')
                    # env msg 
                    if msg[0] == 'env':
                        if msg[1] == 'play':
                            self.env.is_play()
                        elif msg[1] == 'quit':
                            if self.env.in_game:
                                self.env.stop_game(self.username) # quit game
                            else:
                                self.env.quit(self.username) # quit env
                        elif msg[1] == 'dead':
                            self.game_dead_players[msg[2]] = 5 # lifetime of the information in frame
                        elif msg[1] == 'team':
                            self.env.handeln_team(msg[2:])
                        elif msg[1] == 'pos':
                            self.current_pos = [int(msg[2]),int(msg[3])]
                        else:
                            self.env_msgs = msg[1:]
                    elif msg[0] == 'disconn':
                        Interaction.disconn_friend(self)
                        self.logged = False
                        # send to client to interrupt inf loop
                        send(self.conn, 'disconn') 
                    # chat message
                    elif msg[0] == 'chat': 
                        self.chat_current_msg = msg[1]
                    # send a friend demand
                    elif msg[0] == 'dfr': 
                        self.current_demand = msg[1]
                    # send answer to a friend demand
                    elif msg[0] == 'rdfr':
                        if msg[2] == 'True': # demand accepted
                            self.add_friend(msg[1])
                        else: # demand rejected
                            self.reject_demand(msg[1])
                    # send delete a friend
                    elif msg[0] == 'delfr': 
                        self.del_friend(msg[1])
                    # invite a friend
                    elif msg[0] == 'inv':
                        self.invite_friend(msg[1])
                    # get answer of invitation
                    elif msg[0] == 'rinv':
                        self.check_env_rinv(msg[1])

        self.conn.close()
        # remove (thus delete) client from clients list
        clients.remove(self)