from base import TextBox, InputText, Button, C, Font, dim
import pygame
from helper import cumsum, scale
from threading import Thread

E = lambda x: int(x*dim.f) 
DIM_B = scale((120,80), dim.f)

class Chat:
    msgs = []
    MAX_MSG = 8
    def __init__(self, dim, pos, client):
        self.pos = pos
        self.text_box = TextBox((dim[0], dim[1]-E(80)), C.WHITE, pos, marge=True, centered=False, font=Font.f30)
        self.input_text = InputText((dim[0]-E(120), E(80)), (pos[0], pos[1]+dim[1]-E(80)),C.WHITE, font=Font.f30)
        self.button_send = Button(DIM_B, C.LIGHT_BLUE, (pos[0]+dim[0]-E(120), pos[1]+dim[1]-E(80)),'Send',font=Font.f30)

        self.client = client

    def activate(self):
        self.client_thread = Thread(target=self.client.loop_msg)
        self.client_thread.start()

    def reset(self):
        self.msgs = []

    def display(self):
        self.text_box.display()
        self.input_text.display()
        self.button_send.display()
    
    def add_msg(self, username, msg):
        if len(self.msgs) == self.MAX_MSG:
            self.msgs.pop(0)
        
        new_msg = f'{username}: {msg}'
        self.msgs.append(new_msg)

        text = ['\n' for i in range(self.MAX_MSG-1)]
        text.insert(0, self.msgs[0])
        for i in range(len(self.msgs)-1):
            text[i+1] += self.msgs[i+1]

        new_text = cumsum(text, '')
        self.text_box.set_text(new_text)

    def react_events(self, events, pressed):
        self.input_text.run(events, pressed)
        if self.button_send.pushed(events):
            msg = self.input_text.content
            self.input_text.content = ''
            self.client.send_chat_msg(msg)
            self.add_msg(self.client.username, msg)
            
        
        for content in self.client.chat_msgs:
            self.add_msg(content[0], content[1])
        self.client.chat_msgs = []
    
        
        

            
