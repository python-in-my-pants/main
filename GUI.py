import pygame as pg
import sys


class Button:

    def __init__(self, dim, pos=[0, 0], color=(170, 0, 0), img=0, text="Button", name="Button", \
                 action=(lambda: print("Clicked"))):

        self.surf = pg.Surface(dim)
        self.action = action
        self.name = name
        self.pos = pos[:]
        self.dim = dim[:]

        if img:
            background_img = pg.image.load(img).convert()

            #background_img.set_colorkey((0, 0, 0))

            background_img = pg.transform.scale(background_img, dim)

            self.surf.blit(background_img, (0, 0))

            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(dim[1] / 2) - int(font_render.get_height() / 2)))

        else:
            self.surf.fill(color)
            font = pg.font.SysFont("comicsansms", 24)
            font_render = font.render(text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(dim[0] / 2) - int(font_render.get_width() / 2),
                                         int(dim[1] / 2) - int(font_render.get_height() / 2)))

    def is_focused(self, mouse_pos):

        if mouse_pos[0] >= self.pos[0] and mouse_pos[0] <= self.pos[0] + self.dim[0] and \
           mouse_pos[1] >= self.pos[1] and mouse_pos[1] <= self.pos[1] + self.dim[1]:
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
