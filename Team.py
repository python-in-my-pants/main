import Characters
import Weapon
import numpy as np


class Team:

    id_counter = 0

    def __init__(self, id=0, characters=[]):

        if id:
            self.id = id
        else:
            self.id = self.id_counter
            self.id_counter += 1

        self.characters = characters[:]
        self.value = self.calc_val()

    def add_char(self, char):
        self.characters.append(char)

    def remove_char_by_name(self, name="", pos=[]):  # removes all characters with given name or given position
        for char in self.characters:
            if char.name == name or char.pos == pos:
                self.characters.remove(char)

    def remove_char_by_obj(self, char_obj):
        for char in self.characters:
            if char is char_obj:
                self.characters.remove(char)

    def get_char_by_id(self, id):
        for char in self.characters:
            if char.id == id:
                return char
        return False

    def all_dead(self):

        for char in self.characters:
            if not char.is_dead():
                return False

    def calc_val(self):  # TODO: calculate value by adding cost of all units
        return 1
