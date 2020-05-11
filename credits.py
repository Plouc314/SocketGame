from base import TextBox, Button, InputText, Cadre, C, Font, dim, E
from helper import scale

cposx = lambda pos: (dim.center_x - int(pos[0]/2))/dim.f # will be rescaled after

DIM_TDEV = scale((3000, 100), dim.f)
POS_X = scale((cposx(DIM_TDEV), 0), dim.f)[0]

DIM_TIMG = scale((3000, 600), dim.f)


class Credits:
    text_gamename = TextBox(DIM_TDEV, C.WHITE, (POS_X, E(200)), "You can propose a name for the game! Use send.a.proposition.of.name@gmail.com")
    text_dev = TextBox(DIM_TDEV, C.WHITE, (POS_X, E(400)), 'Created, developed and designed by Plouc314')
    text_sourcecode = TextBox(DIM_TDEV, C.WHITE, (POS_X, E(600)), "Source code available on https://github.com/Plouc314/SocketGame")
    str_img = "Images credits:\nImages made by Those Icons, Freepik, Pixel Buddha\nEucalyp, photo3_idea_studio\n from www.flaticon.com"
    text_img = TextBox(DIM_TIMG, C.WHITE, (POS_X, E(800)),str_img)

    @classmethod
    def display(cls):
        cls.text_dev.display()
        cls.text_sourcecode.display()
        cls.text_gamename.display()
        cls.text_img.display()
