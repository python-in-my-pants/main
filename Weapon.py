from Data import *


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

    @classmethod
    def make_weapon_by_id(cls, class_id):
        return cls(class_id, *weapon_stats[class_id])
