import numpy
import sys
from datetime import datetime

import Data


class GameObject:

    name = "Default_name"
    pos = [0,0]
    pixs = []
    type = "default_type"
    material = "default_material"
    id = "-1"

    size_x = 0
    size_y = 0

    def __init__(self, obj_type="default_type", name="default_name", material="default_material", pos=[0,0]):
        self.type = obj_type
        self.name = name
        self.material = material
        self.pos = pos
        self.id = str(datetime.now().time())

    def get_drawable(self):
        pass

    def print(self):
        print(self.name)
        print("Material: " + self.material)
        print("Type: " + self.type)
        print("ID: " + self.id)
        print()


class SimpleHouse(GameObject):

    def __init__(self, obj_type, name="SimpleHouse_def", material_="sandstone", pos=[0,0]):
        super().__init__(obj_type=obj_type, name=name, material=material_, pos=pos)

        # set rdm size for the house
        if self.size_x is 0:
            size_x = numpy.random.randint(3, 10)
        if self.size_y is 0:
            size_y = numpy.random.randint(3, 10)

        self.pixs = []

        # select pixels for walls
        for i in range(size_x):
            self.pixs.append([i, 0])
            self.pixs.append([i, size_y])
        for i in range(size_y):
            self.pixs.append([0, i])
            self.pixs.append([size_x, i])

        self.pixs.append([size_x, size_y])

        # pixs = set(pixs) # soll dopplete Punkte entfernen, aber list ist nicht hashable, muss es aber für set() sein

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

    def get_drawable(self):  # STATUS: tested

        # returns element positions in map coordinates
        return self.pixs
