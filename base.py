from interface import Interface, TextBox, Button, InputText, Cadre, C, Font, Dimension, set_screen
import pygame
pygame.init()

dim = Dimension((3000,1600))

screen = pygame.display.set_mode(dim.window)
screen.fill(C.WHITE)
pygame.display.set_caption('Game')

set_screen(screen)