from interface import Interface, InputText
from menu import Menu
from client import Client

inter = Interface()

menu = Menu(Client())
#menu = Menu(1)

while inter.running:
    pressed, events = inter.run()

    menu.run(events, pressed)

menu.client.stop()
