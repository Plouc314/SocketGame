from interface import Interface, TextBox, Button, InputText, Cadre, C, Font, Dimension, set_screen
import pygame
pygame.init()

E = lambda x: int(x*Dimension.f) 
dim = Dimension((E(3000),E(1600)))

screen = pygame.display.set_mode(dim.window)
screen.fill(C.WHITE)
pygame.display.set_caption('Game')

# icon img
icon = pygame.image.load('game/imgs/flag.png')
icon = pygame.transform.scale(icon, (E(32),E(32)))
pygame.display.set_icon(icon)

set_screen(screen)