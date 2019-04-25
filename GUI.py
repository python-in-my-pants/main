import pygame as pg


class Button:

    def __init__(self, dim, color=(170, 0, 0), img=0, text="Button", name="Button", action=(lambda: print("Clicked"))):

        self.surf = pg.Surface(dim)
        self.action = action
        self.name = name

        if img:
            background_img = pg.image.load("main_background.jpg")
            background_img = pg.transform.scale(background_img, dim)
            background_img = background_img.convert()
            self.surf.blit(background_img)
        else:
            self.surf.fill(color)
            font = pg.font.SysFont("Comic Sans", 24)
            font_render = font.render(text, True, (255, 255, 255))
            self.surf.blit(font_render, (int(dim[0] / 2) - int(font_render.get_width() / 2), \
                                         int(dim[1]/2) - int(font_render.get_height()/2)))
