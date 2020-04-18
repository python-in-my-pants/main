import random


class Weapon:
    # name = "default"    #Name
    # class_idi = 0             #class_id
    # weight = 0          #Gewicht
    # damage = 0          #Schaden der Waffe
    # mag = 0             #Magazin der Waffe
    # spt = 0             #Schuss per Tick

    def __init__(self, class_id=0, name="default", cost=0, weight=0, acc=0, dmg=0, mag=0, spt=0):
        """

        :param class_id: holds kind of weapon e.g. pistol, sniper, etc.
        :param name:
        :param cost:
        :param weight:
        :param acc:
        :param dmg:
        :param mag:
        :param spt:
        """
        self.class_id = class_id  # class id
        self.name = name
        self.class_idi = "w" + str(id(self))  # unique id
        self.cost = cost
        self.weight = weight
        self.acc = acc
        self.dmg = dmg
        self.mag = mag
        self.spt = spt


# <editor-fold desc="weapon classes">
class Pistole(Weapon):
    def __init__(self, class_id=0, name="Pistole", cost=1, weight=0.7, acc=2.5, dmg=18, mag=10, spt=3):
        super().__init__(class_id, name, cost, weight, acc, dmg, mag, spt)


class Maschinenpistole(Weapon):
    def __init__(self, class_id=1, name="Maschinenpistole", cost=2, weight=1.9, acc=1.7, dmg=17, mag=20, spt=6):
        super().__init__(class_id, name,  cost, weight, acc, dmg, mag, spt)


class Sturmgewehr(Weapon):
    def __init__(self, class_id=2, name="Sturmgewehr", cost=3, weight=4, acc=2.7, dmg=22, mag=30, spt=5):
        super().__init__(class_id, name,  cost, weight, acc, dmg, mag, spt)


class Shotgun(Weapon):
    def __init__(self, class_id=3, name="Shotgun", cost=3, weight=3, acc=2, dmg=40, mag=2, spt=2):
        super().__init__(class_id, name, cost, weight, acc, dmg, mag, spt)


class Maschinengewehr(Weapon):
    def __init__(self, class_id=4, name="Maschinengewehr", cost=3, weight=10.5, acc=1.5, dmg=20, mag=100, spt=10):
        super().__init__(class_id, name, cost, weight, acc, dmg, mag, spt)


class Sniper(Weapon):
    def __init__(self, class_id=5, name="Sniper", cost=4, weight=6, acc=3.5, dmg=90, mag=7, spt=1):
        super().__init__(class_id, name, cost, weight, acc, dmg, mag, spt)


class Raketenwerfer(Weapon):
    def __init__(self, class_id=6, name="Raketenwerfer", cost=5, weight=8, acc=2, dmg=100, mag=1, spt=1):
        super().__init__(class_id, name, cost, weight, acc, dmg, mag, spt)
# </editor-fold>


def make_weapon_by_id(class_id):
    if class_id == 0: return Pistole()
    if class_id == 1: return Maschinenpistole()
    if class_id == 2: return Sturmgewehr()
    if class_id == 3: return Shotgun()
    if class_id == 4: return Maschinengewehr()
    if class_id == 5: return Sniper()
    if class_id == 6: return Raketenwerfer()


