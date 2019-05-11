import random

'''
TODO Add weight to item classes
'''


class Item:
	def __init__(self, name="default", idi=0):
		self.name = name
		self.idi = idi


class Bandage(Item):
	def __init__(self, name="Bandage", idi=random.randint(1, 1000), value=25):
		super(Item).__init__(name, idi)
		self.value = value


class Medkit(Item):
	def __init__(self, name="Medkit", idi=random.randint(1001, 2000), value=75):
		super(Item).__init__(name, idi)
		self.value = value


class Healstation(Item):
	# TODO Implement heal on more than one bodypart
	def __init__(self, name="Healstation", idi=random.randint(2001, 3000), value=50):
		super(Item).__init__(name, idi)
		self.value = value


class Accudope(Item):
	# TODO Add bool for the dopes if they are active
	def __init__(self, name="Accuracy-Dope", idi=random.randint(3001, 4000), modifier=1.25, timer=5):
		super(Item).__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Stredope(Item):
	def __init__(self, name="Strength-Dope", idi=random.randint(4001, 5000), modifier=1.25, timer=5):
		super(Item).__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Speeddope(Item):
	def __init__(self, name="Speed-Dope", idi=random.randint(6001, 7000), modifier=1.5, timer=5):
		super(Item).__init__(name, idi)
		self.modifier = modifier
		self.timer = timer


class Defdope(Item):
	# TODO Change get_damage function to implement defdope
	def __init__(self, name="Defence-Dope", idi=random.randint(8001, 9000), timer=5):
		super(Item).__init__(name, idi)
		self.timer = timer


class Helm(Item):
	def __init__(self, name="default_Helm", idi=random.randint(10001, 11000), typ=0, durability=0, reduction=0):
		super(Item).__init__(name, idi)
		self.typ = typ
		self.durability = durability
		self.reduction = reduction
		if self.typ == 1:
			self.name = "Helm Lvl 1"
			self.durability = 50
			self.reduction = 0.3
		if self.typ == 2:
			self.name = "Helm Lvl 2"
			self.durability = 75
			self.reduction = 0.4
		if self.typ == 3:
			self.name = "Helm Lvl 3"
			self.durability = 100
			self.reduction = 0.5


class Armor(Item):
	def __init__(self, name="default_Armor", idi=random.randint(11001, 12000), typ=0, durability=50, reduction=0.3):
		super(Item).__init__(name, idi)
		self.typ = typ
		self.durability = durability
		self.reduction = reduction
		if self.typ == 1:
			self.name = "Armor Lvl 1"
			self.durability = 100
			self.reduction = 0.8
		if self.typ == 2:
			self.name = "Armor Lvl 2"
			self.durability = 125
			self.reduction = 0.75
		if self.typ == 3:
			self.name = "Armor Lvl 3"
			self.durability = 150
			self.reduction = 0.7


'''boi = Bandage()
print(boi.idi)
print(boi.name)
boii = Healstation()
print(boii.idi)
print(boii.name)'''
