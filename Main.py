import pygame as pg
from pygame.locals import *
import numpy
import sys

from Game_objects import *
from Data import *


elem_size = 25
debug = True


# TODO: Nur Map wird gezeichnet und ist ein container für alle anderen drawables, Änderungen an drawables werden durchgeführt
# und diese dann erneut Map hinzugefügt, die alten gelöscht


class Map(GameObject):
    # container class for all other drawable game objects

    unique_pixs = []  # holds definite pixel(materials) that will be drawn
    objects = []  # holds list of objects on the map of the form: [id, object]
    window = -1

    def __init__(self, x_size, y_size, window):  # STATUS: working
        self.size_x = x_size * elem_size  # size_x holds map size in actual drawable pixels coords, x and y are to be commited in desired size in elements
        self.size_y = y_size * elem_size
        self.unique_pixs = [[0 for _ in range(int(x_size))] for _ in range(int(y_size))]  # TODO: check order of x and y
        self.window = window

    def add_object(self, game_object, border_size=0):  # STATUS: partially working (building stuff not ready)

        for obj in self.objects:
            if obj.name == game_object.name:
                print("Warning! Adding object with duplicate name!")
                break

        shift = True

        if game_object.type is "building":
            upper_left_pix = [0, 0]
            lower_rigt_pix = [0, 0]
            # find upper left and lower right most pixel
            for pix in game_object.get_drawable():
                if pix[0] < upper_left_pix[0] and pix[1] < upper_left_pix[1]:
                    upper_left_pix[0] = pix[0]
                    upper_left_pix[1] = pix[1]
                if pix[0] > lower_rigt_pix[0] and pix[1] > lower_rigt_pix[1]:
                    lower_rigt_pix[0] = pix[0]
                    lower_rigt_pix[1] = pix[1]
            # set size of object + border_size accordingly
            size_x = lower_rigt_pix[0] - upper_left_pix[0]
            size_y = lower_rigt_pix[1] - upper_left_pix[1]

            # create clone of pixs to not modify original object
            go_pix_clone = game_object.pixs

            # define a box according to "border_size" around the object
            # TODO: check that coordinates for borders don't get out of map with np.max/np.min stuff
            for i in range(size_x):
                go_pix_clone.append([upper_left_pix[0] + i + 1, numpy.max(0, upper_left_pix[1] - 1)])
                go_pix_clone.append([upper_left_pix[0] + i + 1, size_y + 1])
            for i in range(size_y):
                go_pix_clone.append([0, i])
                go_pix_clone.append([size_x, i])
            go_pix_clone.append([size_x, size_y])

            # check for overlapping
            for go_pix in go_pix_clone:
                if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                    return "Error! Trying to add object over already existing one."
            if debug:
                print("Added game object successfully!")

        # doesn't add object at all if not entirely possible
        if not shift:
            for go_pix in game_object.get_drawable():
                if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                    print("Error! Trying to add object over already existing one.")
                    return 0
        else:

            collision = False

            for go_pix in game_object.get_drawable():
                if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                    collision = True

            while collision:
                collision = False

                for pix in game_object.get_drawable():
                    pix[0] += 1
                    if pix[0] > get_x()/elem_size:
                        pix[0] = int(numpy.floor(get_x()/elem_size))-2 # TODO: remove loop

                for go_pix in game_object.get_drawable():
                    if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                        collision = True

        self.objects.append(game_object)

        # modify unique_pixs
        for go_pix in game_object.get_drawable():
            self.unique_pixs[go_pix[0]][go_pix[1]] = material_codes[game_object.material]

        if debug:
            print(numpy.array(self.objects[0].get_drawable()))
            print("Added game object successfully!")

        return 1

    def remove_object_by_id(self, go):  # STATUS: new

        self.objects.remove(go)
        return self.objects

    def remove_object_by_name(self, name):

        for obj in self.objects:
            if obj.name == name:
                self.objects.remove(obj)
        return self.objects

    def clear(self):  # STATUS: new

        self.objects = []
        self.unique_pixs = [[0 for _ in range(int(self.size_x/elem_size))] for _ in range(int(self.size_y/elem_size))]

    def draw_map(self):  # STATUS: new

        if debug:
            print(self.objects)
            print(numpy.array(self.unique_pixs))

        for go in self.objects:
            for pix in go.get_drawable():
                pg.draw.rect(self.window, mat_colour[go.material],
                             (pix[0] * elem_size, pix[1] * elem_size, elem_size, elem_size))
        self.draw_grid()

    def draw_grid(self):

        '''for i in range(int(self.size_x/elem_size)):
            for d in range(int(self.size_y/elem_size)):
                pg.draw.rect(get_window(), (0, 99, 0), (i*elem_size, d*elem_size, elem_size, elem_size), 1)'''

        for i in range(get_x()):
            for d in range(get_y()):
                pg.draw.rect(get_window(), (0, 99, 0), (i * elem_size, d * elem_size, elem_size, elem_size), 1)


# ----------------------------------------------------------------------------------------------------------------------

def get_window():
    return window
def get_x():
    return x
def get_y():
    return y

pg.init()
x = elem_size* 10 # mult of 10
y = elem_size* 10 # mult of 10
window = pg.display.set_mode((x, y))
pg.display.set_caption("Xepa")

map = Map(x/10, y/10, window)

redraw_house = True

# create/draw objects that are independent of user input (if there are any???)

houses = []
houses.append(SimpleHouse(name=("Simple house" + str(houses)), obj_type="default"))

while True:
    for event in pg.event.get():

        # handle events
        if event.type == QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == ord("n"):
                redraw_house = True
                houses.append(SimpleHouse(name=("Simple house" + str(houses)), obj_type="default"))
        if event.type == pg.KEYDOWN:
            if event.key == K_RIGHT:
                x += elem_size
                window = pg.display.set_mode((x, y))
                map.draw_map()
        if event.type == pg.KEYDOWN:
            if event.key == K_DOWN:
                y += elem_size
                window = pg.display.set_mode((x, y))
                map.draw_map()
        if event.type == pg.KEYDOWN:
            if event.key == K_KP_PLUS:
                houses.append(SimpleHouse(name=("Simple house"+str(houses)), obj_type="default"))
                redraw_house

        if event.type == pg.KEYUP:
            if event.key == ord("n"):
                redraw_house = False

        # apply changes to game state

        # draw changes to screen
        if redraw_house:
            window.fill((0,0,0))
            map.clear()

            for house in houses:
                house.print()
                map.add_object(house)

            map.draw_map()
            redraw_house = False

            if debug:
                print()

        pg.display.update()
