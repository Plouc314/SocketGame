import pandas as pd
from comm import send
from helper import cumsum, filt

def load_user_data():
    to_list = lambda x:  x.split('|')
    data = pd.read_csv('user_data.csv', dtype='object')
    data.index = data.index.astype('int64')
    data.fillna('', inplace=True)
    data['friends'] = data['friends'].map(to_list).map(filt)
    data['demands'] = data['demands'].map(to_list).map(filt)
    data = data.astype({'kills': 'int64', 'deaths': 'int64', 'played':'int64'})
    return data

def store_user_data():
    inv_to_list = lambda x: cumsum(x, '', '|')
    store_df = Data.users.copy()
    store_df['friends'] = store_df['friends'].map(inv_to_list)
    store_df['demands'] = store_df['demands'].map(inv_to_list)
    store_df.to_csv('user_data.csv', index=False)

class Data:
    users = load_user_data()

    @classmethod
    def is_valid_username(cls, username):
        if cls.users[cls.users['username'] == username].size != 0:
            return True
        return False
    
    @classmethod
    def send_stats(cls, username, conn):
        line = Data.users[Data.users['username'] == username] 
        kills = line['kills'].values[0]
        deaths = line['deaths'].values[0]
        played = line['played'].values[0]
        send(conn, f'stats|{kills}|{deaths}|{played}')
