import Characters
import Weapon
import numpy as np


class Team:

    def __init__(self, characters=[], team_number=0):

        self.team_num = team_number

        self.characters = characters[:]
        self.value = self.calc_val()

    def add_char(self, char):
        # TODO set team of char to this teams id
        self.characters.append(char)

    def remove_char_by_name(self, name="", pos=[]):  # removes all characters with given name or given position
        for char in self.characters:
            if char.name == name or char.pos == pos:
                self.characters.remove(char)

    def remove_char_by_obj(self, char_obj):
        for char in self.characters:
            if char is char_obj:
                self.characters.remove(char)

    def get_index_by_obj(self, chari):

        i = 0
        for char in self.characters:
            if char is chari:
                return i
            i += 1
        return -1

    def get_char_by_class_id(self, class_id):
        for char in self.characters:
            if char.my_id == class_id:
                return char
        return None

    def get_char_by_unique_id(self, unique_id):
        for char in self.characters:
            if char.idi == unique_id:
                return char
        return None

    def all_dead(self):

        for char in self.characters:
            if not char.is_dead():
                return False
        return True

    def calc_val(self):  # TODO: calculate value by adding cost of all units
        val = 0
        for char in self.characters:
            for weap in char.weapons:
                val += weap.cost
            for gear in char.gear:
                val += gear.cost
            for item in char.items:
                val += item.cost

        return val
