from comm import send, receive_msg
from interaction import Interaction
import threading
from random import choice
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
    
    def quit_game(self, username):
        index = self.usernames.index(username)
        self.in_games[index] = False
        # send to client that one quit game
        for client in self.clients:
            if client.username != username:
                send(client.conn, f'env|quitgame|{username}')

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
        
        self.check_hit_player()
        self.check_dead_players()
        self.check_items()

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

    def check_items(self):
        to_pop = []
        count_info = {} # count to see if each players send the info
        for client in self.clients:
            for mix in client.game_items.keys():
                # check type of item
                if 'health' in mix:
                    if not mix in count_info.keys():
                        count_info[mix] = {'count':1,'pos_idx':client.game_items[mix]['pos_idx']}
                    else:
                        count_info[mix]['count'] += 1
                # reduce lifetime of infos
                client.game_items[mix]['life'] -= 1
                if client.game_items[mix]['life'] == 0:
                    to_pop.append([client, mix])
        
        for client, mix in to_pop:
            client.game_items.pop(mix)
            send(client.conn, f'env|item|{mix}|0|0') # second zero means nothing (but has to be there for in the case where it's confirmed)

        
        # if every players send item -> confirm item
        for mix, info in count_info.items():
            if info['count'] == self.n_clients:
                # set new pos idx
                available_idx = [0,1,2]
                available_idx.remove(info['pos_idx'])
                new_pos_idx = choice(available_idx)
                for client in self.clients:
                    send(client.conn, f'env|item|{mix}|1|{new_pos_idx}') # 1 for confirmed
                    try:
                        client.game_items.pop(mix)
                    except: pass

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

    def check_hit_player(self):
        # check for hit player
        hit_players = {}
        info_to_pop = []
        for client in self.clients:
            for username, info in client.game_hit_players.items():
                if not username in hit_players.keys():
                    hit_players[username] = {'count':1,'damage': info['damage']}
                else:
                    hit_players[username]['count'] += 1
                # reduce lifetime of infos
                client.game_hit_players[username]['life'] -= 1
                if client.game_hit_players[username]['life'] == 0:
                    info_to_pop.append([client, username])
        
        for client, username in info_to_pop:
            client.game_hit_players.pop(username)

        # if every player send death -> confirm death
        for username, info in hit_players.items():
            if info['count'] == self.n_clients:
                for client in self.clients:
                    damage = info['damage']
                    send(client.conn, f'env|hit|{username}|{damage}')
                    try:
                        client.game_hit_players.pop(username)
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
    
    def quit(self, username):
        client = Interaction.get_client(username)
        # update client attributes
        client.in_env = False
        client.env = None
        send(client.conn, f'env|stop')
        # send to friends: out env
        Interaction.inform_outenv(client.username)
        # update env attributes
        self.clients.remove(client)
        self.usernames.remove(username)
        self.n_clients -= 1
        # check if there is still someone
        if self.n_clients == 0:
            self.active = False
        else:
            # inform other user in env
            for client in self.clients:
                send(client.conn, f'env|quit|{username}')

    def is_play(self):
        self.n_player_game_sess += 1
