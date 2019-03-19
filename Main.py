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

    def __init__(self, x_size, y_size, window):  # STATUS: working, returns 1 on success, 0 else
        self.size_x = x_size * elem_size  # size_x holds map size in actual drawable pixels coords, x and y are to be commited in desired size in elements
        self.size_y = y_size * elem_size
        self.unique_pixs = [[0 for _ in range(int(x_size))] for _ in range(int(y_size))]  # TODO: check order of x and y
        self.window = window

    def add_object(self, game_object, border_size=0,
                   permutation_lenght=[0, 0]):  # STATUS: partially working (building stuff not ready)

        """
                  "out of map bounds" leads to shifting to object until either it is in the map or abortion
        "collision with other object" leads to shifting to object until either no collision is occurring or abortion

        :param game_object: the object to add
        :param border_size: optional border around the object to sustain accessability of buildings etc.
        :return: 1 on success, 0 else
        """

        # TODO: when trying to put in object with border, try to fit in border (test bounds with border) and then check
        # out_of_map with object position relative to border

        # check object size
        for pix in game_object.get_drawable():
            if pix[0] > self.size_x - 1 or pix[1] > self.size_y - 1:
                print("Error! Object is too large senpai ... >///<")
                return 0

        '''

        Collision codes:

        none            0

        left            1
        top             2
        right           4
        bottom          9

        left-top        3 ; left-top-bottom     12
        top-right       6 ; top-right-left       7
        right-bottom    13; right-bottom-top    15
        bottom-left     10; bottom-left-right   14

        left-top-right-bottom 16

        '''

        out_of_map = 0

        # out of bounds?
        for pix in game_object.get_drawable():
            if pix[0] < 0:
                print("Warning! Game object would be out of bounds (left)!")
                out_of_map += 1
            elif pix[1] < 0:
                print("Warning! Game object would be out of bounds (top)!")
                out_of_map += 2
            elif pix[0] > get_x() - 1:
                print("Warning! Game object would be out of bounds (right)!")
                out_of_map += 4
            elif pix[1] > get_y() - 1:
                print("Warning! Game object would be out of bounds (bottom)!")
                out_of_map += 9

        # handle different collisions
        if out_of_map is 16:
            print("Error! Object is too large senpai ... >///<")
            return 0
        elif out_of_map is 12 or out_of_map is 15:
            # TODO: turn object clockwise if object can fit at all

            # get height of object
            upper_left_pix = [0, 0]
            lower_right_pix = [0, 0]

            # find upper left and lower right most pixel
            for pix in game_object.get_drawable():
                if pix[0] < upper_left_pix[0] and pix[1] < upper_left_pix[1]:
                    upper_left_pix[0] = pix[0]
                    upper_left_pix[1] = pix[1]
                if pix[0] > lower_right_pix[0] and pix[1] > lower_right_pix[1]:
                    lower_right_pix[0] = pix[0]
                    lower_right_pix[1] = pix[1]

            # set size of object + border_size accordingly
            size_x = lower_right_pix[0] - upper_left_pix[0] + 2 * border_size
            size_y = lower_right_pix[1] - upper_left_pix[1] + 2 * border_size

            if size_y <= self.size_y:
                game_object.turn("cw")
                return self.add_object(game_object, border_size)
            else:
                print("Error! Object is too large senpai ... >///<")
                return 0

        elif out_of_map is 7 or out_of_map is 14:
            # TODO: turn object counter-clockwise if object can fit at all

            # get height of object
            upper_left_pix = [0, 0]
            lower_right_pix = [0, 0]

            # find upper left and lower right most pixel
            for pix in game_object.get_drawable():
                if pix[0] < upper_left_pix[0] and pix[1] < upper_left_pix[1]:
                    upper_left_pix[0] = pix[0]
                    upper_left_pix[1] = pix[1]
                if pix[0] > lower_right_pix[0] and pix[1] > lower_right_pix[1]:
                    lower_right_pix[0] = pix[0]
                    lower_right_pix[1] = pix[1]

            # set size of object + border_size accordingly
            size_x = lower_right_pix[0] - upper_left_pix[0] + 2 * border_size
            size_y = lower_right_pix[1] - upper_left_pix[1] + 2 * border_size

            if size_x <= self.size_x:
                game_object.turn("ccw")
                return self.add_object(game_object, border_size)
            else:
                print("Error! Object is too large senpai ... >///<")
                return 0

        elif out_of_map is 1:
            game_object.move([1, 0])
            return self.add_object(game_object, border_size)
        elif out_of_map is 2:
            game_object.move([0, 1])
            return self.add_object(game_object, border_size)
        elif out_of_map is 4:
            game_object.move([-1, 0])
            return self.add_object(game_object, border_size)
        elif out_of_map is 9:
            game_object.move([0, -1])
            return self.add_object(game_object, border_size)
        elif out_of_map is 0:
            print("No out_of_map with map boundaries")
        else:
            print("Error!")

        # collision with other objects?
        for go_pix in game_object.get_drawable():
            if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                # TODO: define function "shift(index)"
                # 0 is origin, return vec in according direction:
                '''
                      K 9 D
                    J 8 1 5 E
                    C 4 0 2 A
                    I 7 3 6 F
                      H B G

                    usw.

                    ...maybe via permutations?

                    counter is [a,b] while a is counter for rounds

                    round 1 is 1,2,3,4 ä
                        round 2 is 5,6,7,8
                    round 3 is 8,A,B,C
                        round 4 is D,E,F,G,H,I,J,K
                    round 5 is L,M,N,O

                    and so on
                    and b is the index in the round
                '''
                # simple solution: move in random direction

                game_object.move()

        # check for duplicate names
        for obj in self.objects:
            if obj.name == game_object.name:
                print("Warning! Adding object with duplicate name!")
                break

        #######################################
        # hier warst du!
        #######################################

        '''

        ---> border stuff

        # handle surrounding border if border_size > 0
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
        size_x = lower_rigt_pix[0] - upper_left_pix[0] + 2*border_size
        size_y = lower_rigt_pix[1] - upper_left_pix[1] + 2*border_size

        border = Border(obj_type="default", size_x_=size_x, size_y_=size_y,
                        pos=[upper_left_pix[0]-border_size, upper_left_pix[1]-border_size]).get_drawable()

        for pix in border:
            if pix[0] < 0 or pix[1] < 0 or pix[0] > get_x()-1 or pix[1] > get_y()-1:
                print("Warning! Border would be out of map! Please adjust position or make the object smaller.")
                return 0

        # check for overlapping
        for go_pix in border:
            if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                print("Error! Not enough room for border")
                return 0

        '''

        '''
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
        '''

        # doesn't add object at all if not entirely possible
        for go_pix in game_object.get_drawable():
            if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                print("Error! Trying to add object over already existing one.")
                return 0

            out_of_map = False

            # out_of_map?
            for go_pix in game_object.get_drawable():
                if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                    out_of_map = True

            while out_of_map:
                out_of_map = False
                resized = False

                '''

                ---> shorten object to fit in map

                for pix in game_object.get_drawable():
                    pix[0] += 1

                    if pix[0] > get_x()/elem_size:
                        pix[0] = int(numpy.floor(get_x()/elem_size))-2
                        resized = True'''

                # move
                game_object.move()

                # out of bounds?
                for pix in game_object.get_drawable():
                    if pix[0] < 0 or pix[1] < 0 or pix[0] > get_x() - 1 or pix[1] > get_y() - 1:
                        print("Warning! Game object would be out of bounds!")
                        return 0

                # out_of_map?
                for go_pix in game_object.get_drawable():
                    if self.unique_pixs[go_pix[0]][go_pix[1]] is not 0:
                        out_of_map = True

                if out_of_map and resized:
                    print("Could not add object due to too few space")
                    # TODO: will now add all pending objects at once when windows gets bigger, make so only 1 is added
                    return 0

        self.objects.append(game_object)

        # modify unique_pixs
        for go_pix in game_object.get_drawable():
            self.unique_pixs[go_pix[0]][go_pix[1]] = material_codes[game_object.material]

        if debug:
            # print(numpy.array(self.objects[0].get_drawable()))
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
        self.unique_pixs = [[0 for _ in range(int(self.size_x / elem_size))] for _ in
                            range(int(self.size_y / elem_size))]

    def draw_map(self):  # STATUS: new

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
x = elem_size * 50  # mult of 10
y = elem_size * 20  # mult of 10
window = pg.display.set_mode((x, y))
pg.display.set_caption("Xepa")

map = Map(x / 10, y / 10, window)

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
                h = SimpleHouse(name=("Simple house" + str(houses)), obj_type="default")
                houses.append(h)
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
                h = SimpleHouse(name=("Simple house" + str(houses)), obj_type="default")
                houses.append(h)
                redraw_house

        if event.type == pg.KEYUP:
            if event.key == ord("n"):
                redraw_house = False

        # apply changes to game state

        # draw changes to screen
        if redraw_house:
            window.fill((0, 0, 0))
            map.clear()

            for house in houses:
                house.print_()
                map.add_object(house)

            map.draw_map()
            redraw_house = False

            if debug:
                print()

        pg.display.update()
