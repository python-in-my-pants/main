import pygame as pg
import sys


class Button:

    def __init__(self, dim=[0, 0], pos=[0, 0], real_pos=[-1, -1], color=(170, 0, 0), img=0, text="Button", name="Button",
                 use_dim=True, action=(lambda: print("Clicked"))):

        if use_dim:
            self.surf = pg.Surface(dim)
        self.action = action
        self.name = name
        self.pos = pos[:]

        self.real_pos = 0
        if real_pos[0] == -1 and real_pos[1] == -1:
            self.real_pos = self.pos[:]
        else:
            self.real_pos = real_pos[:]

        self.dim = dim[:]
        self.img = img
        self.use_dim = use_dim
        self.text = text
        self.color = color

        if img:
            background_img = pg.image.load(img).convert()

            # background_img.set_colorkey((0, 0, 0))

            if use_dim:
                background_img = pg.transform.scale(background_img, dim)
            else:
                dim = [background_img.get_rect()[2], background_img.get_rect()[3]]
                self.surf = pg.Surface(dim)

            self.surf.blit(background_img, (0, 0))

            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(self.text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

        else:
            self.surf.fill(color)

            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(self.text, True, (255-color[0], 255-color[1], 255-color[2]))
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

    def update_text(self):

        if self.img:
            background_img = pg.image.load(self.img).convert()

            if self.use_dim:
                background_img = pg.transform.scale(background_img, self.dim)
            else:
                dim = [background_img.get_rect()[2], background_img.get_rect()[3]]
                self.surf = pg.Surface(dim)

            self.surf.blit(background_img, (0, 0))

            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(self.text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

        else:
            self.surf.fill(self.color)

            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(self.text, True, (255 - self.color[0], 255 - self.color[1], 255 - self.color[2]))
            self.surf.blit(font_render, (int(self.dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(self.dim[1] / 2) - int(font_render.get_height() / 2)))

    def is_focused(self, mouse_pos):

        if self.real_pos[0] + self.dim[0] >= mouse_pos[0] >= self.real_pos[0] and \
           self.real_pos[1] + self.dim[1] >= mouse_pos[1] >= self.real_pos[1]:
            return True
        return False

    @staticmethod
    def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pg.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)


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

        self.surf = pg.Surface(dim. pg.SRCALPHA, 32)
        self.surf.convert_alpha()

        self.bar_surf = pg.Surface([int(dim[0]*curr / end), dim[1]])
        self.bar_surf.fill(color)

        self.surf.blit(self.bar_surf)

    def update(self, val):

        self.curr = val
        self.bar_surf = pg.Surface([int(self.dim[0]*self.curr / self.end), self.dim[1]])

        x = 100*self.curr/self.end

        r = 255 if (x <= 50) else int(255 - 255*(x-50)/50)
        g = int(255 - 255*(50-x)/50) if x <= 50 else 255

        self.bar_surf.fill((r, g, 0))
        self.surf.blit(self.bar_surf)


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
        font = pg.font.SysFont("comicsansms", 24)
        font_render = font.render(self.content, True, (255, 255, 255))
        self.surf.blit(font_render, (int(self.dimension[0] / 2) - int(font_render.get_width() / 2),
                                     int(self.dimension[1] / 2) - int(font_render.get_height() / 2)))

        return self.surf'''
