import pygame as pg
import Data
import sys


class Button:

    def __init__(self, dim=[0, 0], pos=[0, 0], real_pos=[-1, -1], color=(170, 0, 0), font_color=(0, 0, 0), img_uri=0,
                 img_source=None, text="Button", name="Button", use_dim=True, action=(lambda: print("Clicked"))):

        if use_dim:
            self.surf = pg.Surface(dim)

        self.action = action
        self.name = name
        self.offset = 0
        self.font_color = font_color
        self.pos = pos[:]  # position relative to surface it is to be blitted on

        self.real_pos = 0  # real position on screen
        if real_pos[0] == -1 and real_pos[1] == -1:
            self.real_pos = self.pos[:]
        else:
            self.real_pos = real_pos[:]

        self.dim = dim[:]
        self.img_uri = img_uri
        self.use_dim = use_dim
        self.text = text
        self.color = color

        if img_uri or img_source:

            if img_uri and not img_source:
                background_img = pg.image.load(img_uri)#.convert_alpha()  # HAHAHAHA does not work ...
            if img_source:
                background_img = img_source

            # background_img.set_colorkey((0, 0, 0))

            if use_dim:
                background_img = pg.transform.scale(background_img, dim)
            else:
                dim = [background_img.get_rect()[2], background_img.get_rect()[3]]
                self.surf = pg.Surface(dim)

            self.surf.blit(background_img, (0, 0))
            self.surf.convert_alpha()

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
        self.bar_surf = pg.Surface([int(self.dim[0]*self.curr / self.end), self.dim[1]])

        x = 100*self.curr/self.end

        r = 255 if (x <= 50) else int(255 - 255*(x-50)/50)
        g = int(255 - 255*(50-x)/50) if x <= 50 else 255

        self.surf.fill((12, 12, 12))
        self.surf.set_colorkey((12, 12, 12))
        self.bar_surf.fill((r, g, 0))
        self.surf.blit(self.bar_surf, [0, 0])


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
