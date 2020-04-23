from .platform import blocks, display_cursor
from .game_menu import GameMenu
from .weapons import BulletSystem
from .score import Score

#player1 = Player(1, [100,1000], 'bob')
#player1.set_weapon(M4())
#player1.is_client = True
#
#player2 = Player(0, [2000,1000], 'alex')
#player2.set_weapon(Sniper())
#
#players = [player1, player2]
#
#Score.set_teams([player1], [player2])
#


def run(pressed, events):
    for block in blocks:
        block.display()
    
    ended = Score.check_win()
    if ended:
        Score.display_end()
    else:
        # react to communications from server
        Score.react_events()
        for player in Score.players:
            if not player.dead:
                if player.is_client:
                    player.react_events_client(pressed, events)
                player.update(Score)
                player.collisions(blocks)
                player.display()

    
    BulletSystem.update(blocks, Score.players)
    Score.display_lives()

def start_game(client):
    GameMenu.init(client, Score)
    Score.client = client

def run_game(pressed, events):
    if not GameMenu.ready:
        GameMenu.run(pressed, events)
    else:
        run(pressed, events)
    display_cursor()
