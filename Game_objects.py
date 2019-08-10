import numpy
import pygame
import sys
import copy
from datetime import datetime

import Data


class GameObject:

    name = "Default_name"
    pos = [0, 0]
    pixs = []
    type = "default_type"
    materials = ["default_material"]  # hold list of all materials of the object
    mat_ind = []  # holds list of indices signaling when new material is used in self.pixs
    id = "-1"

    size_x = 0
    size_y = 0

    def __init__(self, obj_type="default_type", name="default_name", materials=["default_material"], pos=[0, 0], \
                 mat_ind=[]):
        self.type = obj_type
        self.name = name
        self.materials = materials[:]  # make a copy because else python reuses old value for another call
        self.pos = pos[:]
        self.id = str(datetime.now().time())
        self.mat_ind = mat_ind[:]
        self.render_type = "draw"
        self.orientation = 0  # attribute ONLY for render type "blit", has nothing to do  with "turn" method
        self.special_pixs = []  # array for doors etc. with functionality
        self.collider = 0
        self.changed = False # TODO only draw game_objects, if changed is True

    def confirm(self):
        pass

    def move(self, direction):

        self.pos[0] += direction[0]
        self.pos[1] += direction[1]

        for p in self.pixs:
            p[0] += direction[0]
            p[1] += direction[1]
        return self.get_drawable()

    def get_mat_ind(self):

        return self.mat_ind

    def turn(self, direction):

        # turn
        for p in self.pixs:
            if direction == "cw":  # clockwise
                p = [-p[1], p[0]]
            else:
                p = [p[1], -p[0]]

        upper_left_pix = [0, 0]
        lower_right_pix = [0, 0]

        # find upper left and lower right most pixel
        for pix in self.pixs:
            if pix[0] < upper_left_pix[0] and pix[1] < upper_left_pix[1]:
                upper_left_pix[0] = pix[0]
                upper_left_pix[1] = pix[1]
            if pix[0] > lower_right_pix[0] and pix[1] > lower_right_pix[1]:
                lower_right_pix[0] = pix[0]
                lower_right_pix[1] = pix[1]

        # set size of object + border_size accordingly
        self.size_x = lower_right_pix[0] - upper_left_pix[0]
        self.size_y = lower_right_pix[1] - upper_left_pix[1]

        # move object so origin is at upper left pix again
        if direction == "cw":
            for p in self.pixs:
                p[0] += self.size_x
        elif direction == "ccw":
            for p in self.pixs:
                p[1] += self.size_y

        return self.get_drawable()

    def add_elem(self, material, elem):
        pass

    def get_drawable(self):
        pass

    def print_(self):
        print(self.name)
        print("Material: " + self.materials)
        print("Type: " + self.type)
        print("ID: " + self.id)
        print()


class CollAtom(pygame.sprite.Sprite):

    def __init__(self, pos, w=1, h=1, height=1, name="collAtom", opaque=True):
        """"
        pos: gives the position in pixel coordinates like in pixs from GameObject [x,y]
          w: width of the collAtom, usually 1, not intended to be changed
          h: height of the collAtom, usually 1, not intended to be changed
        height: theoretical height of the object in game, used for evaluating visibility
                possible values are: 1 (default), 0.5 (for walls with windows etc.) and so on
        """
        super().__init__()  # pygame.sprite.Sprite
        self.pos = pos
        self.w = w
        self.h = h
        self.height = height
        self.name = name
        self.opaque = opaque

        # print(type(pygame.Rect(self.pos, (w, h))))

        self.rect = pygame.Rect(self.pos, (w, h))


class LineOfSight(GameObject):

    def __init__(self, x, y):
        super().__init__()
        for i in range(x):
            self.pixs.append([x, y])
        self.material = "border"

    def get_drawable(self):
        return self.pixs


class Border(GameObject):

    def __init__(self, obj_type, size_x_, size_y_, name="Border", materials_=["dirt"], pos=[0, 0], thiccness="1"):
        super().__init__(obj_type=obj_type, name=name, materials=materials_, pos=pos)

        self.pixs = []

        self.size_x = size_x_
        self.size_y = size_y_

        # select pixels for walls
        for i in range(self.size_x):
            self.pixs.append([i, 0])
            self.pixs.append([i, self.size_y])
        for i in range(self.size_y):
            self.pixs.append([0, i])
            self.pixs.append([self.size_x, i])

        self.pixs.append([self.size_x, self.size_y])

        # generate inner border recursively
        if thiccness > 1:
            inner_border = Border(["border"], self.size_x-2, self.size_y-2, pos=[1, 1], thiccness=thiccness-1).\
                get_drawable()
            for pix in inner_border:
                self.pixs.append(pix)

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def get_drawable(self):  # STATUS: tested

        # returns element positions in map coordinates
        return self.pixs


class Bush(GameObject):

    def __init__(self, obj_type, name="Bush_def", materials_=["bush"], pos=[0, 0]):
        super().__init__(obj_type=obj_type, name=name, materials=materials_, pos=pos)

        self.pixs = []

        self.pixs.append([0, 0])
        self.pixs.append([0, 1])
        self.pixs.append([1, 0])
        self.pixs.append([1, 1])
        self.pixs.append([0, 2])
        self.pixs.append([1, 2])

        self.size_x = 2
        self.size_y = 3

        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def get_drawable(self):
        return self.pixs


class SimpleHouse(GameObject):

    def __init__(self, obj_type, name="SimpleHouse_def", materials_=["sandstone"], pos=[0, 0]):
        super().__init__(obj_type=obj_type, name=name, materials=materials_, pos=pos)

        # set rdm size for the house
        if self.size_x is 0:
            size_x = numpy.random.randint(5, 10)
        if self.size_y is 0:
            size_y = numpy.random.randint(5, 10)

        self.size_x = size_x
        self.size_y = size_y

        self.pixs = []

        # select pixels for walls
        for i in range(size_x):
            self.pixs.append([i, 0])
            self.pixs.append([i, size_y-1])
        for i in range(size_y):
            self.pixs.append([0, i])
            self.pixs.append([size_x-1, i])

        self.pixs.append([size_x-1, size_y-1])

        # remove doubles
        for pix in self.pixs:
            clone = copy.deepcopy(self.pixs)
            clone.remove(pix)
            while clone.__contains__(pix):
                clone.remove(pix)
                self.pixs.remove(pix)

        # remove door
        door_pos = numpy.random.randint(0, self.pixs.__len__())

        while self.pixs[door_pos] == [0, 0] or self.pixs[door_pos] == [0, self.size_y-1] or \
                self.pixs[door_pos] == [self.size_x-1, 0] or self.pixs[door_pos] == [self.size_x-1, self.size_y-1]:
            door_pos = numpy.random.randint(0, self.pixs.__len__())

        door = self.pixs[door_pos]

        self.pixs.remove(self.pixs[door_pos])

        self.special_pixs.append(door)  # holds stuff like doors and windows

        #  -------------------------------------------------------------------------------------------------------------

        # assign material for door and update mat_ind
        self.add_elem("oak wood", [door])

        # assign material for floor and update mat_ind
        floor = []

        for i in range(size_x-2):
            for j in range(size_y-2):
                floor.append([i+1, j+1])

        self.add_elem("dirt", floor)

        #  -------------------------------------------------------------------------------------------------------------

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def confirm(self):  # is called, when object is put in at final pos on map

        # create collider
        wall = []
        for i in range(self.size_x):
            wall.append([i, 0])
            wall.append([i, self.size_y-1])
        for i in range(self.size_y):
            wall.append([0, i])
            wall.append([self.size_x-1, i])

        wall.append([self.size_x-1, self.size_y-1])

        # TODO: this removes door from collider - comment out to make it wall again
        door = [self.special_pixs[0][0]-self.pos[0], self.special_pixs[0][1]-self.pos[1]]
        wall.remove(door)

        for point in wall:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

        collAtoms = [CollAtom(p, name=("door" if self.special_pixs.__contains__(p) else "wall")) for p in wall]

        self.collider = pygame.sprite.Group()

        for atom in collAtoms:
            atom.add(self.collider)

    def add_elem(self, material, elem_pixs):  # adds new element to pixs and adjusts mat_ind and materials

        self.mat_ind.append(self.pixs.__len__() - 1)
        self.materials.append(material)
        for elem_pix in elem_pixs:
            self.pixs.append(elem_pix)

    def get_drawable(self):  # STATUS: tested

        # returns element positions in map coordinates
        return self.pixs
