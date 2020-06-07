"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer, Christian Loose                                                                        #
#                                                                                                                      #
# Die durch die hier aufgeführten Autoren erstellten Inhalte und Werke unterliegen dem deutschen Urheberrecht.         #
# Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes  #
# bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.                                         #
#                                                                                                                      #
# Die Autoren räumen Dritten ausdrücklich kein Verwertungsrecht an der hier beschriebenen Software oder einer          #
# Kopie/Abwandlung dieser ein.                                                                                         #
#                                                                                                                      #
# Insbesondere untersagt ist das Entfernen und/oder Verändern dieses Hinweises.                                        #
#                                                                                                                      #
# Bei Zuwiderhandlung behalten die Autoren sich ausdrücklich die Einleitung rechtlicher Schritte vor.                  #
#                                                                                                                      #
########################################################################################################################
"""

import random
import functools
from Data import *

'''
TODO Add weight to item classes
'''


class Item:

	def __init__(self, my_id=0, name="default", cost=1, weight=0, stop_bleed=False, hp_regen=False):
		self.my_id = my_id  # class id
		self.name = name
		self.idi = "i" + str(id(self))  # unique id
		self.rand_id = random.randint(0, 1000000000)
		self.cost = cost
		self.weight = weight
		self.stop_bleed = stop_bleed
		self.hp_regen = hp_regen
		self.depletes = True

	def use(self, char, bodypart):  # abstract method
		pass


# <editor-fold desc="Items">
class Bandage(Item):
	"""
	heals selected body part and stops bleeding
	"""

	def __init__(self, my_id=0, name="Bandage", cost=1, heal_multiplier=1.2, weight=0.5):
		super().__init__(my_id, name, cost, weight, stop_bleed=True, hp_regen=True)
		self.heal_multiplier = heal_multiplier

	def use(self, char, bodypart=-1):

		# TODO  should a bandage even be able to heal hp? if not we must assure that each occurring battle can be
		#  foreseen or prevented, e.g. you cannot just be rushed inside a building and be killed, without being able
		#  to defend yourself

		# select part automatically if none was given
		if bodypart == -1:
			if self.hp_regen:
				# bodypart = char.health.index(functools.reduce(lambda a, b: a if 0 < a < b else b, char.health))
				bodypart = 0
				low_h = 1
				for index, h in enumerate(char.health):
					if h / default_hp[index] < low_h:
						bodypart = index
						low_h = h / default_hp[index]
			else:
				if self.stop_bleed:
					bodypart = next(ind for ind, val in enumerate(char.bleed) if val)
				else:
					bodypart = 3  # use on torso

		char.regenerate_hp(self.heal_multiplier, bodypart)
		char.stop_bleeding(bodypart)


class Medkit(Item):

	def __init__(self, my_id=1, name="Medkit", cost=2, heal_multiplier=1.5, weight=1):
		super().__init__(my_id, name, cost, weight, stop_bleed=True, hp_regen=True)
		self.heal_multiplier = heal_multiplier

	def use(self, char, bodypart=-1):

		# select part automatically if none was given
		if bodypart == -1:
			if self.hp_regen:
				# TODO rework, heals head above max
				# bodypart = char.health.index(functools.reduce(lambda a, b: a if 0 < a < b else b, char.health))
				bodypart = 0
				low_h = 1
				for index, h in enumerate(char.health):
					if h/default_hp[index] < low_h:
						bodypart = index
						low_h = h/default_hp[index]
			else:
				if self.stop_bleed:
					bodypart = next(ind for ind, val in enumerate(char.bleed) if val)
				else:
					bodypart = 3  # use on torso

		print("regenerating {} times hp to bodypart {}".format(self.heal_multiplier, bodypart))
		char.regenerate_hp(self.heal_multiplier, bodypart)
		char.stop_bleeding(bodypart)


class Pills(Item):
	"""
	heals whole body hp by 20% but not dead parts
	"""
	def __init__(self, my_id=2, name="Pills", cost=2, heal_multiplier=1.2, weight=0.1):
		super().__init__(my_id, name, cost, weight, hp_regen=True)
		self.heal_multiplier = heal_multiplier

	def use(self, char, bodypart=-1):

		for i in range(6):
			if char.health[i] > 0:
				char.regenerate_hp(self.heal_multiplier, i)


"""class Accudope(Item):
	# TODO Add bool for the dopes if they are active
	def __init__(self, my_id=3, name="Accuracy-Dope", cost=3, modifier=1.25, timer=5, weight=0.1):
		super().__init__(my_id, name, cost, weight)
		self.modifier = modifier
		self.timer = timer


class Stredope(Item):
	def __init__(self, my_id=4, name="Strength-Dope", cost=3, modifier=1.25, timer=5, weight=0.1):
		super().__init__(my_id, name,  cost, weight)
		self.modifier = modifier
		self.timer = timer


class Speeddope(Item):
	def __init__(self, my_id=5, name="Speed-Dope", cost=3, modifier=1.5, timer=5, weight=0.1):
		super().__init__(my_id, name, cost, weight)
		self.modifier = modifier
		self.timer = timer


class Defdope(Item):
	# TODO Change get_damage function to implement defdope
	def __init__(self, my_id=6, name="Defence-Dope", cost=3, timer=5, weight=0.1):
		super().__init__(my_id, name, cost, weight)
		self.timer = timer"""
# </editor-fold>


def make_item_by_id(my_id):
	if my_id == 0: return Bandage()
	if my_id == 1: return Medkit()
	if my_id == 2: return Pills()
	"""if my_id == 3: return Accudope()
	if my_id == 4: return Stredope()
	if my_id == 5: return Speeddope()
	if my_id == 6: return Defdope()"""


class Gear:
	def __init__(self, my_id=0, cost=1, weight=0):
		self.my_id = my_id  # class id and tier id
		self.idi = id(self)  # unique id
		self.cost = cost
		self.weight = weight
		self.rand_id = random.randint(0, 1000000000)


# <editor-fold desc="Gear">
class Helm(Gear):
	def __init__(self, my_id=0, cost=1, durability=0, reduction=0, weight=0):
		super().__init__(my_id, cost, weight)
		self.durability = durability
		self.reduction = reduction

		if self.my_id == 0:
			self.durability = 50
			self.reduction = 0.7
			self.cost = 3
			self.weight = 1
		if self.my_id == 1:
			self.durability = 75
			self.reduction = 0.6
			self.cost = 6
			self.weight = 1.5
		if self.my_id == 2:
			self.durability = 100
			self.reduction = 0.5
			self.cost = 10
			self.weight = 2


class Armor(Gear):
	def __init__(self, my_id=0, cost=1, durability=50, reduction=0.3, weight=0):
		super().__init__(my_id, cost, weight)
		self.durability = durability
		self.reduction = reduction
		if self.my_id == 3:
			self.name = "Armor Lvl 1"
			self.durability = 100
			self.reduction = 0.8
			self.cost = 3
			self.weight = 5
		if self.my_id == 4:
			self.name = "Armor Lvl 2"
			self.durability = 125
			self.reduction = 0.75
			self.cost = 6
			self.weight = 10
		if self.my_id == 5:
			self.name = "Armor Lvl 3"
			self.durability = 150
			self.reduction = 0.7
			self.cost = 10
			self.weight = 15
# </editor-fold>


def make_gear_by_id(my_id):
	if my_id in [0, 1, 2]:
		return Helm(my_id)
	if my_id in [3, 4, 5]:
		return Armor(my_id)
