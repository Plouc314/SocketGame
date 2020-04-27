from comm import send, receive_msg
from interaction import Interaction
import threading
from time import sleep

class Env:
    active = True
    in_game = False
    in_game_session = False
    def __init__(self, clients, usernames):
        self.clients = list(clients)
        for client in self.clients:
            client.team = 0
        self.usernames = list(usernames)
        self.n_clients = len(self.clients)
        self.in_games = [False for _ in range(self.n_clients)]
        self.ready_players = [] # players who have chosen there weapon
        self.n_player_game_sess = 0 # players who pushed the play button
        # send to clients that there in an env
        for client in self.clients:
            usernames = self.usernames.copy()
            usernames.remove(client.username)
            usernames = '|'.join(usernames)
            send(client.conn, f'env|conn|{usernames}')
        # start thread for run func
        run_thread = threading.Thread(target=self.run)
        run_thread.start()
    
    def add_client(self, new_client):
        # send to the new client all the connect players
        usernames = self.usernames.copy()
        usernames = '|'.join(usernames)
        send(new_client.conn, f'env|conn|{usernames}')
        # send to the other client that there is a new one
        for client in self.clients:
            send(client.conn, f'env|conn|{new_client.username}')
        self.clients.append(new_client)
        new_client.team = 0
        self.usernames.append(new_client.username)
        self.n_clients += 1
        
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
            
            self.body()

    def body(self):
        sleep(0.03)
            
        msgs = self.get_frame_msgs()
        
        if self.in_game:
            self.run_in_game(msgs)
            
        elif self.in_game_session:
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
                self.in_games = [True for _ in range(self.n_clients)]
                self.in_game = True
        else:
            if self.n_player_game_sess == len(self.clients):
                self.send_play_msg()
                self.in_game_session = True

    def run_in_game(self, msgs):
        # check that there is still somebody in game
        try:
            self.in_games.index(True)
        except:
            self.in_game = False
            self.reset_game()
            
        # send msgs to clients
        msg = self.build_frame_msg(msgs)
        if msg != 'env':
            for client in self.clients:
                send(client.conn, msg)
        
        self.check_dead_players()

    def handeln_team(self, msg):
        if msg[0] == 'create':
            # create a new team
            # send to the clients that one created a team
            for client in self.clients:
                send(client.conn, f'env|team|create')

        elif msg[0] == 'change':
            username = msg[1]
            team_idx = int(msg[2])
            # send to the other clients that one changes team
            for client in self.clients:
                if client.username != username:
                    send(client.conn, f'env|team|change|{username}|{team_idx}')
                else:
                    # send the team of the user
                    client.team = team_idx


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

    def send_play_msg(self):
        for client in self.clients:
            send(client.conn, f'env|play|{client.team}')

    def reset_game(self):
        self.ready_players = []
        self.n_player_game_sess = 0
        self.in_game_session = False

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
    
    def is_play(self):
        self.n_player_game_sess += 1
