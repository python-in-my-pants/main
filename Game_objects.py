import numpy
import sys
import copy
from datetime import datetime

import Data

# comment for pushing into other branch
class bullshit:
    pass

class GameObject:

    name = "Default_name"
    pos = [0, 0]
    pixs = []
    type = "default_type"
    material = "default_material"
    id = "-1"

    size_x = 0
    size_y = 0

    def __init__(self, obj_type="default_type", name="default_name", material="default_material", pos=[0, 0]):
        self.type = obj_type
        self.name = name
        self.material = material
        self.pos = pos
        self.id = str(datetime.now().time())

    def move(self, direction):

        for p in self.pixs:
            p[0] += direction[0]
            p[1] += direction[1]
        return self.get_drawable()

    def turn(self, direction):

        for p in self.pixs:
            if direction == "cw": # clockwise
                p = [-p[1], p[0]]
            else:
                p = [p[1], -p[0]]
        return self.get_drawable()

    def get_drawable(self):
        pass

    def print_(self):
        print(self.name)
        print("Material: " + self.material)
        print("Type: " + self.type)
        print("ID: " + self.id)
        print()


class Border(GameObject):

    def __init__(self, obj_type, size_x_, size_y_, name="Border", material_="default", pos=[0,0]):
        super().__init__(obj_type=obj_type, size_x=size_x_, size_y=size_y_, name=name, material=material_, pos=pos)

        self.pixs = []

        # select pixels for walls
        for i in range(self.size_x):
            self.pixs.append([i, 0])
            self.pixs.append([i, self.size_y])
        for i in range(self.size_y):
            self.pixs.append([0, i])
            self.pixs.append([self.size_x, i])

        self.pixs.append([self.size_x, self.size_y])

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def get_drawable(self):  # STATUS: tested

        # returns element positions in map coordinates
        return self.pixs


class SimpleHouse(GameObject):

    def __init__(self, obj_type, name="SimpleHouse_def", material_="sandstone", pos=[0,0]):
        super().__init__(obj_type=obj_type, name=name, material=material_, pos=pos)

        # set rdm size for the house
        if self.size_x is 0:
            size_x = numpy.random.randint(3, 10)
        if self.size_y is 0:
            size_y = numpy.random.randint(3, 10)

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

        self.pixs.remove(self.pixs[door_pos])

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def get_drawable(self):  # STATUS: tested

        # returns element positions in map coordinates
        return self.pixs
