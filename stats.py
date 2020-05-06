from base import TextBox, Button, InputText, Cadre, C, Font, dim, E
from helper import scale

cposx = lambda pos: (dim.center_x - int(pos[0]/2))/dim.f # will be rescaled after

DIM_BX = E(400)
DIM_TY = E(120)
DIM_BY = E(80)
DIM_TITLE = (DIM_BX, DIM_TY)
DIM_BOX = (DIM_BX, DIM_BY)
POS_X = E(cposx((1600,0)))

class Stats:
    @classmethod
    def init(cls, client, pos_y):
        cls.client = client
        cls.pos = [POS_X, pos_y]
        cls.title_n_game = TextBox(DIM_TITLE, C.WHITE, cls.pos, 'Games played')
        cls.text_n_game = TextBox(DIM_BOX, C.WHITE, (cls.pos[0], cls.pos[1] + DIM_TY),'',font=Font.f30,marge=True)
        cls.title_n_kill = TextBox(DIM_TITLE, C.WHITE, (cls.pos[0]+DIM_BX,cls.pos[1]), 'Kills')
        cls.text_n_kill = TextBox(DIM_BOX, C.WHITE, (cls.pos[0]+DIM_BX, cls.pos[1] + DIM_TY),'',font=Font.f30,marge=True)
        cls.title_n_death = TextBox(DIM_TITLE, C.WHITE, (cls.pos[0]+2*DIM_BX,cls.pos[1]), 'Deaths')
        cls.text_n_death = TextBox(DIM_BOX, C.WHITE, (cls.pos[0]+2*DIM_BX, cls.pos[1] + DIM_TY),'',font=Font.f30,marge=True)
        cls.title_ratio = TextBox(DIM_TITLE, C.WHITE, (cls.pos[0]+3*DIM_BX,cls.pos[1]), 'K/D')
        cls.text_ratio = TextBox(DIM_BOX, C.WHITE, (cls.pos[0]+3*DIM_BX, cls.pos[1] + DIM_TY),'',font=Font.f30,marge=True)
    
    @classmethod
    def set_stats(cls):
        # set text
        cls.text_n_game.set_text(str(cls.client.stats['played']))
        kills = cls.client.stats['kills']
        cls.text_n_kill.set_text(str(kills))
        deaths = cls.client.stats['deaths']
        cls.text_n_death.set_text(str(deaths))
        try:
            ratio = kills/deaths
        except: ratio = kills # if division by 0
        cls.text_ratio.set_text(f'{ratio:.1f}')

    @classmethod
    def display(cls):
        cls.title_n_game.display()
        cls.text_n_game.display()
        cls.title_n_kill.display()
        cls.text_n_kill.display()
        cls.title_n_death.display()
        cls.text_n_death.display()
        cls.title_ratio.display()
        cls.text_ratio.display()





        
