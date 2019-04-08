import random


class Weapon:
    name = "default"    #Name
    idi = 0             #ID
    weight = 0          #Gewicht
    damage = 0          #Schaden der Waffe
    mag = 0             #Magazin der Waffe
    spt = 0             #Schuss per Tick

    def __init__(self, name="default", idi=0, weight=0, dmg=0, mag=0, spt=0):
        self.name = name
        self.idi = idi
        self.weight = weight
        self.dmg = dmg
        self.mag = mag
        self.spt = spt


class Pistole(Weapon):
    def __init__(self, name="Pistole", idi=random.randint(10000, 11000), weight=42, dmg=18, mag=7, spt=2):
        super().__init__(name, idi, weight, dmg, mag, spt)





