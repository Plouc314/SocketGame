import pygame
from numpy import mean

pygame.init()

class Dimension:
    def __init__(self, dim):
        self.window = dim
        self.center_x = int(dim[0]/2)
        self.center_y = int(dim[1]/2)
        self.center = (self.center_x, self.center_y)
        self.x = dim[0]
        self.y = dim[1]

dim = Dimension((3000,1600))

class C:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    LIGHT_BLUE = (135,206,250)
    LIGHT_GREY = (200,200,200)
    LIGHT_RED = (255, 80, 80)
    RED = (225, 50, 50)
    LIGHT_GREEN = (124,252,100)
    GREEN = (94,222,70)

class Font:
    f25 = pygame.font.SysFont("Arial", 25)
    f30 = pygame.font.SysFont("Arial", 30)
    f50 = pygame.font.SysFont("Arial", 50)
    f100 = pygame.font.SysFont("Arial", 100)

screen = pygame.display.set_mode(dim.window)
screen.fill(C.WHITE)
pygame.display.set_caption('Game')

class Form(pygame.sprite.Sprite):
    screen = screen
    MARGE_WIDTH = 4
    def __init__(self, dim, color):
        super().__init__()
        self.surf = pygame.Surface(dim)
        self.surf.fill(color)
        self.dim = dim
        self.COLOR = color
    
    def set_color(self, color, marge=False):
        self.surf.fill(color)
        self.COLOR = color
        if marge:
            self.set_highlight_color()
            self.MARGE_COLOR = self.high_color

    def set_highlight_color(self):
        light_color = []
        for i in range(3):
            if self.COLOR[i] <= 235:
                light_color.append(self.COLOR[i] + 20)
            else:
                light_color.append(255)
        dark_color = []
        for i in range(3):
            if self.COLOR[i] >= 20:
                dark_color.append(self.COLOR[i] - 20)
            else:
                dark_color.append(0)
        if mean(self.COLOR) < 130:
            self.high_color = light_color
        else:
            self.high_color = dark_color

    def display_margin(self):
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPLEFT, self.TOPRIGHT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPLEFT, self.BOTTOMLEFT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.TOPRIGHT, self.BOTTOMRIGHT, self.MARGE_WIDTH)
        pygame.draw.line(self.screen, self.MARGE_COLOR, self.BOTTOMLEFT, self.BOTTOMRIGHT, self.MARGE_WIDTH)

    def display(self, pos):
        self.screen.blit(self.surf, pos)
    
    def set_corners(self, pos, dim):
        self.TOPLEFT = pos
        self.TOPRIGHT = (pos[0]+dim[0],pos[1])
        self.BOTTOMLEFT = (pos[0], pos[1]+dim[1])
        self.BOTTOMRIGHT = (pos[0]+dim[0],pos[1]+dim[1])

def center_text(dim_box, font, text):
    width, height = font.size(text)
    if width > dim_box[0] or height > dim_box[1]:
        raise ValueError('Dimension too small for text')
    
    x_marge = int((dim_box[0] - width)/2)
    y_marge = int((dim_box[1] - height)/2)
    return x_marge, y_marge

class Cadre(Form):
    def __init__(self, dim, color, pos):
        super().__init__(dim, color)
        self.pos = pos
        self.set_corners(pos, dim)
        self.set_highlight_color()
        self.MARGE_COLOR = self.high_color

    def display(self):
        super().display(self.pos)
        self.display_margin()

class Button(Form):
    def __init__(self, dim, color, pos, text='', TEXT_COLOR=(0,0,0), centered=True, font=Font.f50):
        super().__init__(dim, color)
        self.text = text
        self.TEXT_COLOR = TEXT_COLOR
        self.pos = pos
        self.set_corners(pos, dim)
        self.highlighted = False
        self.centered = centered
        self.font = font
        self.set_highlight_color()
        self.MARGE_COLOR = self.high_color


    def on_it(self):    
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.TOPLEFT[0] and mouse_pos[0] < self.TOPRIGHT[0]:
            if mouse_pos[1] > self.TOPLEFT[1] and mouse_pos[1] < self.BOTTOMLEFT[1]:
                return True
        return False

    def pushed(self, events):
        if self.on_it():
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    return True

    def highlight(self):        
        if self.on_it():
            self.surf.fill(self.high_color)
        else:
            self.surf.fill(self.COLOR)
        
    def display(self):
        
        if self.highlighted:
            self.surf.fill(self.high_color)
        else:
            self.highlight()
        
        super().display(self.pos)
        
        self.display_margin()
        
        x_marge, y_marge = center_text(self.dim, self.font, self.text)
        if not self.centered:
            x_marge = 5
        font_text = self.font.render(self.text,True,self.TEXT_COLOR)
        self.screen.blit(font_text,(self.pos[0]+x_marge,self.pos[1]+y_marge))

class TextBox(Form):
    def __init__(self, dim, background_color, pos, text='', 
                    TEXT_COLOR=(0,0,0), centered=True, font=Font.f50, marge=False):
        super().__init__(dim, background_color)
        self.pos = pos
        self.text = text
        self.centered = centered
        self.font = font
        self.lines = text.split('\n')
        self.TEXT_COLOR = TEXT_COLOR
        self.set_corners(pos, dim)
        self.as_marge = marge
        if marge:
            self.set_highlight_color()
            self.MARGE_COLOR = self.high_color

    def set_text(self, text):
        self.text = text
        self.lines = text.split('\n')

    def display(self):
        super().display(self.pos)
        if self.as_marge:
            self.display_margin()

        # split the box in n part for n lines
        y_line = round(self.dim[1]/len(self.lines))
        for i, line in enumerate(self.lines):
            x_marge, y_marge = center_text((self.dim[0],y_line), self.font, line)
            if not self.centered:
                x_marge = 5
            font_text = self.font.render(line,True,self.TEXT_COLOR)
            self.screen.blit(font_text,(self.pos[0]+x_marge,self.pos[1]+i*y_line+y_marge))

from helper import get_pressed_key, Delayed

get_input_deco = Delayed(3)
cursor_deco = Delayed(20)

class InputText(Button):
    bool_cursor = True
    def __init__(self, dim, pos, color, TEXT_COLOR=(0,0,0), centered=False, font=Font.f30):
        super().__init__(dim, color, pos, TEXT_COLOR=TEXT_COLOR, centered=centered, font=font)
        self.active = False
    
    @get_input_deco
    def get_input(self, events, pressed):
        self.active = True
        
        # check for end active
        if pressed[pygame.K_RETURN]:
            self.active = False
            self.highlighted = False
            return False
        elif not self.on_it():
            pushed = False
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    pushed =  True 
            if pushed:
                self.active = False
                self.highlighted = False
                return False

        key = get_pressed_key(pressed)
        if key:
            self.text += key
            try:
                center_text(self.dim, self.font, self.text)
            except ValueError:
                self.text = self.text[:-1]
            return True
        
        if pressed[pygame.K_BACKSPACE]:
            self.text = self.text[:-1]
            return True
    
        return False
    
    def display_text_cursor(self):
        width, height = self.font.size(self.text)
        x_marge, y_marge = center_text(self.dim, self.font, self.text)
        if not self.centered:
            x_marge = 5

        bottom_pos = (self.TOPLEFT[0] + x_marge + width, self.BOTTOMLEFT[1]-y_marge)
        top_pos = (self.TOPLEFT[0] + x_marge + width, self.TOPLEFT[1]+y_marge)
        
        if self.bool_cursor:
            pygame.draw.line(self.screen, C.BLACK, top_pos, bottom_pos, 2)
        self.change_cursor_state()

    @cursor_deco
    def change_cursor_state(self):
        self.bool_cursor = not self.bool_cursor
        return True

    def run(self, events, pressed):
        if self.pushed(events):
            self.active = True
        
        if self.active:
            self.highlighted = True
            self.display_text_cursor()
            self.get_input(events, pressed)


class Interface:
    clock = pygame.time.Clock()
    running = True
    screen = screen

    def check_quit(self, pressed, events):
        for event in events:
            # check quit
            if event.type == pygame.QUIT:
                self.running = False
        
        if pressed[pygame.K_ESCAPE]:
            self.running = False

    def run(self):
        self.clock.tick(30)
        pygame.display.update()
        self.screen.fill(C.WHITE)
        pressed = pygame.key.get_pressed()
        events = pygame.event.get()
        self.check_quit(pressed, events)

        return pressed, events


