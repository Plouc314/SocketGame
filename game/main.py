from .platform import blocks, display_cursor
from .items import ItemSystem
from .game_menu import GameMenu
from .weapons import BulletSystem
from .score import Score
from helper import timer


def run(pressed, events):
    
    # first check client player
    if not Score.ended:
        Score.client_player.react_events_client(pressed, events)
    
    for block in blocks:
        block.display()
    
    Score.display_lives()

    ItemSystem.update(Score)
    
    if Score.ended:
        Score.run_end(events, pressed)
    else:
        Score.check_win()
        # react to communications from server
        Score.react_events()
        for player in Score.players:
            if not player.dead:
                player.update()
                player.collisions(blocks)
                player.display()
    
    BulletSystem.update(blocks, Score.players)
    

def start_game(client):
    GameMenu.reset()
    Score.reset()
    GameMenu.init(client, Score)
    Score.client = client
    BulletSystem.client = client
    ItemSystem.set_client(client)
    client.ingame_quit_players = []

def run_game(pressed, events):
    if not GameMenu.ready:
        GameMenu.run(pressed, events)
    else:
        run(pressed, events)
    display_cursor()

