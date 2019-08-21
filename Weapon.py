import random


class Weapon:
    # name = "default"    #Name
    # idi = 0             #ID
    # weight = 0          #Gewicht
    # damage = 0          #Schaden der Waffe
    # mag = 0             #Magazin der Waffe
    # spt = 0             #Schuss per Tick

    def __init__(self, name="default", idi=0, cost=0, weight=0, dmg=0, mag=0, spt=0):
        self.name = name
        self.idi = idi
        self.cost = cost
        self.weight = weight
        self.dmg = dmg
        self.mag = mag
        self.spt = spt


class Pistole:
    def __init__(self, name="Pistole", idi=random.randint(100000, 101000), cost=5, weight=42, dmg=18, mag=10, spt=2):
        super().__init__(name, idi, cost, weight, dmg, mag, spt)


class Maschinenpistole:
    def __init__(self, name="Maschinenpistole", idi=random.randint(101001, 102000), cost=5, weight=60, dmg=19, mag=20, spt=6):
        super().__init__(name, idi, cost, weight, dmg, mag, spt)


class Sturmgewehr:
    def __init__(self, name="Sturmgewehr", idi=random.randint(102001, 103000), cost=5, weight=80, dmg=22, mag=30, spt=4):
        super().__init__(name, idi, cost, weight, dmg, mag, spt)


class Maschinengewehr:
    def __init__(self, name="Maschinengewehr", idi=random.randint(103001, 104000), cost=5, weight=120, dmg=25, mag=100, spt=10):
        super().__init__(name, idi, cost, weight, dmg, mag, spt)


class Sniper:
    def __init__(self, name="Sniper", idi=random.randint(104001, 105000), cost=5, weight=120, dmg=90, mag=7, spt=1):
        super().__init__(name, idi, cost, weight, dmg, mag, spt)

class Raketenwerfer:
    def __init__(self, name="Raketenwerfer", idi=random.randint(105001, 106000), weight=150, dmg=100, mag=1, spt=1):
        super().__init__(name, idi, weight, dmg, mag, spt)




