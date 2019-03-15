import numpy

import Data


class GameObject:

    _window = 0

    name = "Default_name"
    pixs = []
    type = "default"
    material = "default_material"

    size_x = 0
    size_y = 0

    def __init__(self, window, obj_type="default_type", name="default_name", material="default_material"):
        self._window = window
        self.type = obj_type
        self.name = name

    def get_drawable(self):
        pass


class SimpleHouse(GameObject):

    def __init__(self, wind, obj_type):
        super().__init__(window=wind, obj_type=obj_type)

    def get_drawable(self):

        # set rdm size for the house
        if self.size_x is 0:
            size_x = numpy.random.randint(3,10)
        if self.size_y is 0:
            size_y = numpy.random.randint(3,10)

        # select pixels for walls
        for i in range(size_x):
            self.pixs.append([i,0])
            self.pixs.append([i,size_y])
        for i in range(size_y):
            self.pixs.append([0,i])
            self.pixs.append([size_x,i])

        self.pixs.append([size_x, size_y])

        # pixs = set(pixs) # soll dopplete Punkte entfernen, aber list ist nicht hashable, muss es aber für set() sein

        # adjust pixels to desired position on map
        for point in self.pixs:
            point[0] += self.pos[0]
            point[1] += self.pos[1]

        # returns element positions in map coordinates
        return self.pixs
