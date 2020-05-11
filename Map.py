# encoding: UTF-8

import pygame as pg
from pygame.locals import *
from skimage.draw import line_aa, line
import hashlib
import numpy as np
import sys

from Game_objects import *
from Data import *
from Weapon import *
from Characters import Character

debug = True


class Map(GameObject):  # TODO maybe dont inherit from GObj
    # container class for all other drawable game objects

    def __init__(self, x_size, y_size, window=None, objects=[], characters=[], unique_pixels=[]):

        # size_x holds map size in actual drawable pixels coords, x and y are to be
        # committed in desired size in elements * elem_size
        self.size_x = x_size
        self.size_y = y_size
        self.base_map = None

        if not window:
            self.window = pg.Surface([x_size*def_elem_size, y_size*def_elem_size])
        else:
            self.window = window

        self.starting_areas = []  # holds lists [a,b,c,d]

        # beware, when using you have to call [y][x]
        if not unique_pixels:
            self.unique_pixs = [[0 for _ in range(int(x_size))] for _ in range(int(y_size))]
        else:
            self.unique_pixs = unique_pixels[:]

        # just testing stuff 11072019 1511
        self.objects = objects[:]           # holds list of objects on the map of the form: [id, object]
        self.characters = characters[:]     # holds indices of objects[] of characters

        # ToDo Texture Stuff, implement flooring for ruined difference
        texture_size = (def_elem_size, def_elem_size)
        self.texture_dump = [pg.transform.scale(pg.image.load(grass_texture), texture_size),
                             pg.transform.scale(pg.image.load(sandstone_texture), texture_size),
                             pg.transform.scale(pg.image.load(border_texture), texture_size),
                             pg.transform.scale(pg.image.load(house_floor_texture), texture_size),
                             pg.transform.scale(pg.image.load(flooring_texture), texture_size),
                             pg.transform.scale(pg.image.load(bush_texture), texture_size),
                             None,
                             pg.transform.scale(pg.image.load(boulder_texture), texture_size),
                             pg.transform.scale(pg.image.load(ruin_floor_texture), texture_size)]

    def add_object(self, game_object, border_size=0, recursion_depth=0):  # STATUS: partially working, border
        # stuff not yet, crashes when too deep recursion occurs

        """
                  "out of map bounds" leads to shifting to object until either it is in the map or abortion
        "collision with other object" leads to shifting to object until either no collision is occurring or abortion

        :param game_object: the object to add
        :param border_size: optional border around the object to sustain accessibility of buildings etc.
        :param recursion_depth: limits attempts to fit a certain object in
        :return: 1 on success, 0 else
        """

        # check for too deep recursion, may remove this when better collision handling is in place
        if recursion_depth > 100:
            return 0
        else:
            recursion_depth += 1

        #########################
        ### check object size ###
        #########################

        # get dims of object
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

        border = Border(obj_type="default", size_x_=size_x, size_y_=size_y,
                        pos=[game_object.pos[0] - border_size, game_object.pos[1] - border_size], thiccness=border_size)

        # check if border would be out of map
        if border_size > 0:
            for pix in border.get_drawable():
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
                game_object.rotate("cw")
                return self.add_object(game_object, border_size, recursion_depth)
            else:
                print("Error! Object is too large senpai, this will never fit! >///<")
                return 0

        elif out_of_map[0] is True and out_of_map[2] is True:

            # if object could fit when turned, do so, else reject
            if size_x <= self.size_y:
                game_object.rotate("ccw")
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
                if obj.collider:

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
            for go_pix in border.get_drawable():
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
            # TODO comment this out to make borders not render
            pass
            # self.objects.append(border)

        # modify unique_pixs
        for index, go_pix in enumerate(game_object.get_drawable()):
            mat_counter = 0
            if game_object.mat_ind:
                if index > game_object.mat_ind[mat_counter]:
                    mat_counter += 1
            self.unique_pixs[go_pix[1]][go_pix[0]] = material_codes[game_object.materials[mat_counter]]

        game_object.confirm()

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

    def get_vmat(self):  # TODO: character height, laying characters hitbox etc ... NO :)

        """
        :param self:
        :return: matrix of [a, b]s as the entries where a indicates that char1 can see char2 and b that he can shoot him
        """

        # build char list
        chars = []
        for ind, obj in enumerate(self.objects):
            if self.characters.__contains__(ind):
                chars.append((ind, obj))

        v_dict = dict()

        for ind1, char1 in chars:
            for ind2, char2 in chars:
                if char1 is not char2:

                    line_gr = pg.sprite.Group()  # line group

                    # todo try line(), was line aa
                    """y_coord, x_coord, _ = line_aa(char1.pos[1], char1.pos[0],
                                                  char2.pos[1], char2.pos[0])  # y1, x1, y2, x2"""

                    y_coord, x_coord = line(char1.pos[1], char1.pos[0],
                                            char2.pos[1], char2.pos[0])  # y1, x1, y2, x2

                    for index in range(y_coord.__len__()):
                        CollAtom([x_coord[index], y_coord[index]], name="line").add(line_gr)

                    v_dict[(ind1, ind2)] = self.__get_mat_x_y(line_gr, char1, char2)
                else:
                    v_dict[(ind1, ind2)] = [1, 1]

        return v_dict

    # tells if line of sight between 2 chars collides with objects in world
    def __get_mat_x_y(self, line_gr, char1, char2):  # line group

        for obj in self.objects:

            if obj.collider and obj is not char1 and obj is not char2:
                colliding_objs = pg.sprite.groupcollide(line_gr, obj.collider, dokilla=False, dokillb=False)

                if colliding_objs:

                    for key in colliding_objs:
                        if key.opaque or colliding_objs[key].opaque:
                            return [0, 0]  # cannot see, cannot shoot

                    return [1, 0]  # can see, cannot shoot

        return [1, 1]  # can see & shoot

    def get_reachable_fields(self, char):
        pos_w, pos_h = char.pos
        max_dist = (char.speed/5)**2
        mov_range = int((char.speed / 5) * 1.5 + 0.5)

        reachable = [(pos_w, pos_h)]
        checked = set()
        counter = 0

        while counter < mov_range:
            my_set = set(reachable)-checked
            for r in list(my_set):
                neigh = self.get_neighbours(r[0], r[1])
                for n in neigh:
                    if self.movement_possible(char, [n[0], n[1]]) and \
                            (n[0]-char.pos[0])**2 + (n[1]-char.pos[1])**2 <= max_dist:
                        reachable.append(tuple(n))
                checked.add(r)
            counter += 1

        return list(set(reachable) - {(pos_w, pos_h)})  # own position is not reachable

    def get_distance(self, pos1, pos2):  # TODO use euclidean dist instead of manhattan
        if pos1 == pos2:
            return 0

        pos_w, pos_h = pos1

        reachable = [(pos_w, pos_h)]
        checked = set()
        counter = 0

        while True:
            my_set = set(reachable)-checked
            for r in list(my_set):
                neigh = self.get_neighbours(r[0], r[1])
                for n in neigh:
                    if self.movement_possible(pos1, [n[0], n[1]]):
                        reachable.append(tuple(n))
                    if n == pos2:
                        return counter
                checked.add(r)
            counter += 1

    def get_path(self, start, end):

        start = tuple(start)
        end = tuple(end)

        class Node:
            """A node class for A* Pathfinding"""

            def __init__(self, parent=None, position=None):
                self.parent = parent
                self.position = position

                self.g = 0
                self.h = 0
                self.f = 0

            def __eq__(self, other):
                return self.position == other.position

        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        # create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0

        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # initialize both open and closed list
        open_list = []
        closed_list = []

        # add the start node
        open_list.append(start_node)

        # loop until you find the end
        while len(open_list) > 0:

            # get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # found the goal
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Return reversed path

            # generate children
            children = []
            for new_position in self.get_neighbours(*current_node.position):  # adjacent squares

                # get node position
                node_position = tuple(new_position)

                # make sure within range
                if not self.check_valid_list(node_position) or\
                   not self.movement_possible_pos(current_node.position, node_position):
                    continue

                # create new node
                new_node = Node(current_node, node_position)

                # append
                children.append(new_node)

            # loop through children
            for child in children:

                # child is on the closed list
                for closed_child in closed_list:
                    if child == closed_child:
                        continue

                # create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0]) ** 2) + \
                          ((child.position[1] - end_node.position[1]) ** 2)
                child.f = child.g + child.h

                # child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # add the child to the open list
                open_list.append(child)

    def movement_possible(self, char, new_pos):  # takes a char and the destination as inputs

        if new_pos[0] < 0 or new_pos[0] > self.size_x-1 or new_pos[1] < 0 or new_pos[1] > self.size_y-1:
            return False

        objs_at_pos = self.get_objs_at(new_pos)
        for obj in objs_at_pos:
            if obj.collider:  # it has a collider and is not the moving char
                # use new sprite group for collision, because using game_objects could result in false results after
                # moving the object (sprites are NOT moved by GameObject methods!)
                for collAtom in pg.sprite.Group(CollAtom(new_pos)).sprites():
                    # TODO: adjust so that laying characters are handled with 2 sprites ... No :)
                    if pg.sprite.spritecollide(collAtom, obj.collider, dokill=0):
                        # collision occurs
                        return False

        return True

    def movement_possible_pos(self, old_pos, new_pos):  # takes old and new pos as inputs

        if new_pos[0] < 0 or new_pos[0] > self.size_x-1 or new_pos[1] < 0 or new_pos[1] > self.size_y-1:
            return False

        objs_at_pos = self.get_objs_at(new_pos)
        for obj in objs_at_pos:
            if obj.collider:  # it has a collider and is not the moving char
                # use new sprite group for collision, because using game_objects could result in false results after
                # moving the object (sprites are NOT moved by GameObject methods!)
                for collAtom in pg.sprite.Group(CollAtom(new_pos)).sprites():
                    # TODO: adjust so that laying characters are handled with 2 sprites ... No :)
                    if pg.sprite.spritecollide(collAtom, obj.collider, dokill=0):
                        # collision with other char occurs
                        return False

        return True

    def get_objs_at(self, pos):
        # does the sprite group of the object (aka collider)
        # contain a collision atom (inherits from sprite) with pos=[x,y]?

        def pos_in_rect(_pos, r_start, r_x, r_y):
            return r_start[0] <= _pos[0] <= r_start[0]+r_x or \
                   r_start[1] <= _pos[1] <= r_start[1]+r_y

        # mapping of pixels to objects

        objects_at_pos = []
        # check which object is present at this pos
        for o in self.objects:
            if o.collider:  # check only for objects that may collide
                if pos_in_rect(pos, o.pos, o.size_x, o.size_y):
                    objects_at_pos.append(o)

        return objects_at_pos

    def get_neighbours(self, x, y):

        neigh = [[x, y-1],
                 [x, y+1],
                 [x-1, y],
                 [x+1, y]]

        to_ret = []

        for n in neigh:
            if self.check_valid_list(n):
                to_ret.append(n)

        return to_ret

    def check_valid(self, x, y):  # check if coords are inside map bounds

        if 0 <= x <= self.size_x-1 and 0 <= y <= self.size_y-1:
            return True
        else:
            return False

    def check_valid_list(self, pos):

        return self.check_valid(pos[0], pos[1])

    def draw_map(self):  # STATUS: new

        for i in range(self.size_x):
            for d in range(self.size_y):
                self.window.blit(self.texture_dump[0], (i * def_elem_size, d * def_elem_size))

        for go in self.objects:
            if go.render_type == "blit":  # it is a character
                if go.is_selected is True:
                    go.orientation = go.orientation  # TODO: look at mouse OR at char to attack
                go_surf = go.get_drawable_surf()
                if go.orientation > 0:
                    go_surf = pg.transform.rotate(go_surf, go.orientation)

                self.window.blit(pg.transform.smoothscale(go_surf, (int(def_elem_size), int(def_elem_size))),
                                 (int(go.pos[0] * def_elem_size), int(go.pos[1] * def_elem_size)))

            if go.materials == ["bush"]:
                self.window.blit(pg.transform.scale(pg.image.load(bush_types[go.type]), (go.size_x * def_elem_size,
                                                                                         go.size_y * def_elem_size)),
                                 (go.pixs[0][0] * def_elem_size, go.pixs[0][1] * def_elem_size))
            elif go.materials == ["puddel"]:
                self.window.blit(pg.transform.scale(pg.image.load(puddel_types[go.type]), (go.size_x * def_elem_size,
                                                                      go.size_y * def_elem_size)),
                                 (go.pixs[0][0] * def_elem_size, go.pixs[0][1] * def_elem_size))
            elif go.materials == ["boulder"]:
                self.window.blit(pg.transform.scale(pg.image.load(boulder_types[go.type]), (go.size_x * def_elem_size,
                                                                                            go.size_y * def_elem_size)),
                                 (go.pixs[0][0] * def_elem_size, go.pixs[0][1] * def_elem_size))
            elif go.materials == ["oak wood"]:
                self.window.blit(pg.transform.scale(pg.image.load(tree_types[go.type]), ((go.size_x + 2) * def_elem_size,
                                                                     (go.size_y + 2) * def_elem_size)),
                                 ((go.pixs[0][0] - 1) * def_elem_size, (go.pixs[0][1] - 1) * def_elem_size))

            else:
                mat_counter = 0
                for index, pix in enumerate(go.get_drawable()):
                    if go.mat_ind:
                        if mat_counter < go.mat_ind.__len__() and index > go.mat_ind[mat_counter]:
                            mat_counter += 1
                    self.window.blit(self.texture_dump[material_codes[go.materials[mat_counter]]],
                                     (pix[0] * def_elem_size, pix[1] * def_elem_size))

        self.__draw_grid()
        self.base_map = self.window.copy()

    def get_visible_chars_ind(self, team_num):  # TODO implement looking direction

        v_dict = self.get_vmat()

        own_chars = []  # holds indices of own team in objects
        visible_chars = []  # holds indices of visible chars

        for i in self.characters:
            if self.objects[i].team == team_num:
                own_chars.append(i)

        for own_char_index in own_chars:
            for other_char_index in self.characters:
                if v_dict[(own_char_index, other_char_index)][0] == 1\
                        and not own_chars.__contains__(other_char_index) \
                        and not visible_chars.__contains__(other_char_index):
                    visible_chars.append(other_char_index)

        for c in own_chars:
            visible_chars.append(c)

        return visible_chars

    def get_char_index(self, char):
        for char_index in self.characters:
            if self.objects[char_index].rand_id == char.rand_id:
                return char_index

    def selective_draw_map(self, team_num):

        self.window.blit(self.base_map, (0, 0))

        visible_chars = self.get_visible_chars_ind(team_num=team_num)
        # pg.image.load("assets/Teams/Red_Team/"+character_classes[go.class_id]+"/Red_"+character_classes[go.class_id]+
        #                          "_Pistol.png")
        # pg.image.load("assets/Teams/Blue_Team/"+character_classes[go.class_id]+"/Blue_"+character_classes[go.class_id]+
        #                          "_Pistol.png")
        for index, go in enumerate(self.objects):
            if go.render_type == "blit":  # character
                if visible_chars.__contains__(index):
                    if go.is_dead():
                        go_surf = pg.image.load("assets/textures/Teams/dead_char.png")
                    else:
                        if go.team == 0:
                            if isinstance(go.active_slot, Weapon):
                                go_surf = pg.image.load("assets/textures/teams/Blue_Team/" + character_classes[go.class_id] + "/Blue_" +
                                                        character_classes[go.class_id] + "_" + go.active_slot.name + ".png")
                            else:
                                go_surf = pg.image.load("assets/textures/teams/Blue_Team/" + character_classes[go.class_id] + "/Blue_" +
                                                        character_classes[go.class_id] + ".png")
                        if go.team == 1:
                            if isinstance(go.active_slot, Weapon):
                                go_surf = pg.image.load("assets/textures/teams/Red_Team/" + character_classes[go.class_id] + "/Red_" +
                                                        character_classes[go.class_id] + "_" + go.active_slot.name + ".png")
                            else:
                                go_surf = pg.image.load("assets/textures/teams/Red_Team/" + character_classes[go.class_id] + "/Red_" +
                                                        character_classes[go.class_id] + ".png")
                        # go_surf = go.get_drawable_surf()
                        if go.orientation > 0:
                            go_surf = pg.transform.rotate(go_surf, go.orientation)

                    self.window.blit(
                        pg.transform.smoothscale(go_surf,               # surface to blit
                                                 (def_elem_size, def_elem_size)),
                                                (int(go.pos[0] * def_elem_size),           # destination
                                                 int(go.pos[1] * def_elem_size)))

    def __draw_grid(self):  # maybe static? (but who cares tbh)

        for i in range(self.size_x):
            for d in range(self.size_y):
                pg.draw.rect(self.window, (30, 30, 20), (i * def_elem_size, d * def_elem_size,
                                                         def_elem_size, def_elem_size), 1)

    def get_map(self):  # return all data from map BUT NOT self.window

        lis = [self.unique_pixs,
               self.objects,
               self.characters,
               self.size_x,
               self.size_y]  # encode self.window as string and rebuild surface from this

        return lis

    def get_ident(self):
        return hashlib.sha1(self.get_map())

    @staticmethod
    def combine_map(_map, team1, team2):
        for char in team1.characters:
            _map.objects[0].place_character(char)
        for char in team2.characters:
            _map.objects[1].place_character(char)
        return _map


class MapBuilder:

    def __init__(self):
        self.map = None

    def build_map(self, size=30, encode_surf=False):

        # build map without characters
        fields_x = fields_y = size
        self.map = Map(x_size=fields_x, y_size=fields_y)

        # add spawns
        areas = Spawnarea.create_areas([fields_x, fields_y])

        # areas are the first game_objects
        for area in areas:
            self.map.add_object(area)

        # buildings
        house_limit = int((fields_x*fields_y) / 300)
        ruins_limit = int((fields_x*fields_y) / 300)

        # nature
        bush_limit = int((fields_x*fields_y) / 150)
        boulder_limit = int((fields_x*fields_y) / 150)
        tree_limit = int((fields_x*fields_y) / 150)
        puddel_limit = int((fields_x*fields_y / 150))

        if True:
            house_limit = ruins_limit = bush_limit = boulder_limit = tree_limit = puddel_limit = 0

        def add_obj(obj_class, obj_limit):

            obj_counter = 0
            for i in range(obj_limit):

                h = obj_class(name=(obj_class.__name__ + " " + str(obj_counter)), obj_type=obj_class.__name__,
                              pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])

                # while there is a house (to add) and it does not fit and you did not try 100 times yet
                # generate a new one
                limit = 0
                while h != 0 and self.map.add_object(h, border_size=1) != 1 and limit < 100:
                    h = SimpleHouse(name=(obj_class.__name__ + " " + str(obj_counter)), obj_type=obj_class.__name__,
                                    pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])
                    limit += 1

                if limit >= 100:
                    # print("Could not place another object")
                    pass
                else:
                    obj_counter += 1

        add_obj(SimpleHouse, house_limit)
        add_obj(Ruins, ruins_limit)
        add_obj(Bush, bush_limit)
        add_obj(Puddle, puddel_limit)
        add_obj(Boulder, boulder_limit)
        add_obj(Tree, tree_limit)

        # draw everything to surf
        self.map.draw_map()
        return self.map

    def populate(self, team):
        # add all team members to characters
        for char in team.characters:
            self.map.add_object(char)

