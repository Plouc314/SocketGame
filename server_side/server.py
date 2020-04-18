import socket 
import threading
import pandas as pd
from time import sleep
from helper import cumsum, filt

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

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
    to_list = lambda x:  x.split('-')
    data = pd.read_csv('user_data.csv', dtype='object')
    data.index = data.index.astype('int64')
    data.fillna('', inplace=True)
    data['friends'] = data['friends'].map(to_list).map(filt)
    data['demands'] = data['demands'].map(to_list).map(filt)
    return data

def store_user_data():
    inv_to_list = lambda x: cumsum(x, '', '-')
    store_df = Data.users.copy()
    store_df['friends'] = store_df['friends'].map(inv_to_list)
    store_df['demands'] = store_df['demands'].map(inv_to_list)
    store_df.to_csv('user_data.csv', index=False)

class Data:
    users = load_user_data()

class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True
        self.logged = False
        self.chat_current_msg = None
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
            self.on_log(username)
            send(self.conn, 'signed')

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
            username = Data.users.loc[int(index), 'username']
            send(self.conn, f'dfr-{username}')

    def add_friend(self, username):
        other_index = Data.users[Data.users['username'] == username].index[0]
        # add friend to data
        Data.users.loc[self.index,'friends'].append(str(other_index))
        Data.users.loc[other_index,'friends'].append(str(self.index))
        # remove other from demands
        Data.users.loc[self.index,'demands'].remove(str(other_index))
        # if other is connected, update his friends
        if Interaction.is_connected(username):
            other_client = Interaction.get_client(username)
            Interaction.manage_friends(other_client)

    def reject_demand(self, username):
        other_index = Data.users[Data.users['username'] == username].index[0]
        Data.users[Data.users['username']==self.username]['demands'].values[0].remove(str(other_index))

    def run(self):
        while self.connected:
            msg = receive_msg(self.conn)
            if msg:
                if msg == DISCONNECT_MESSAGE:
                    # disconnect
                    self.connected = False
                    Interaction.disconn_friend(self)
                    print(f"[{self.addr}] {msg}")
                    break

                if not self.logged:
                    print(f"[{self.addr}] {msg}")
                    state, username, password = msg.split('-')
                    if state == 'log':
                        self.log(username, password)
                    elif state == 'sign':
                        self.sign(username, password)
                else:
                    print(f'[{self.username}] {msg}')
                    msg = msg.split('-')
                    if msg[0] == 'chat': # chat message
                        self.chat_current_msg = msg[1]
                    elif msg[0] == 'dfr': # send a friend demand
                        self.current_demand = msg[1]
                    elif msg[0] == 'rdfr': # send answer to a friend demand
                        if msg[2] == 'True': # demand accepted
                            self.add_friend(msg[1])
                        else: # demand rejected
                            self.reject_demand(msg[1])

                    
        self.conn.close()


class Interaction:
    clients = []
    current_contents = []
    current_demands = {}

    @classmethod
    def run(cls):
        while 1:
            sleep(.1)
            
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
                        send(client.conn, 'chat-' + content[0] + '-' + content[1])
            
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
                Data.users[Data.users['username'] == requested]['demands'].values[0].append(str(index_requester))

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
            send(friend.conn, f'fr-disconn-{disc_client.username}')

    @classmethod
    def manage_friends(cls, new_client):

        friends, client_friends = cls.get_connected_friends(new_client)
        
        # send to all connected friends that the new client is connected
        for friend in friends:
            send(friend.conn, f'fr-conn-{new_client.username}')
        
        # send to new client all connected friends
        for i, is_conn in client_friends.items():
            username = Data.users.loc[int(i),'username']
            if is_conn:
                send(new_client.conn, f'fr-conn-{username}')
            else:
                send(new_client.conn, f'fr-disconn-{username}')
                
    @classmethod
    def get_connected_friends(cls, the_client):
        '''Return list [CLient] and dict [index:is_conn]'''
        index = the_client.index
        client_friends = {v:False for v in Data.users.loc[index, 'friends']}
        friends = []
        for client in cls.clients:
            if str(index) in client.friends:
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
