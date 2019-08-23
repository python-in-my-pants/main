import random


class Weapon:
    # name = "default"    #Name
    # idi = 0             #ID
    # weight = 0          #Gewicht
    # damage = 0          #Schaden der Waffe
    # mag = 0             #Magazin der Waffe
    # spt = 0             #Schuss per Tick

    def __init__(self, id=0, name="default", idi=0, cost=0, weight=0, acc=0, dmg=0, mag=0, spt=0):
        self.id = id
        self.name = name
        self.idi = idi
        self.cost = cost
        self.weight = weight
        self.acc = acc
        self.dmg = dmg
        self.mag = mag
        self.spt = spt


class Pistole(Weapon):
    def __init__(self, id=0, name="Pistole", idi=random.randint(100000, 101000), cost=5, weight=42, acc=0, dmg=18, mag=10, spt=2):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Maschinenpistole(Weapon):
    def __init__(self, id=1, name="Maschinenpistole", idi=random.randint(101001, 102000), cost=5, weight=60, acc=0, dmg=19, mag=20, spt=6):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Shotgun(Weapon):
    def __init__(self, id=3, name="Shotgun", idi=random.randint(102001, 103000), cost=3, weight=70, acc=0, dmg=40, mag=2, spt=2):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Sturmgewehr(Weapon):
    def __init__(self, id=2, name="Sturmgewehr", idi=random.randint(103001, 104000), cost=5, weight=80, acc=0, dmg=22, mag=30, spt=4):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Maschinengewehr(Weapon):
    def __init__(self, id=4, name="Maschinengewehr", idi=random.randint(104001, 105000), cost=5, weight=120, acc=0, dmg=25, mag=100, spt=10):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Sniper(Weapon):
    def __init__(self, id=5, name="Sniper", idi=random.randint(105001, 106000), cost=5, weight=120, acc=0, dmg=90, mag=7, spt=1):
        super().__init__(id, name, idi, cost, weight, acc, dmg, mag, spt)


class Raketenwerfer(Weapon):
    def __init__(self, id=6, name="Raketenwerfer", idi=random.randint(106001, 107000), weight=150, acc=0, dmg=100, mag=1, spt=1):
        super().__init__(id, name, idi, weight, acc, dmg, mag, spt)


def make_weapon_by_id(id):
    if id == 0: return Pistole()
    if id == 1: return Maschinenpistole()
    if id == 2: return Sturmgewehr()
    if id == 3: return Shotgun()
    if id == 4: return Maschinengewehr()
    if id == 5: return Sniper()
    if id == 6: return Raketenwerfer()


