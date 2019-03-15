import pygame as pg
from pygame.locals import *
import numpy
import sys

from Game_objects import *
from Data import *


elem_size = 10
debug = True


def main():
    pg.init()
    x = 640
    y = 480
    window = pg.display.set_mode((640, 480))
    pg.display.set_caption("Xepa")
    go = Game_object(window)

    # create/draw objects that are independent of user input (if there are any???)

    while True:
        for event in pg.event.get():

            # handle events
            if event.type == QUIT:
                pg.quit()
                sys.exit()

            # apply changes to gamestate

            # draw changes to screen
            #window.fill((0,0,0))

            pg.display.update()

# TODO: Nur Map wird gezeichnet und ist ein container für alle anderen drawables, Änderungen an drawables werden durchgeführt
# und diese dann erneut Map hinzugefügt, die alten gelöscht


class Map(Game_object):

    # container class for all other drawable game objects

    unique_pixs = []
    objects = []

    def __init__(self, x, y):
        self.size_x = x * elem_size
        self.size_y = y * elem_size
        self.unique_pixs = [[0 for _ in range(x)] for _ in range(y)]  # TODO: check order of x and y

    def add_object(self, game_object, border_size=0):

        self.objects.append([self.objects.__len__(), game_object.name, game_object.type])

        if game_object.type is "building":
            upper_left_pix = [0,0]
            lower_rigt_pix = [0,0]
            for pix in game_object.pixs:
                if pix[0] < upper_left_pix[0] and pix[1] < upper_left_pix[1]:
                    upper_left_pix[0] = pix[0]
                    upper_left_pix[1] = pix[1]
                if pix[0] > lower_rigt_pix[0] and pix[1] > lower_rigt_pix[1]:
                    lower_rigt_pix[0] = pix[0]
                    lower_rigt_pix[1] = pix[1]
            size_x = lower_rigt_pix[0]-upper_left_pix[0]
            size_y = lower_rigt_pix[1]-upper_left_pix[1]

            go_pix_clone = game_object.pixs

            # TODO: check that coordinates for borders don't get out of map with np.max/np.min stuff
            for i in range(size_x):
                go_pix_clone.append([upper_left_pix[0]+i+1, numpy.max(0, upper_left_pix[1]-1)])
                go_pix_clone.append([upper_left_pix[0]+i+1, size_y+1])
            for i in range(size_y):
                go_pix_clone.append([0,i])
                go_pix_clone.append([size_x,i])
            go_pix_clone.append([size_x, size_y])

            for go_pix in go_pix_clone:
                if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                    return "Error! Trying to add object over already existing one."
            if debug:
                print("Added game object successfully!")

        # doesn't add object at all if not entirely possible
        for go_pix in game_object.pixs:
            if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                print("Error! Trying to add object over already existing one.")
                return 0
        for go_pix in game_object.pixs:
            self.unique_pixs[go_pix[0]][go_pix[1]] = material_codes[game_object.material]  # TODO: add different values for different objects/materials
        if debug:
            print("Added game object successfully!")
        return 1

    def remove_object(self, go):

        self.objects.remove([go.__len__(), go.name, go.type])
        return self.objects

    def draw_map(self):

        for go in self.objects:
            for pix in go.get_drawable():
                pg.draw.rect(self._window, mat_colour[go.type], (pix[0] * elem_size, pix[1] * elem_size, elem_size, elem_size))

main()


