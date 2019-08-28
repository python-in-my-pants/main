import random


class Weapon:
    # name = "default"    #Name
    # class_idi = 0             #class_id
    # weight = 0          #Gewicht
    # damage = 0          #Schaden der Waffe
    # mag = 0             #Magazin der Waffe
    # spt = 0             #Schuss per Tick

    def __init__(self, class_id=0, name="default", cost=0, weight=0, acc=0, dmg=0, mag=0, spt=0):
        self.class_id = class_id
        self.name = name
        self.class_idi = id(self)
        self.cost = cost
        self.weight = weight
        self.acc = acc
        self.dmg = dmg
        self.mag = mag
        self.spt = spt


class Pistole(Weapon):
    def __init__(self, class_id=0, name="Pistole", class_idi=random.randint(101001, 102000), cost=1, weight=42, acc=2.7, dmg=18, mag=10, spt=3):
        super().__init__(class_id, name, class_idi, cost, weight, acc, dmg, mag, spt)


class Maschinenpistole(Weapon):
    def __init__(self, class_id=1, name="Maschinenpistole", class_idi=random.randint(101001, 102000), cost=2, weight=60, acc=1.8, dmg=19, mag=20, spt=6):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


class Sturmgewehr(Weapon):
    def __init__(self, class_id=2, name="Sturmgewehr", class_idi=random.randint(103001, 104000), cost=3, weight=80, acc=2.8, dmg=22, mag=30, spt=4):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


class Shotgun(Weapon):
    def __init__(self, class_id=3, name="Shotgun", class_idi=random.randint(102001, 103000), cost=3, weight=70, acc=2, dmg=40, mag=2, spt=2):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


class Maschinengewehr(Weapon):
    def __init__(self, class_id=4, name="Maschinengewehr", class_idi=random.randint(104001, 105000), cost=3, weight=120, acc=1.8, dmg=25, mag=100, spt=10):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


class Sniper(Weapon):
    def __init__(self, class_id=5, name="Sniper", class_idi=random.randint(105001, 106000), cost=4, weight=120, acc=3.5, dmg=90, mag=7, spt=1):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


class Raketenwerfer(Weapon):
    def __init__(self, class_id=6, name="Raketenwerfer", class_idi=random.randint(106001, 107000), cost=5, weight=150, acc=1.8, dmg=100, mag=1, spt=1):
        super().__init__(class_id, name,  class_idi, cost, weight, acc, dmg, mag, spt)


def make_weapon_by_id(class_id):
    if class_id == 0: return Pistole()
    if class_id == 1: return Maschinenpistole()
    if class_id == 2: return Sturmgewehr()
    if class_id == 3: return Shotgun()
    if class_id == 4: return Maschinengewehr()
    if class_id == 5: return Sniper()
    if class_id == 6: return Raketenwerfer()


