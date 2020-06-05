from Data import *
import numpy as np


class Weapon:
    # name = "default"    #Name
    # class_idi = 0             #class_id
    # weight = 0          #Gewicht
    # damage = 0          #Schaden der Waffe
    # mag = 0             #Magazin der Waffe
    # spt = 0             #Schuss per Tick

    def __init__(self, class_id=0, name="default", cost=0, weight=0, mag=0, spt=0, bar_len=0, pv=0, pw=0):
        """

        :param class_id: holds kind of weapon e.g. pistol, sniper, etc.
        :param name: .
        :param cost: buying cost
        :param weight: .
        :param acc: projectile spread
        :param dmg: damage to body parts without armor
        :param mag: magazine size
        :param spt: shots per turn aka fire rate
        """
        self.class_id = class_id  # class id
        self.name = name
        self.class_idi = "w" + str(id(self))  # unique id

        self.cost = cost

        # base values
        self.weight = weight
        self.spt = spt
        self.barrel_len = 0         # in cm
        self.projectile_w = 0       #
        self.projectile_v = 0

        # calculated

        self.recoil = (self.spt * self.projectile_v * self.projectile_w) / (self.weight * k6)
        str_infl_on_recoil = (-np.tanh(self.recoil / k5) - k9 * 100)/2 + 0.5                     # 100 because max strength, but could be any constant I think
        inverse_recoil_influence = 1/((1-str_infl_on_recoil) * self.recoil + 1)

        self.acc = (self.barrel_len_conversion(self.barrel_len)/5.1) * inverse_recoil_influence
        self._dmg = self.projectile_w * self.projectile_v
        self.ran = self.projectile_v * (self.projectile_w/k6) * self.barrel_len_conversion(self.barrel_len)

        # unused
        self.mag = mag

    @classmethod
    def make_weapon_by_id(cls, class_id):
        return cls(class_id, *weapon_stats[class_id])

    @staticmethod
    def barrel_len_conversion(x):

        """
        :return: influence of barrel len, 0 to 1 where 1 equals 1m barrel len
        """

        return (k4 * np.log((k3 * x + k4)/k4))

    def get_dmg(self, dist):

        dmg_mult = (-np.tanh((dist / (self.ran * k1)) - 0.1 * self.ran * k1 - (1/k1)) / 2) + 0.5  # was - k1 at end of tanh

        return self._dmg * dmg_mult
