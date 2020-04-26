from comm import send, receive_msg
import threading
from time import sleep

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
        self.in_games = [True for _ in range(self.n_clients)]
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
        self.active = False
        for client in self.clients:
            client.in_env = False
            client.in_game = False
            client.env = None
            send(client.conn, f'env|stop')
    
    def stop_game(self, username):
        index = self.usernames.index(username)
        self.in_games[index] = False

    def run(self):
        while self.active:
            # check that there is still somebody in game
            try:
                self.in_games.index(True)
            except:
                self.in_game = False
                
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
