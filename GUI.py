import pygame as pg
import Data
import time
import sys


class Button:

    def __init__(self, dim=[0, 0], pos=[0, 0], real_pos=[-1, -1], color=(170, 0, 0), font_color=(0, 0, 0), img_uri=0,
                 img_source=None, text="Button", name="Button", use_dim=True, action=(lambda: print("Clicked"))):

        self.dim = [int(d) for d in dim]
        self.use_dim = use_dim
        if use_dim:
            self.surf = pg.Surface(self.dim)
        self.action = action
        self.func = action  # holds the action function when button is not active
        self.name = name
        self.offset = 0
        self.font_color = font_color
        self.pos = [int(p) for p in pos]  # position relative to surface it is to be blitted on

        self.real_pos = 0  # real position on screen
        if real_pos[0] == -1 and real_pos[1] == -1:
            self.real_pos = self.pos[:]
        else:
            self.real_pos = [int(p) for p in real_pos]

        self.img_uri = img_uri
        self.text = text
        self.color = color

        if img_uri or img_source:

            if img_uri and not img_source:
                background_img = pg.image.load(img_uri)
            if img_source:
                background_img = img_source

            if use_dim:
                background_img = pg.transform.scale(background_img, self.dim)
            else:
                dim = [background_img.get_rect()[2], background_img.get_rect()[3]]
                self.surf = pg.Surface(dim)

            self.surf = background_img

            # TODO make font size dependent on text len
            font_size = int(0.7 * self.dim[1]) if int(0.7*self.dim[1]) < int(0.6*self.dim[0]) else int(0.6*self.dim[0])
            font = pg.font.SysFont(Data.font, font_size)
            #font = pg.font.Font("assets/18 ARMY.ttf", font_size)
            font_render = font.render(self.text, True, self.font_color)
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))
        else:
            darker = (max(0, color[0]-45),
                      max(0, color[1]-45),
                      max(0, color[2]-45))
            self.surf.fill(darker)
            b = min(int(self.surf.get_width()*0.05), int(self.surf.get_height()*0.05))
            col_surf = pg.Surface([self.surf.get_width()-2*b, self.surf.get_height()-2*b])
            col_surf.fill(color)
            self.surf.blit(col_surf, [b, b])

            # TODO make font size dependent on text len
            font_size = int(0.7 * self.dim[1]) if int(0.7*self.dim[1]) < int(0.6*self.dim[0]) else int(0.6*self.dim[0])
            font = pg.font.SysFont(Data.font, font_size)
            font_render = font.render(self.text, True, self.font_color)
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

    def activate(self):
        self.action = self.func

    def deactivate(self):
        self.action = (lambda: None)

    def set_offsets(self, y_offset=0):
        self.offset = y_offset

    def update_real_position(self, y_diff):

        self.real_pos[1] += y_diff

    def update_text(self):

        if self.img_uri:
            background_img = pg.image.load(self.img_uri).convert()

            if self.use_dim:
                background_img = pg.transform.scale(background_img, self.dim)
            else:
                dim = [background_img.get_rect()[2], background_img.get_rect()[3]]
                self.surf = pg.Surface(dim)

            self.surf.blit(background_img, (0, 0))

            font_size = int(0.7 * self.dim[1]) if int(0.7*self.dim[1]) < int(0.6*self.dim[0]) else int(0.6*self.dim[0])
            font = pg.font.SysFont(Data.font, font_size)
            font_render = font.render(self.text, True, self.font_color)
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

        else:
            darker = (max(0, self.color[0] - 45),
                      max(0, self.color[1] - 45),
                      max(0, self.color[2] - 45))
            self.surf.fill(darker)
            b = min(int(self.surf.get_width() * 0.05), int(self.surf.get_height() * 0.05))
            col_surf = pg.Surface([self.surf.get_width() - 2 * b, self.surf.get_height() - 2 * b])
            col_surf.fill(self.color)
            self.surf.blit(col_surf, [b, b])

            # TODO make font size dependent on text len
            font_size = int(0.7 * self.dim[1]) if int(0.7 * self.dim[1]) < int(0.6 * self.dim[0]) else int(
                0.6 * self.dim[0])
            font = pg.font.SysFont(Data.font, font_size)
            font_render = font.render(self.text, True, self.font_color)
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

    def set_text(self, text):

        self.text = text

    def change_text(self, new_text):
        self.text = new_text
        self.update_text()

    def is_focused(self, mouse_pos):

        # todo is this faster? presumably no because you have to use real positions
        # return self.surf.get_rect().collidepoint(mouse_pos)

        if self.real_pos[0] + self.dim[0] >= mouse_pos[0] >= self.real_pos[0] and \
           self.real_pos[1] + self.offset + self.dim[1] >= mouse_pos[1] >= self.real_pos[1] + self.offset:
            return True
        return False


class HPBar:

    id_counter = 0

    def __init__(self, dim, pos=[0, 0], curr=100, end=100, color=(0, 255, 0), name="HPBar"):

        self.dim = dim[:]
        self.pos = pos[:]
        self.name = name

        self.idi = self.id_counter
        self.id_counter += 1

        self.curr = curr
        self.end = end
        self.color = color

        self.surf = pg.Surface(dim)
        #self.surf.convert_alpha(self.surf)
        self.surf.fill((12, 12, 12))
        self.surf.set_colorkey((12, 12, 12))

        self.bar_surf = pg.Surface([int(dim[0]*curr / end), dim[1]])
        self.bar_surf.fill(color)

        self.surf.blit(self.bar_surf, [0, 0])

    def update(self, val):

        self.curr = val
        if not int(self.dim[0]*self.curr / self.end) < 0:
            self.bar_surf = pg.Surface([int(self.dim[0]*self.curr / self.end), self.dim[1]])

            x = 100*self.curr/self.end

            r = 255 if (x <= 50) else int(255 - 255*(x-50)/50)
            g = int(255 - 255*(50-x)/50) if x <= 50 else 255

            self.surf.fill((12, 12, 12))
            self.surf.set_colorkey((12, 12, 12))
            self.bar_surf.fill((r, g, 0))
            self.surf.blit(self.bar_surf, [0, 0])


class Overlay:

    def __init__(self, pos=(0, 0), boi_to_attack=None):
        self.surf = pg.transform.scale(pg.image.load("assets/Overlay/dude.png"), (150, 200))
        self.pos = pos
        self.boi_to_attack = boi_to_attack
        self.newblit = False

        self.info_pos = self.pos[0]-25, self.pos[1] + 200
        self.myfont = pg.font.SysFont('Comic Sans MS', 15)
        self.info_tafel = pg.transform.scale(pg.image.load("assets/deco_banner.png"), (150, 150))
        self.timer = 0

        self.type = {
            "0": pg.transform.scale(pg.image.load("assets/Overlay/dude_kopf.png"), (100, 200)),
            "1": pg.transform.scale(pg.image.load("assets/Overlay/dude_larm.png"), (100, 200)),
            "2": pg.transform.scale(pg.image.load("assets/Overlay/dude_rarm.png"), (100, 200)),
            "3": pg.transform.scale(pg.image.load("assets/Overlay/dude_torso.png"), (100, 200)),
            "4": pg.transform.scale(pg.image.load("assets/Overlay/dude_lbein.png"), (100, 200)),
            "5": pg.transform.scale(pg.image.load("assets/Overlay/dude_rbein.png"), (100, 200)),
            "6": pg.transform.scale(pg.image.load("assets/Overlay/dude.png"), (100, 200))
        }

        self.btn_dim = {
            0: (20, 25),
            1: (19, 69),
            2: (19, 69),
            3: (30, 50),
            4: (15, 87),
            5: (15, 87)
        }

        self.btn_pos = {
            0: [self.pos[0] + 41, self.pos[1] + 16],
            1: [self.pos[0] + 16, self.pos[1] + 41],
            2: [self.pos[0] + 66, self.pos[1] + 41],
            3: [self.pos[0] + 35, self.pos[1] + 42],
            4: [self.pos[0] + 35, self.pos[1] + 93],
            5: [self.pos[0] + 51, self.pos[1] + 93],
        }

    def update_info(self, info):
        print(info)
        if isinstance(info, int):
            self.timer = time.time() + 2
            self.info_tafel = pg.transform.scale(pg.image.load("assets/deco_banner.png"), (150, 150))
            self.info_tafel.blit(self.myfont.render("Damage done: " + str(info), False, (255, 255, 255)), (18, 65))

        if self.timer <= time.time():
            if isinstance(info, tuple) and len(info) == 4:

                self.info_tafel = pg.transform.scale(pg.image.load("assets/deco_banner.png"), (150, 150))
                self.info_tafel.blit(self.myfont.render(("Hitchance: " + str(info[0]) + " %"),
                                     False, (255, 255, 255)), (22, 40))
                if info[3]:
                    self.info_tafel.blit(self.myfont.render(("Damage:     " + str(info[1]*6)),
                                         False, (255, 255, 255)), (22, 65))
                else:
                    self.info_tafel.blit(self.myfont.render(("Damage:     " + str(info[1])),
                                         False, (255, 255, 255)), (22, 65))
                self.info_tafel.blit(self.myfont.render(("Shots:         " + str(info[2])),
                                     False, (255, 255, 255)), (22, 90))

            if isinstance(info, str):
                self.info_tafel = pg.transform.scale(pg.image.load("assets/deco_banner.png"), (150, 150))
                self.info_tafel.blit(self.myfont.render(info, False, (255, 255, 255)), (22, 65))


class VisualTimer:

    def __init__(self, amount=0, pos=(0, 0), size=75, action=(lambda: None)):
        self.amount = amount
        self.pos = pos
        self.size = size
        self.action = action

        self.myfont = pg.font.SysFont('Comic Sans MS', size)
        self.surf = self.myfont.render("00:00", False, (250, 0, 0))
        self.pre = 0

    def update_visualtimer(self):
        if not self.pre:
            self.pre = int(time.time())
        if self.amount <= 0:
            self.action()
        if self.pre <= int(time.time()) and self.amount > 0:
            self.amount -= 1
            minuten = int(self.amount / 60)
            zwi_zeit = self.amount - (minuten * 60)
            sekunden = int(zwi_zeit % 60)

            if minuten < 10:
                minuten_str = "0" + str(minuten)
            else:
                minuten_str = str(minuten)

            if sekunden < 10:
                sekunden_str = "0" + str(sekunden)
            else:
                sekunden_str = str(sekunden)

            self.surf = self.myfont.render((minuten_str + ":" + sekunden_str), False, (255, 255, 255))
            self.pre = int(time.time()) + 1

    def start_timer(self, zeit):
        self.amount = zeit

    def stop_timer(self):
        self.amount = 0


'''class Textfield:

    def __init__(self, dim, pos=[], background_colour=(255, 255, 255), name="Textfield"):

        self.dimension = dim[:]
        self.pos = pos[:]
        self.background_colour = background_colour
        self.name = name
        self.surf = pg.Surface(dim)
        self.content = "Enter IP here"

        def on_click():


        self.action = on_click

    def is_focused(self, mouse_pos):

        if mouse_pos[0] > self.pos[0] and mouse_pos[0] < self.pos[0] + self.dim[0] and \
           mouse_pos[1] > self.pos[1] and mouse_pos[1] < self.pos[1] + self.dim[1]:
            return True
        return False

    def draw(self):  # returns surface of button

        self.surf.fill(self.background_colour)
        font = pg.font.SysFont(Data.font, 24)
        font_render = font.render(self.content, True, (255, 255, 255))
        self.surf.blit(font_render, (int(self.dimension[0] / 2) - int(font_render.get_width() / 2),
                                     int(self.dimension[1] / 2) - int(font_render.get_height() / 2)))

        return self.surf'''
