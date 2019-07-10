import pygame as pg


class Button:

    def __init__(self, dim, pos=[0, 0], color=(170, 0, 0), img=0, text="Button", name="Button", \
                 action=(lambda: print("Clicked"))):

        self.surf = pg.Surface(dim)
        self.action = action
        self.name = name
        self.pos = pos[:]
        self.dim = dim[:]

        if img:
            background_img = pg.image.load(img)
            background_img = pg.transform.scale(background_img, dim)
            background_img = background_img.convert()
            self.surf.blit(background_img)
        else:
            self.surf.fill(color)
            font = pg.font.SysFont("Comic Sans", 24)
            font_render = font.render(text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(dim[0] / 2) - int(font_render.get_width() / 2), \
                                         int(dim[1] / 2) - int(font_render.get_height()/ 2)))

    def is_focused(self, mouse_pos):

        if mouse_pos[0] > self.pos[0] and mouse_pos[0] < self.pos[0] + self.dim[0] and \
           mouse_pos[1] > self.pos[1] and mouse_pos[1] < self.pos[1] + self.dim[1]:
            return True
        return False