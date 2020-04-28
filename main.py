from base import Interface, InputText
from menu import Menu
from client import Client
import pygame
import sys

pygame.init()

inter = Interface()

menu = Menu(Client())

while inter.running:
    pressed, events = inter.run()

    menu.run(events, pressed)

menu.client.stop()
sys.exit()