import random

'''
TODO Add weight to item classes
'''


class Item:
	def __init__(self, id=0, name="default", idi=0, cost=1):
		self.id = id
		self.name = name
		self.idi = idi
		self.cost = cost


class Bandage(Item):
	def __init__(self, id=0, name="Bandage", idi=random.randint(1, 1000), cost=1, value=25):
		super(Item).__init__(id, name, idi, cost)
		self.value = value


class Medkit(Item):
	def __init__(self, id=1, name="Medkit", idi=random.randint(1001, 2000), cost=1, value=75):
		super().__init__(id, name, idi, cost)
		self.value = value


class Pillen(Item):
	# TODO Implement heal on more than one bodypart
	def __init__(self, id=2, name="Healstation", idi=random.randint(2001, 3000), cost=1, value=50):
		super(Item).__init__(id, name, idi, cost)
		self.value = value


class Accudope(Item):
	# TODO Add bool for the dopes if they are active
	def __init__(self, id=3, name="Accuracy-Dope", idi=random.randint(3001, 4000), cost=1, modifier=1.25, timer=5):
		super(Item).__init__(id, name, idi, cost)
		self.modifier = modifier
		self.timer = timer


class Stredope(Item):
	def __init__(self, id=4, name="Strength-Dope", idi=random.randint(4001, 5000), cost=1, modifier=1.25, timer=5):
		super(Item).__init__(id, name, idi, cost)
		self.modifier = modifier
		self.timer = timer


class Speeddope(Item):
	def __init__(self, id=5, name="Speed-Dope", idi=random.randint(6001, 7000), cost=1, modifier=1.5, timer=5):
		super(Item).__init__(id, name, idi, cost)
		self.modifier = modifier
		self.timer = timer


class Defdope(Item):
	# TODO Change get_damage function to implement defdope
	def __init__(self, id=6, name="Defence-Dope", idi=random.randint(8001, 9000), cost=1, timer=5):
		super(Item).__init__(id, name, idi, cost)
		self.timer = timer


def make_item_by_id(id):
	if id == 0: return Bandage()
	if id == 1: return Medkit()
	if id == 2: return Pillen()
	if id == 3: return Accudope()
	if id == 4: return Stredope()
	if id == 5: return Speeddope()
	if id == 6: return Defdope()


class Gear:
	def __init__(self, id=0, name="default", idi=0, cost=1):
		self.id = id
		self.name = name
		self.idi = idi
		self.cost = cost


class Helm(Gear):
	def __init__(self, id=0, name="default_Helm", idi=random.randint(10001, 11000), cost=1, durability=0, reduction=0):
		super(Gear).__init__(id, name, idi, cost)
		self.durability = durability
		self.reduction = reduction
		if self.id == 0:
			self.name = "Helm Lvl 1"
			self.durability = 50
			self.reduction = 0.3
			self.cost = 1
		if self.id == 1:
			self.name = "Helm Lvl 2"
			self.durability = 75
			self.reduction = 0.4
			self.cost = 2
		if self.id == 2:
			self.name = "Helm Lvl 3"
			self.durability = 100
			self.reduction = 0.5
			self.cost = 3


class Armor(Gear):
	def __init__(self, id=0, name="default_Armor", idi=random.randint(11001, 12000), cost=1, durability=50, reduction=0.3):
		super(Gear).__init__(id, name, idi, cost)
		self.durability = durability
		self.reduction = reduction
		if self.id == 3:
			self.name = "Armor Lvl 1"
			self.durability = 100
			self.reduction = 0.8
			self.cost = 1
		if self.id == 4:
			self.name = "Armor Lvl 2"
			self.durability = 125
			self.reduction = 0.75
			self.cost = 2
		if self.id == 5:
			self.name = "Armor Lvl 3"
			self.durability = 150
			self.reduction = 0.7
			self.cost = 3


def make_gear_by_id(id):
	if id == 0 or id == 1 or id == 2: return Helm(id)
	if id == 3 or id == 4 or id == 5: return Armor(id)

'''boi = Bandage()
print(boi.idi)
print(boi.name)
boii = Healstation()
print(boii.idi)
print(boii.name)'''
