import socket
from time import sleep

HEADER = 64
PORT = 5050
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
    def __init__(self):
        self.logged = False
        self.connected = True
        self.state = 'logging'
        self.chat_msgs = []
    
    def log(self, username, password):
        
        self.send(f'log-{username}-{password}')
        
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

        self.send(f'sign-{username}-{password}')

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
            sleep(.1)
            msg = self.receive_msg()
            if msg:
                print(f'[SERVER] {msg}')
                msg = msg.split('-')
                # check to know type of msg
                if msg[0] == 'chat': # chat msg
                    username = msg[1]
                    content = msg[2]
                    self.chat_msgs.append((username, content))
                elif msg[0] == 'fr': # friend connected or disconnected
                    if msg[1] == 'conn':
                        self.fr_msgs.append((msg[2],True))
                    else:
                        self.fr_msgs.append((msg[2],False))
                elif msg[0] == 'dfr': # friend demand
                    self.fr_demands.append(msg[1])


    def send_chat_msg(self, msg):
        self.send(f'chat-{msg}')
    
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
            sleep(.1)        
            msg_length = client.recv(HEADER).decode(FORMAT)
            if msg_length:
                received = True
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)
                return msg
    
    def check_friend(self):
        for username, is_conn in self.fr_msgs:
            self.friends[username] = is_conn
        self.fr_msgs = []

    def get_demand_fr(self):
        demands = self.fr_demands
        self.fr_demands = []
        return demands

    def demand_friend(self, username):
        self.send(f'dfr-{username}')
    
    def return_friend_demand(self, username, accepted):
        self.send(f'rdfr-{username}-{accepted}')



