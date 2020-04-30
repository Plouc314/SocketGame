import socket 
import threading
import pandas as pd
from time import sleep
from interaction import Interaction
from client import Client, clients
from env import Env

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

        
chat_thread = threading.Thread(target=Interaction.run)
chat_thread.start()


print("[STARTING] server is starting...")
start()
