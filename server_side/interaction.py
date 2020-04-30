from data import Data, store_user_data
from comm import send, receive_msg
from time import sleep

class Interaction:
    clients = []
    current_contents = []
    current_demands = {}

    @classmethod
    def run(cls):
        while 1:
            sleep(.2)
            
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
                    # check for valid username
                    if Data.is_valid_username(client.current_demand):
                        cls.current_demands[client.username] = client.current_demand
                        # send to the client that the username is valid
                        send(client.conn, 'dfrv|1')
                    else:
                        # send to the client that the username is not valid
                        send(client.conn, 'dfrv|0')
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
    def inform_inenv(cls, username):
        the_client = cls.get_client(username)
        friends, _ = cls.get_connected_friends(the_client)
        for friend in friends:
            send(friend.conn, f'fr|inenv|{username}')
    
    @classmethod
    def inform_outenv(cls, username):
        the_client = cls.get_client(username)
        friends, _ = cls.get_connected_friends(the_client)
        for friend in friends:
            send(friend.conn, f'outenv|{username}')

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
