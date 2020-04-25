from .platform import blocks, display_cursor
from .game_menu import GameMenu
from .weapons import BulletSystem
from .score import Score
from helper import timer


def run(pressed, events):
    
    # first check client player
    Score.client_player.react_events_client(pressed, events)
    
    for block in blocks:
        block.display()
    Score.display_lives()
    
    Score.check_win()
    if Score.ended:
        Score.display_end()
    else:
        # react to communications from server
        Score.react_events()
        for player in Score.players:
            if not player.dead:
                player.update(Score)
                player.collisions(blocks)
                player.display()
    
    BulletSystem.update(blocks, Score.players)
    

def start_game(client):
    GameMenu.init(client, Score)
    Score.client = client

def run_game(pressed, events):
    if not GameMenu.ready:
        GameMenu.run(pressed, events)
    else:
        run(pressed, events)
    display_cursor()
