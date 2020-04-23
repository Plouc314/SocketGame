import socket
from time import sleep

HEADER = 64
PORT = 44778 #5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '127.0.1.1'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

    

class Client:
    client = client
    fr_msgs = []
    fr_demands = []
    friends = {}
    ready_users = []
    game_msgs = []
    invs = []
    is_del_fr = False
    in_env = False
    env_users = None
    in_game = False
    def __init__(self):
        self.logged = False
        self.connected = True
        self.state = 'logging'
        self.chat_msgs = []
    
    def log(self, username, password):
        
        self.send(f'log|{username}|{password}')
        
        # wait for response
        response = self.receive_msg()
        print(f'[SERVER] {response}')
        if response == 'logged':
            self.logged = True
            self.username = username
            return True
        else:
            return False
    
    def sign_up(self, username, password):

        self.send(f'sign|{username}|{password}')

        # wait for response
        response = self.receive_msg()
        if response == 'signed':
            self.logged = True
            self.username = username
            return True
        elif response == 'taken':
            return False

    def stop(self):
        self.logged = False
        self.connected = False
        self.send(DISCONNECT_MESSAGE)

    def loop_msg(self):
        while self.logged:
            msg = self.receive_msg()
            if msg:
                if not self.in_game:
                    print(f'[SERVER] {msg}')
                msg = msg.split('|')
                # check to know type of msg
                if msg[0] == 'chat': # chat msg
                    username = msg[1]
                    content = msg[2]
                    self.chat_msgs.append((username, content))
                elif msg[0] == 'disconn':
                    break
                elif msg[0] == 'fr': # friend connected or disconnected
                    if msg[1] == 'conn':
                        self.fr_msgs.append((msg[2],True))
                    else:
                        self.fr_msgs.append((msg[2],False))
                elif msg[0] == 'dfr': # friend demand
                    self.fr_demands.append(msg[1])
                elif msg[0] == 'delfr': # a friend delete self (you)
                    self.friends.pop(msg[1])
                    self.is_del_fr = True
                elif msg[0] == 'inv':
                    self.invs.append(msg[1])
                # env msgs
                elif msg[0] == 'env':
                    if not self.in_game:
                        if msg[1] == 'conn':
                            self.in_env = True
                            self.env_users = msg[2:]
                            self.n_env_users = len(self.env_users) + 1
                        elif msg[1] == 'ready':
                            self.ready_users.append({'username':msg[2],'weapon':msg[3],'char':int(msg[4]),'team':int(msg[5])})
                        elif msg[1] == 'team':
                            self.team = int(msg[2])
                    else:
                        username = msg[1]
                        angle = float(msg[2])
                        fire = int(msg[3])
                        left = int(msg[4])
                        right = int(msg[5])
                        jump = int(msg[6])
                        self.game_msgs.append({'username':username, 'angle':angle, 'fire':fire, 'left':left, 'right':right, 'jump':jump})

    def send_chat_msg(self, msg):
        self.send(f'chat|{msg}')
    
    def send(self,msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

    def receive_msg(self):
        received = False
        while not received and self.connected:        
            msg_length = client.recv(HEADER).decode(FORMAT)
            if msg_length:
                received = True
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)
                return msg
    
    def disconn(self):
        self.logged = False
        self.friends = {}
        self.fr_demands = []
        self.fr_msgs = []
        self.send('disconn')

    def check_friend(self):
        for username, is_conn in self.fr_msgs:
            self.friends[username] = is_conn
        self.fr_msgs = []

    def del_friend(self, username):
        self.friends.pop(username)
        self.send(f'delfr|{username}')

    def get_invs(self):
        invs = self.invs
        self.invs = []
        return invs

    def get_del_friend(self):
        is_del_fr = self.is_del_fr
        self.is_del_fr = False
        return is_del_fr

    def get_demand_fr(self):
        demands = self.fr_demands
        self.fr_demands = []
        return demands

    def invite_friend(self, username):
        self.send(f'inv|{username}')

    def return_inv_fr(self, username):
        self.send(f'rinv|{username}')

    def demand_friend(self, username):
        self.send(f'dfr|{username}')
    
    def return_friend_demand(self, username, accepted):
        self.send(f'rdfr|{username}|{accepted}')

    def env_play(self):
        self.send(f'env|play')

    def env_ready(self, weapon, char):
        self.send(f'env|ready|{weapon}|{char}|{self.team}')
    
    def env_game(self, angle, fire, left, right, jump):
        self.send(f'env|{self.username}|{angle:.2f}|{fire}|{left}|{right}|{jump}')
