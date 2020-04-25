import socket 
import threading
import pandas as pd
from time import sleep
from helper import cumsum, filt, timer

HEADER = 64
PORT = 5050 #44778 
SERVER = ''#socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(ADDR)
except:
    print('Port already used')
    quit()

clients = []

def receive_msg(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        return msg
    return False

def send(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        
        new_client = Client(conn, addr)
        clients.append(new_client)
        thread = threading.Thread(target=new_client.run)
        thread.start()
        
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")

def load_user_data():
    to_list = lambda x:  x.split('|')
    data = pd.read_csv('user_data.csv', dtype='object')
    data.index = data.index.astype('int64')
    data.fillna('', inplace=True)
    data['friends'] = data['friends'].map(to_list).map(filt)
    data['demands'] = data['demands'].map(to_list).map(filt)
    return data

def store_user_data():
    inv_to_list = lambda x: cumsum(x, '', '|')
    store_df = Data.users.copy()
    store_df['friends'] = store_df['friends'].map(inv_to_list)
    store_df['demands'] = store_df['demands'].map(inv_to_list)
    store_df.to_csv('user_data.csv', index=False)

class Data:
    users = load_user_data()

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
            Interaction.envs.append(self.env)
            other_client.env = self.env
            other_client.in_env = True
            self.in_env = True

    def when_play(self):
        # send team to player
        send(self.conn, f'env|team|{self.team}')

    def run(self):
        while self.connected:
            msg = receive_msg(self.conn)
            if msg:
                
                if not self.logged:
                    print(f"[{self.addr}] {msg}")
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
                            self.when_play()
                        elif msg[1] == 'dead':
                            self.game_dead_players[msg[2]] = 5 # lifetime of the information in frame
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
                        self.create_env(msg[1])

                if msg == DISCONNECT_MESSAGE:
                    # disconnect
                    if self.in_env:
                        self.env.clients.remove(self)
                        print('stop env')
                        self.env.stop()
                    self.connected = False
                    if self.logged:
                        Interaction.disconn_friend(self)
                    clients.remove(self)
                    print(f"[{self.addr}] {msg}")
                    break

                    
        self.conn.close()

class Env:
    active = True
    in_game = False
    def __init__(self, clients, usernames):
        self.clients = list(clients)
        ### TEMPORARY ###
        self.clients[0].team = 0
        self.clients[1].team = 1
        ###
        self.usernames = list(usernames)
        self.n_clients = len(self.clients)
        self.ready_players = []
        # send to clients that there in an env
        for client in self.clients:
            usernames = self.usernames.copy()
            usernames.remove(client.username)
            usernames = '|'.join(usernames)
            send(client.conn, f'env|conn|{usernames}')
        # start thread for run func
        run_thread = threading.Thread(target=self.run)
        run_thread.start()
    
    def stop(self):
        print('stopping...')
        self.active = False
        for client in self.clients:
            send(client.conn, f'env|stop')

    def run(self):
        while self.active:
            self.body()

    def body(self):
        sleep(0.03)
            
        msgs = self.get_frame_msgs()
        
        if self.in_game:
            # send msgs to clients
            msg = self.build_frame_msg(msgs)
            if msg != 'env':
                for client in self.clients:
                    send(client.conn, msg)
            
            self.check_dead_players()
            
        else:
            for username, current_msgs in msgs.items():
                if current_msgs:
                    if current_msgs[0] == 'ready':
                        weapon = current_msgs[1]
                        char = current_msgs[2]
                        team = current_msgs[3]
                        for client in self.clients:
                            if username != client.username:
                                send(client.conn, f'env|ready|{username}|{weapon}|{char}|{team}')
                        d = {'username':username,'weapon':weapon,'char':char,'team':team}
                        self.ready_players.append(d)
            
            if len(self.ready_players) == len(self.clients):
                self.in_game = True

    def check_dead_players(self):
        # check for dead player
        dead_players = {}
        info_to_pop = []
        for client in self.clients:
            for username in client.game_dead_players.keys():
                if not username in dead_players.keys():
                    dead_players[username] = 1
                else:
                    dead_players[username] += 1
                # reduce lifetime of infos
                client.game_dead_players[username] -= 1
                if client.game_dead_players[username] == 0:
                    info_to_pop.append([client, username])
        
        for client, username in info_to_pop:
            client.game_dead_players.pop(username)

        # if every player send death -> confirm death
        for username, n_msg in dead_players.items():
            if n_msg == self.n_clients:
                for client in self.clients:
                    send(client.conn, f'env|dead|{username}')
                    try:
                        client.game_dead_players.pop(username)
                    except: pass


    def get_frame_msgs(self):
        msgs = {}
        # get clients msgs
        for client in self.clients:
            if client.env_msgs:
                msgs[client.username] = client.env_msgs
                client.env_msgs = None
        return msgs
    
    def build_frame_msg(self, msgs):
        msg = 'env'
        for username, current_msgs in msgs.items():
            current_msg = f'u|{username}|' + '|'.join(current_msgs)
            msg += '|'+current_msg
        return msg  


class Interaction:
    clients = []
    current_contents = []
    current_demands = {}
    envs = []

    @classmethod
    def run(cls):
        while 1:
            sleep(.5)
            
            # check that clients are connected
            for client in cls.clients:
                if not client.connected:
                    cls.clients.remove(client)

            # collect messages from clients
            for client in cls.clients:
                if client.chat_current_msg:
                    content = (client.username, client.chat_current_msg)
                    cls.current_contents.append(content)
                    client.chat_current_msg = None

            # send messages to clients
            for client in cls.clients:
                for content in cls.current_contents:
                    if content[0] != client.username:
                        send(client.conn, 'chat|' + content[0] + '|' + content[1])
            
            # empties the messages list
            cls.current_contents = []
    
            # collect fr demand from clients
            for client in cls.clients:
                if client.current_demand:
                    cls.current_demands[client.username] = client.current_demand
                    client.current_demand = None
            
            # send demands to clients
            for requester, requested in cls.current_demands.items():
                # update data
                index_requester = Data.users[Data.users['username'] == requester].index[0]
                Data.users[Data.users['username'] == requested]['demands'].values[0].append(index_requester)

                if cls.is_connected(requested):
                    current_client = cls.get_client(requested)
                    current_client.look_for_fr_request()
            
            # empties the demands dictionnary
            cls.current_demands = {}

            store_user_data()


    @classmethod
    def disconn_friend(cls, disc_client):

        friends, _ = cls.get_connected_friends(disc_client)

        # send to all connected friends that the new client is disconnected
        for friend in friends:
            send(friend.conn, f'fr|disconn|{disc_client.username}')
        
        # remove client from Interaction
        try:
            cls.clients.remove(disc_client)
        except: pass

    @classmethod
    def manage_friends(cls, new_client):

        friends, client_friends = cls.get_connected_friends(new_client)
        
        # send to all connected friends that the new client is connected
        for friend in friends:
            send(friend.conn, f'fr|conn|{new_client.username}')
        
        # send to new client all connected friends
        for i, is_conn in client_friends.items():
            username = Data.users.loc[i,'username']
            if is_conn:
                send(new_client.conn, f'fr|conn|{username}')
            else:
                send(new_client.conn, f'fr|disconn|{username}')
                
    @classmethod
    def get_connected_friends(cls, the_client):
        '''Return list [CLient] and dict [index:is_conn]'''
        index = the_client.index
        client_friends = {v:False for v in Data.users.loc[index, 'friends']}
        friends = []
        for client in cls.clients:
            if index in client.friends:
                friends.append(client)
                client_friends[client.index] = True
        return friends, client_friends
                
    @classmethod
    def is_connected(cls, username):
        for client in cls.clients:
            if client.username == username:
                return True
    
    @classmethod
    def get_client(cls, username):
        for client in cls.clients:
            if client.username == username:
                return client

interaction = Interaction()

        
chat_thread = threading.Thread(target=Interaction.run)
chat_thread.start()


print("[STARTING] server is starting...")
start()
