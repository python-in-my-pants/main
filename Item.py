import random

'''
TODO Add weight to item classes
'''


class Item:
	def __init__(self, my_id=0, name="default", cost=1, weight=0):
		self.my_id = my_id
		self.name = name
		self.idi = "i" + str(id(self))
		self.cost = cost
		self.weight = weight


class Bandage(Item):
	def __init__(self, my_id=0, name="Bandage", cost=1, value=25, weight=0.5):
		super().__init__(my_id, name, cost, weight)
		self.value = value


class Medkit(Item):
	def __init__(self, my_id=1, name="Medkit", cost=2, value=75, weight=1):
		super().__init__(my_id, name, cost, weight)
		self.value = value


class Pillen(Item):
	# TODO Implement heal on more than one bodypart
	def __init__(self, my_id=2, name="Healstation", cost=2, value=50, weight=0.1):
		super().__init__(my_id, name, cost, weight)
		self.value = value


class Accudope(Item):
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
		self.timer = timer


def make_item_by_id(my_id):
	if my_id == 0: return Bandage()
	if my_id == 1: return Medkit()
	if my_id == 2: return Pillen()
	if my_id == 3: return Accudope()
	if my_id == 4: return Stredope()
	if my_id == 5: return Speeddope()
	if my_id == 6: return Defdope()


class Gear:
	def __init__(self, my_id=0, cost=1, weight=0):
		self.my_id = my_id
		self.idi = id(self)
		self.cost = cost
		self.weight = weight


class Helm(Gear):
	def __init__(self, my_id=0, cost=1, durability=0, reduction=0, weight=0):
		super().__init__(my_id, cost, weight)
		self.durability = durability
		self.reduction = reduction
		if self.my_id == 0:
			self.durability = 50
			self.reduction = 0.3
			self.cost = 1
			self.weight = 1
		if self.my_id == 1:
			self.durability = 75
			self.reduction = 0.4
			self.cost = 2
			self.weight = 1.5
		if self.my_id == 2:
			self.durability = 100
			self.reduction = 0.5
			self.cost = 3
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
			self.cost = 1
			self.weight = 5
		if self.my_id == 4:
			self.name = "Armor Lvl 2"
			self.durability = 125
			self.reduction = 0.75
			self.cost = 2
			self.weight = 10
		if self.my_id == 5:
			self.name = "Armor Lvl 3"
			self.durability = 150
			self.reduction = 0.7
			self.cost = 3
			self.weight = 15


def make_gear_by_id(my_id):
	if my_id == 0 or my_id == 1 or my_id == 2: return Helm(my_id)
	if my_id == 3 or my_id == 4 or my_id == 5: return Armor(my_id)

'''boi = Bandage()
print(boi.idi)
print(boi.name)
boii = Healstation()
print(boii.idi)
print(boii.name)'''
