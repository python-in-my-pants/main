# encoding: UTF-8

import pygame as pg
from pygame.locals import *
from skimage.draw import line_aa
import numpy as np
import sys

from Game_objects import *
from Data import *
from Characters import Character

debug = True

# TODO: Nur Map wird gezeichnet und ist ein container für alle anderen drawables, Änderungen an drawables werden \
#       durchgeführt und diese dann erneut Map hinzugefügt, die alten gelöscht


class Map(GameObject):  # TODO add selective renderer that renders only visible characters from own team
                        # TODO maybe dont inherit from GObj
    # container class for all other drawable game objects

    '''
    # unique_pixs = []  # holds definite pixel(materials) that will be drawn
    objects = []  # holds list of objects on the map of the form: [id, object]
    characters = []
    # window = -1
    '''

    def __init__(self, x_size, y_size, window, elem_size, objects=[], characters=[], unique_pixels=[]):  # STATUS: working, returns 1 on success, 0 else

        # size_x holds map size in actual drawable pixels coords, x and y are to be
        # committed in desired size in elements * elem_size
        self.size_x = x_size
        self.size_y = y_size

        self.starting_areas = []  # holds lists [a,b,c,d]

        # beware, when using you have to call [y][x]
        if not unique_pixels:
            self.unique_pixs = [[0 for _ in range(int(x_size))] for _ in range(int(y_size))]
        else:
            self.unique_pixs = unique_pixels[:]

        self.window = window
        self.elem_size = elem_size

        # just testing stuff 11072019 1511
        self.objects = objects[:]           # holds list of objects on the map of the form: [id, object]
        self.characters = characters[:]     # holds indices of objects[] of characters

    def set_elem_size(self, elem_size):
        self.elem_size = elem_size

    def add_object(self, game_object, border_size=0, recursion_depth=0, permutation_lenght=[0, 0]):  # STATUS: partially working, border
        # stuff not yet, crashes when too deep recursion occurs

        """
                  "out of map bounds" leads to shifting to object until either it is in the map or abortion
        "collision with other object" leads to shifting to object until either no collision is occurring or abortion

        :param game_object: the object to add
        :param border_size: optional border around the object to sustain accessability of buildings etc.
        :return: 1 on success, 0 else
        """

        # check for too deep recursion, may remove this when better collision handling is in place
        if recursion_depth > 100:
            print("Cannot fit object")
            return 0
        else:
            recursion_depth += 1

        #########################
        ### check object size ###
        #########################

        # get height of object
        size_x = game_object.size_x + 2 * border_size
        size_y = game_object.size_y + 2 * border_size

        if size_x > self.size_x - 1 or size_y > self.size_y - 1:
            print("Error! Object is too large senpai ... >///<")
            return 0

        ##############################
        ### out of bounds handling ###
        ##############################

        #             left   top    right  bottom
        out_of_map = [False, False, False, False]

        # check if border would be out of map
        if border_size > 0:
            for pix in Border(obj_type="default", size_x_=size_x, size_y_=size_y,
                              pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size],
                              thiccness=border_size).get_drawable():
                if pix[0] < 0:
                    out_of_map[0] = True
                elif pix[1] < 0:
                    out_of_map[1] = True
                elif pix[0] > self.size_x - 1:
                    out_of_map[2] = True
                elif pix[1] > self.size_y - 1:
                    out_of_map[3] = True

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

        '''
        if out_of_map[0]:
            print("Warning! Game object would be out of bounds (left)!\n")
        elif out_of_map[1]:
            print("Warning! Game object would be out of bounds (top)!\n")
        elif out_of_map[2]:
            print("Warning! Game object would be out of bounds (right)!\n")
        elif out_of_map[3]:
            print("Warning! Game object would be out of bounds (bottom)!\n")
        '''

        # handle different collisions
        if out_of_map[0] is True and out_of_map[1] is True and out_of_map[2] is True and out_of_map[3] is True:
            print("Error! Object is too large senpai ... >///<")
            return 0
        elif out_of_map[1] is True and out_of_map[3] is True:

            # if object could fit when turned, do so, else reject
            if size_y <= self.size_x:
                game_object.turn("cw")
                return self.add_object(game_object, border_size, recursion_depth)
            else:
                print("Error! Object is too large senpai, this will never fit! >///<")
                return 0

        elif out_of_map[0] is True and out_of_map[2] is True:

            # if object could fit when turned, do so, else reject
            if size_x <= self.size_y:
                game_object.turn("ccw")
                return self.add_object(game_object, border_size, recursion_depth)
            else:
                print("Error! Object is too large senpai, this will never fit! >///<")
                return 0

        elif out_of_map[0] is True:
            game_object.move([1, 0])
            return self.add_object(game_object, border_size, recursion_depth)
        elif out_of_map[1] is True:
            game_object.move([0, 1])
            return self.add_object(game_object, border_size, recursion_depth)
        elif out_of_map[2] is True:
            game_object.move([-1, 0])
            return self.add_object(game_object, border_size, recursion_depth)
        elif out_of_map[3] is True:
            game_object.move([0, -1])
            return self.add_object(game_object, border_size, recursion_depth)
        elif all(item is False for item in out_of_map):
            pass
            # print("No collision with map boundaries")
        else:
            print("Error! \"out_of_map\" results to:" + str(out_of_map))

        ##########################
        ### collision handling ###
        ##########################

        # collision with characters should happen with colliders, not pixels of objects
        if game_object.type == "character":

            for obj in self.objects:
                if obj.collider != 0:

                    # use new sprite group for collision, because using game_objects could result in false results after
                    # moving the object (sprites are NOT moved by GameObject methods!)
                    for collAtom in pg.sprite.Group(CollAtom(
                            game_object.pos)).sprites():  # TODO: adjust so that laying characters are handled with 2 sprites
                        if pg.sprite.spritecollide(collAtom, obj.collider, dokill=0):
                            # collision with other char occurs
                            game_object.move([numpy.random.randint(-1, 1), numpy.random.randint(-1, 1)])
                            return self.add_object(game_object, border_size, recursion_depth)

        else:

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
                    return self.add_object(game_object, border_size, recursion_depth)

        # check border
        if border_size > 0:
            for go_pix in Border(obj_type="default", size_x_=size_x - 1, size_y_=size_y - 1,
                                 pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size], \
                                 thiccness=border_size).get_drawable():
                if self.unique_pixs[go_pix[1]][go_pix[0]] is not 0:
                    # simple solution: move in random direction
                    # TODO: apply better solution
                    game_object.move([numpy.random.randint(-10, 10), numpy.random.randint(-10, 10)])
                    return self.add_object(game_object, border_size, recursion_depth)

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
        if game_object.type == "character":
            self.characters.append(self.objects.__len__() - 1)

        if border_size > 0:
            self.objects.append(Border(obj_type="default", size_x_=size_x - 1, size_y_=size_y - 1,
                                       pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size], \
                                       thiccness=border_size))

        # modify unique_pixs TODO because new
        for index, go_pix in enumerate(game_object.get_drawable()):
            mat_counter = 0
            if game_object.mat_ind:
                if index > game_object.mat_ind[mat_counter]:
                    mat_counter += 1
            self.unique_pixs[go_pix[1]][go_pix[0]] = material_codes[game_object.materials[mat_counter]]

        game_object.confirm()

        return 1

    def movement_possible(self, char, new_pos):  # returns true or false

        if new_pos[0] < 0 or new_pos[0] > self.size_x-1 or new_pos[1] < 0 or new_pos[1] > self.size_y-1:
            print("out of map")
            return False

        for obj in self.objects:
            if obj.collider != 0 and obj is not char:
                # use new sprite group for collision, because using game_objects could result in false results after
                # moving the object (sprites are NOT moved by GameObject methods!)
                for collAtom in pg.sprite.Group(CollAtom(new_pos)).sprites():
                    # TODO: adjust so that laying characters are handled with 2 sprites
                    if pg.sprite.spritecollide(collAtom, obj.collider, dokill=0):
                        # collision with other char occurs
                        print("collision with other collidable object")
                        return False

        '''if self.unique_pixs[new_pos[1]][new_pos[0]] != 0:
            print("coll with some obj")
            return False'''

        return True

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

    @staticmethod
    def get_vmat(self):  # TODO: character height, laying characters hitbox etc

        # TODO return visibility matrix containing visibility for every char on the map
        chars = []
        for ind, obj in enumerate(self.objects):
            if self.characters.__contains__(ind):
                chars.append(obj)

        mat = [[[1, 1] for _ in range(chars.__len__())] for _ in range(chars.__len__())]

        for ind1, char1 in enumerate(chars):
            for ind2, char2 in enumerate(chars):
                if char1 is not char2:

                    line_gr = pg.sprite.Group()  # line group

                    # TODO maybe try switching x,y
                    #  AND try line()
                    y_coord, x_coord, _ = line_aa(char1.pos[1], char1.pos[0], char2.pos[1],
                                                  char2.pos[0])  # y1, x1, y2, x2

                    for index in range(y_coord.__len__()):
                        CollAtom([x_coord[index], y_coord[index]], name="line").add(line_gr)

                    mat[ind1][ind2] = self.get_mat_x_y(line_gr, char1, char2)

        return mat

    def get_mat_x_y(self, line_gr, char1, char2):

        for obj in self.objects:

            if obj.collider and obj is not char1 and obj is not char2:
                colliding_objs = pg.sprite.groupcollide(line_gr, obj.collider, dokilla=False, dokillb=False)

                if colliding_objs:

                    for key in colliding_objs:
                        if key.opaque or colliding_objs[key].opaque:
                            return [0, 0]  # cannot see, cannot shoot

                    return [1, 0]  # can see, cannot shoot

        return [1, 1]  # can see & shoot

    def draw_map(self):  # STATUS: new

        for go in self.objects:
            if go.render_type == "blit":
                if go.is_selected is True:
                    go.orientation = go.orientation  # TODO: look at mouse OR at char to attack
                go_surf = go.get_drawable_surf()
                if go.orientation > 0:
                    go_surf = pg.transform.rotate(go_surf, go.orientation)
                factor = ((numpy.sqrt(2) - 1) / 2) * numpy.sin(3.5 * numpy.pi + 4 * numpy.deg2rad(go.orientation)) + \
                         ((numpy.sqrt(2) - 1) / 2) + 1
                factor = 1
                self.window.blit(pg.transform.smoothscale(go_surf, (int(self.elem_size * factor), int(self.elem_size * factor))), \
                                 (int(go.pos[0] * self.elem_size), int(go.pos[1] * self.elem_size)))
                #shit = pg.transform.smoothscale(go_surf, (int(self.elem_size * factor), int(self.elem_size * factor)))
                # print("-"*10+str(shit.get_width()))
            else:
                mat_counter = 0
                for index, pix in enumerate(go.get_drawable()):
                    if go.mat_ind:
                        if mat_counter < go.mat_ind.__len__() and index > go.mat_ind[mat_counter]:
                            mat_counter += 1
                    pg.draw.rect(self.window, mat_colour[go.materials[mat_counter]],
                                 (pix[0] * self.elem_size, pix[1] * self.elem_size, self.elem_size, self.elem_size))
        self.__draw_grid()

    def __draw_grid(self):  # maybe static? (but who cares tbh)

        '''for i in range(int(self.size_x/elem_size)):
            for d in range(int(self.size_y/elem_size)):
                pg.draw.rect(get_window(), (0, 99, 0), (i*elem_size, d*elem_size, elem_size, elem_size), 1)'''

        for i in range(self.size_x):
            for d in range(self.size_y):
                pg.draw.rect(self.window, (0, 99, 0), (i * self.elem_size, d * self.elem_size, self.elem_size, self.elem_size), 1)

    def get_map(self):  # return all data from map BUT NOT self.window

        lis = [self.unique_pixs,
               self.objects,
               self.characters,
               self.size_x,
               self.size_y]

        return lis


class MapBuilder:

    def __init__(self):
        self.map = None

    def build_map(self, size=30):

        # build map without characters
        surf = pg.Surface([500, 500])
        elem_size = 25

        fields_x = fields_y = size

        self.map = Map(x_size=size, y_size=size, window=surf, elem_size=elem_size)

        # ------------------------------------------------------------------------------------------------------------

        self.map.window.fill((23, 157, 0))

        # add spawns

        areas = Spawnarea.create_areals([size, size])  # TODO

        for area in areas:
            self.map.add_object(area)

        # add houses

        house_limit = 5 #int((size*size) / 25)
        house_counter = 0

        for i in range(house_limit):

            h = SimpleHouse(name=("Simple house " + str(house_counter)), obj_type="default", \
                            pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])

            # while there is a house (to add) and it does not fit and you did not try 100 times yet generate a new one
            limit = 0
            while h != 0 and self.map.add_object(h, border_size=1) != 1 and limit < 100:
                h = SimpleHouse(name=("Simple house " + str(house_counter)), obj_type="default", \
                                pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])
                limit += 1

            if limit >= 100:
                print("Could not place another object")
            else:
                house_counter += 1

        # add bushes

        bush_limit = 5 #int((size*size)/15)
        bush_counter = 0

        for i in range(bush_limit):

            h = Bush(name=("Simple bush " + str(bush_counter)), obj_type="default", \
                     pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])

            # while there is a house (to add) and it doesn't fit and you didn't try 100 times yet generate a new one
            limit = 0
            while h != 0 and self.map.add_object(h, border_size=1) != 1 and limit < 100:
                h = Bush(name=("Simple bush " + str(bush_counter)), obj_type="default", \
                         pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])
                limit += 1

            if limit >= 100:
                print("Could not place another object")
            else:
                bush_counter += 1

        # draw everything to surf

        self.map.draw_map()
        return self.map

    def populate(self, team):
        # add all team members to characters
        for char in team.characters:

            self.map.add_object(char)

