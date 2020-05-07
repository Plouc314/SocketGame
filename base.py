from interface import Interface, TextBox, Button, InputText, Cadre, C, Font, Dimension, set_screen
import pygame
pygame.init()

E = lambda x: int(x*Dimension.f) 
dim = Dimension((E(3000),E(1600)))

screen = pygame.display.set_mode(dim.window)
screen.fill(C.WHITE)
pygame.display.set_caption('Game')

# icon img - just remove default img
icon = pygame.Surface((32,32))
icon.fill(C.WHITE)
pygame.display.set_icon(icon)

set_screen(screen)