import Characters
import Weapon
import numpy as np


class Team:

    def __init__(self, id=0, characters=[]):

        if id:
            self.id = id
        else:
            self.id = np.random.randint(0, 100)

        self.characters = characters[:]
        self.value = self.calc_val()

    def add_char(self, char):
        self.characters.append(char)

    def remove_char_by_name(self, name="", pos=[]):  # removes all characters with given name or given position
        for char in self.characters:
            if char.name == name or char.pos == pos:
                self.characters.remove(char)

    def calc_val(self):  # TODO: calculate value by adding cost of all units
        return 1