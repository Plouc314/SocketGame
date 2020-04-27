import pygame

pygame.init()

def mean(array):
    total = 0
    for v in array:
        total += v
    return total/len(array)

def set_screen(screen):
    TextBox.screen = screen
    Button.screen = screen
    InputText.screen = screen
    Cadre.screen = screen
    Interface.screen = screen

class Dimension:
    f = 1
    def __init__(self, dim):
        self.window = dim
        self.center_x = int(dim[0]/2)
        self.center_y = int(dim[1]/2)
        self.center = (self.center_x, self.center_y)
        self.x = dim[0]
        self.y = dim[1]

E = lambda x: int(x * Dimension.f)

screen = None

class C:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    LIGHT_BLUE = (135,206,250)
    BLUE = (65,105,225)
    DARK_BLUE = (7, 19, 134)
    LIGHT_GREY = (200,200,200)
    XLIGHT_GREY = (230,230,230)
    LIGHT_RED = (255, 80, 80)
    RED = (225, 50, 50)
    LIGHT_GREEN = (124,252,100)
    GREEN = (94,222,70)
    DARK_GREEN = (17, 159, 26)
    LIGHT_BROWN = (225, 167, 69)
    DARK_PURPLE = (140, 17, 159)
    PURPLE = (180, 57, 199)

class Font:
    f25 = pygame.font.SysFont("Arial", E(25))
    f30 = pygame.font.SysFont("Arial", E(30))
    f50 = pygame.font.SysFont("Arial", E(50))
    f70 = pygame.font.SysFont("Arial", E(70))
    f100 = pygame.font.SysFont("Arial", E(100))
    @classmethod
    def init(cls, factor):
        cls.f25 = pygame.font.SysFont("Arial", int(25*factor))
        cls.f30 = pygame.font.SysFont("Arial", int(30*factor))
        cls.f50 = pygame.font.SysFont("Arial", int(50*factor))
        cls.f70 = pygame.font.SysFont("Arial", int(70*factor))
        cls.f100 = pygame.font.SysFont("Arial", int(100*factor))



class Form(pygame.sprite.Sprite):
    screen = screen
    MARGE_WIDTH = E(4)
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

    def set_pos(self, pos):
        self.pos = pos
        self.set_corners(pos, self.dim)

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
    def __init__(self, dim, color, pos, text='', TEXT_COLOR=(0,0,0), 
                    centered=True, font=Font.f50, image=False):
        super().__init__(dim, color)
        if image:
            self.img = pygame.transform.scale(image, dim)
            self.as_image = True
        else:
            self.as_image = False
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
        
        # if it's text
        if not self.as_image:
            x_marge, y_marge = center_text(self.dim, self.font, self.text)
            if not self.centered:
                x_marge = E(5)
            font_text = self.font.render(self.text,True,self.TEXT_COLOR)
            self.screen.blit(font_text,(self.pos[0]+x_marge,self.pos[1]+y_marge))
        else:
            self.screen.blit(self.img, self.pos)

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
                x_marge = E(5)
            font_text = self.font.render(line,True,self.TEXT_COLOR)
            self.screen.blit(font_text,(self.pos[0]+x_marge,self.pos[1]+i*y_line+y_marge))

class Delayed:
    '''
    Creates decorators,

    The decorated function should return True/False depending on whether or not it has been activated,
    if true, creates a delay in order to be spammed.
    '''
    wait = 0
    delayed = False
    def __init__(self, delay):
        self.delay = delay
        
    def __call__(self, func):
        def inner(*args, **kwargs):
            if self.delayed:
                self.wait += 1
                if self.wait == self.delay:
                    self.delayed = False
                    self.wait = 0
            else:
                # first argument if a boolean value of if the tested key was pressed
                executed = func(*args, **kwargs)
                if executed:
                    self.delayed = True
                return executed
        return inner

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
            x_marge = E(5)

        bottom_pos = (self.TOPLEFT[0] + x_marge + width, self.BOTTOMLEFT[1]-y_marge)
        top_pos = (self.TOPLEFT[0] + x_marge + width, self.TOPLEFT[1]+y_marge)
        
        if self.bool_cursor:
            pygame.draw.line(self.screen, C.BLACK, top_pos, bottom_pos, E(2))
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


def get_pressed_key(pressed):
    if pressed[pygame.K_a]:
        return 'a'
    elif pressed[pygame.K_b]:
        return 'b'
    elif pressed[pygame.K_c]:
        return 'c'
    elif pressed[pygame.K_d]:
        return 'd'    
    elif pressed[pygame.K_e]:
        return 'e'
    elif pressed[pygame.K_f]:
        return 'f'
    elif pressed[pygame.K_g]:
        return 'g'
    elif pressed[pygame.K_h]:
        return 'h'
    elif pressed[pygame.K_i]:
        return 'i'
    elif pressed[pygame.K_j]:
        return 'j'
    elif pressed[pygame.K_k]:
        return 'k'
    elif pressed[pygame.K_l]:
        return 'l'
    elif pressed[pygame.K_m]:
        return 'm'
    elif pressed[pygame.K_n]:
        return 'n'
    elif pressed[pygame.K_o]:
        return 'o'
    elif pressed[pygame.K_p]:
        return 'p'
    elif pressed[pygame.K_q]:
        return 'q'
    elif pressed[pygame.K_r]:
        return 'r'
    elif pressed[pygame.K_s]:
        return 's'
    elif pressed[pygame.K_t]:
        return 't'
    elif pressed[pygame.K_u]:
        return 'u'
    elif pressed[pygame.K_v]:
        return 'v'
    elif pressed[pygame.K_w]:
        return 'w'
    elif pressed[pygame.K_x]:
        return 'x'
    elif pressed[pygame.K_y]:
        return 'y'
    elif pressed[pygame.K_z]:
        return 'z'
    elif pressed[pygame.K_1]:
        return '1'
    elif pressed[pygame.K_2]:
        return '2'
    elif pressed[pygame.K_3]:
        return '3'
    elif pressed[pygame.K_4]:
        return '4'
    elif pressed[pygame.K_5]:
        return '5'
    elif pressed[pygame.K_6]:
        return '6'
    elif pressed[pygame.K_7]:
        return '7'
    elif pressed[pygame.K_8]:
        return '8'
    elif pressed[pygame.K_9]:
        return '9'
    elif pressed[pygame.K_0]:
        return '0'
    elif pressed[pygame.K_SPACE]:
        return ' '
