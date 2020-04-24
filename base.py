from interface import Interface, TextBox, Button, InputText, Cadre, C, Font, Dimension, set_screen
import pygame
pygame.init()

dim = Dimension((2400,1280)) #(3000,1600))
Font.init(dim.f)

screen = pygame.display.set_mode(dim.window)
screen.fill(C.WHITE)
pygame.display.set_caption('Game')

set_screen(screen)