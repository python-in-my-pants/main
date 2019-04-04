import random

'''
TODO 
in CHARACTER: 
	Change way of Item deletion from pop to remove
in ITEMS:   
	Add weight to item classes
'''


class Item:
	idi = 0
	name = "default"
	
	def __init__(self, name="default", idi=0):
		self.name = name
		self.idi = idi


class Bandage(Item):
	def __init__(self, name="Bandage", idi=random.randint(1, 100), value=25):
		super().__init__(name, idi)
		self.value = value


class Medkit(Item):
	def __init__(self, name="Medkit", idi=random.randint(101, 200), value=75):
		super().__init__(name, idi)
		self.value = value


class Healstation(Item):
	# TODO Implement heal on more than one bodypart
	def __init__(self, name="Healstation", idi=random.randint(201, 300), value=50):
		super().__init__(name, idi)
		self.value = value


class Accudope(Item):
	# TODO Add bool for the dopes if they are active
	def __init__(self, name="Accuracy-Dope", idi=random.randint(501, 600), modifier=1.25, timer=5):
		super().__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Stredope(Item):
	def __init__(self, name="Strength-Dope", idi=random.randint(601, 700), modifier=1.25, timer=5):
		super().__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Speeddope(Item):
	def __init__(self, name="Speed-Dope", idi=random.randint(301, 400), modifier=1.5, timer=5):
		super().__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Defdope(Item):
	# TODO Change get_damage function to implement defdope
	def __init__(self, name="Defence-Dope", idi=random.randint(401, 500), timer=5):
		super().__init__(name, idi)
		self.timer = timer


class Helm1(Item):
	def __init__(self, name="Lvl 1 Helm", idi=random.randint(501, 600)):
		super().__init__(name, idi)


class Helm2(Item):
	def __init__(self, name="Lvl 2 Helm", idi=random.randint(601, 700)):
		super().__init__(name, idi)


class Helm3(Item):
	def __init__(self, name="Lvl 3 Helm", idi=random.randint(701, 800)):
		super().__init__(name, idi)


class Armor1(Item):
	def __init__(self, name="Lvl 1 Rüstung", idi=random.randint(801, 900)):
		super().__init__(name, idi)


class Armor2(Item):
	def __init__(self, name="Lvl 2 Rüstung", idi=random.randint(901, 1000)):
		super().__init__(name, idi)


class Armor3(Item):
	def __init__(self, name="Lvl 3 Rüstung", idi=random.randint(1001, 1100)):
		super().__init__(name, idi)


boi = Bandage()
print(boi.idi)
print(boi.name)
boii = Healstation()
print(boii.idi)
print(boii.name)
