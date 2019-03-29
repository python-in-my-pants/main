import pygame as pg
from pygame.locals import *
import numpy
import sys

from Game_objects import *
from Data import *

elem_size = 25
debug = True


# TODO: Nur Map wird gezeichnet und ist ein container für alle anderen drawables, Änderungen an drawables werden \
#       durchgeführt und diese dann erneut Map hinzugefügt, die alten gelöscht


class Map(GameObject):
    # container class for all other drawable game objects

    unique_pixs = []  # holds definite pixel(materials) that will be drawn
    objects = []  # holds list of objects on the map of the form: [id, object]
    window = -1

    def __init__(self, x_size, y_size, window):  # STATUS: working, returns 1 on success, 0 else
        self.size_x = x_size  # size_x holds map size in actual drawable pixels coords, x and y are to be \
                              # commited in desired size in elements
        self.size_y = y_size
        self.unique_pixs = [[0 for _ in range(int(x_size))] for _ in range(int(y_size))] # beware, when using you have\
        # to call [y][x]
        self.window = window

    def add_object(self, game_object, border_size=0, recursion_depth=0, permutation_lenght=[0, 0]):  # STATUS: partially working, border
        # stuff not yet, crashes when too deep recursion occurs

        """
                  "out of map bounds" leads to shifting to object until either it is in the map or abortion
        "collision with other object" leads to shifting to object until either no collision is occurring or abortion

        :param game_object: the object to add
        :param border_size: optional border around the object to sustain accessability of buildings etc.
        :return: 1 on success, 0 else
        """

        if debug:
            print(game_object.size_x)
            print(game_object.size_y)

        # check for too deep recursion, may remove this when better collision handling is in place
        if recursion_depth > 100:
            print("Cannot fit object")
            return 0

        #########################
        ### check object size ###
        #########################

        # get height of object
        size_x = game_object.size_x+2*border_size
        size_y = game_object.size_y+2*border_size

        if size_x > self.size_x - 1 or size_y > self.size_y - 1:
            print("Error! Object is too large senpai ... >///<")
            return 0

        ##############################
        ### out of bounds handling ###
        ##############################

        #             left   top    right  bottom
        out_of_map = [False, False, False, False]

        ########################################################### new ###############################################

        # check if border would be out of map
        if border_size > 0:
            for pix in Border(obj_type="default", size_x_=size_x, size_y_=size_y,
                              pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size]).get_drawable():
                if pix[0] < 0:
                    out_of_map[0] = True
                elif pix[1] < 0:
                    out_of_map[1] = True
                elif pix[0] > self.size_x - 1:
                    out_of_map[2] = True
                elif pix[1] > self.size_y - 1:
                    out_of_map[3] = True

        ################################################################################################################

        # check if object itself would be out of map
        for pix in game_object.get_drawable():
            if pix[0] < 0:
                out_of_map[0] = True
            elif pix[1] < 0:
                out_of_map[1] = True
            elif pix[0] > self.size_x - 1:
                out_of_map[2] = True
            elif pix[1] > self.size_y - 1:
                out_of_map[3] = True

        if out_of_map[0]:
            print("Warning! Game object would be out of bounds (left)!\n")
        elif out_of_map[1]:
            print("Warning! Game object would be out of bounds (top)!\n")
        elif out_of_map[2]:
            print("Warning! Game object would be out of bounds (right)!\n")
        elif out_of_map[3]:
            print("Warning! Game object would be out of bounds (bottom)!\n")

        # handle different collisions
        if out_of_map[0] is True and out_of_map[1] is True and out_of_map[2] is True and out_of_map[3] is True:
            print("Error! Object is too large senpai ... >///<")
            return 0
        elif out_of_map[1] is True and out_of_map[3] is True:

            # if object could fit when turned, do so, else reject
            if size_y <= self.size_x:
                game_object.turn("cw")
                return self.add_object(game_object, border_size, recursion_depth+1)
            else:
                print("Error! Object is too large senpai, this will never fit! >///<")
                return 0

        elif out_of_map[0] is True and out_of_map[2] is True:

            # if object could fit when turned, do so, else reject
            if size_x <= self.size_y:
                game_object.turn("ccw")
                return self.add_object(game_object, border_size, recursion_depth+1)
            else:
                print("Error! Object is too large senpai, this will never fit! >///<")
                return 0

        elif out_of_map[0] is True:
            game_object.move([1, 0])
            return self.add_object(game_object, border_size, recursion_depth+1)
        elif out_of_map[1] is True:
            game_object.move([0, 1])
            return self.add_object(game_object, border_size, recursion_depth+1)
        elif out_of_map[2] is True:
            game_object.move([-1, 0])
            return self.add_object(game_object, border_size, recursion_depth+1)
        elif out_of_map[3] is True:
            game_object.move([0, -1])
            return self.add_object(game_object, border_size, recursion_depth+1)
        elif all(item is False for item in out_of_map):
            print("No collision with map boundaries")
        else:
            print("Error! \"out_of_map\" results to:" + str(out_of_map))

        ##########################
        ### collision handling ###
        ##########################

        # collision with other objects?
        for go_pix in game_object.get_drawable():
            if self.unique_pixs[go_pix[1]][go_pix[0]] is not 0:
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
                    
                    just pretend ur drawing a spiral BOI
                '''
                # simple solution: move in random direction
                game_object.move([numpy.random.randint(-10, 10), numpy.random.randint(-10, 10)])
                return self.add_object(game_object, border_size, recursion_depth+1)

        ######################################################### new ##################################################

        # check border
        if border_size > 0:
            for go_pix in Border(obj_type="default", size_x_=game_object.size_x + 2*border_size, size_y_=game_object.size_y + 2*border_size,
                                 pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size]).get_drawable():
                if self.unique_pixs[go_pix[1]][go_pix[0]] is not 0:
                    # simple solution: move in random direction
                    # TODO: apply better solution
                    game_object.move([numpy.random.randint(-10, 10), numpy.random.randint(-10, 10)])
                    return self.add_object(game_object, border_size, recursion_depth+1)

        ################################################################################################################

        # check for duplicate names
        for obj in self.objects:
            if obj.name == game_object.name:
                print("Warning! Adding object with duplicate name!")
                break

        ##############################################
        ### putting it in (be gentle senpai >///<) ###
        ##############################################

        # if everything is statisfied:
        self.objects.append(game_object)
        print("map objects from inside add object" + str(self.objects))

        if debug and border_size > 0:
            self.objects.append(Border(obj_type="default", size_x_=game_object.size_x + 2*border_size,
                                       size_y_=game_object.size_y + 2*border_size,
                                       pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size]))

        # modify unique_pixs
        for go_pix in game_object.get_drawable():
            self.unique_pixs[go_pix[1]][go_pix[0]] = material_codes[game_object.material]

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
        self.unique_pixs = [[0 for _ in range(int(self.size_x))] for _ in range(int(self.size_y))]

    def draw_map(self):  # STATUS: new

        for go in self.objects:
            for pix in go.get_drawable():
                pg.draw.rect(self.window, mat_colour[go.material],
                             (pix[0] * elem_size, pix[1] * elem_size, elem_size, elem_size))
        self.draw_grid()

    def draw_grid(self): # maybe static? (but who cares tbh)

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

map = Map(x/elem_size, y/elem_size, window)

redraw_house = True

# create/draw objects that are independent of user input (if there are any???)

houses = []
h = 0
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

            if h != 0 and map.add_object(h, border_size=0) == 1:
                map.add_object(h, border_size=0)
                houses.append(h)
                house.print_()
            else:
                print("Could not add house")

            print("map objects:" + str(map.objects))
            map.draw_map()
            redraw_house = False

            if debug:
                print()

        pg.display.update()
