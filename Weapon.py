"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
# Stand: 07.06.2020                                                                                                    #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer, Christian Loose                                                                        #
#                                                                                                                      #
# Die durch die hier aufgeführten Autoren erstellten Inhalte und Werke unterliegen dem deutschen Urheberrecht.         #
# Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes  #
# bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers und des Projektleiters,                  #
# Daniel Kretschmer.                                                                                                   #
#                                                                                                                      #
# Die Autoren räumen Dritten ausdrücklich kein Verwertungsrecht an der hier beschriebenen Software oder einer          #
# Kopie/Abwandlung dieser ein.                                                                                         #
#                                                                                                                      #
# Jegliche kommerzielle Nutzung des Programmcodes oder des zugrunde liegenden geistigen Eigentums oder von Teilen      #
# oder veränderten Verionen dessen ist strengstens untersagt.                                                          #
#                                                                                                                      #
# Insbesondere untersagt ist das Entfernen und/oder Verändern dieses Hinweises.                                        #
#                                                                                                                      #
# Bei Zuwiderhandlung behalten die Autoren sich ausdrücklich die Einleitung rechtlicher Schritte vor.                  #
#                                                                                                                      #
########################################################################################################################
"""

from Data import *
import numpy as np


class Weapon:

    def __init__(self, class_id=0, name="Weapon", cost=0, weight=0, mag=0, spt=0, bar_len=0, pv=0, pw=0):
        """

        :param class_id: holds kind of weapon e.g. pistol, sniper, etc.
        :param cost: buying cost
        :param weight: .
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
        self.barrel_len = bar_len         # in cm
        self.projectile_w = pw       #
        self.projectile_v = pv

        # calculated

        muzzle_energy = ((self.projectile_w/1000)**2 * self.projectile_v**2) / (2*self.weight)
        self.dmg = ((((self.projectile_w/1000)/2)*(self.projectile_v**2)/40) + 0.5)
        self.recoil = muzzle_energy * self.spt
        recoil_f = (2 * max(np.sign(spt-1)/2, 0)) * (6.9/((-0.008 * 100 + 1) * self.recoil)) + 1 - \
                   (2 * max(np.sign(spt-1)/2, 0))
        bar_len_factor = -(np.tanh(4 * (1 - (3.4 * np.log10( (200 * self.barrel_len + 3.4)/3.4))/5.55) - 2.4)/2)+0.5
        self.acc = recoil_f * bar_len_factor

        #self.ran = self.projectile_w * (self.projectile_v/k6) * self.barrel_len_conversion(self.barrel_len)

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

        return k4 * np.log10(((k3 * x) + k4)/k4)

    def get_dmg_old(self, dist):

        dmg_mult = (-np.tanh((dist / (self.ran * k1)) - 0.1 * self.ran * k1 - (1/k1)) / 2) + 0.5  # was - k1 at end of tanh

        return self._dmg * dmg_mult

    def __str__(self):

        return "{}:\n" \
               "\t  Weight:\t{}\n" \
               "\t     Spt:\t{}\n" \
               "\t Bar len:\t{}\n" \
               "\t      pv:\t{}\n" \
               "\t      pw:\t{}\n\n" \
               "\t     acc:\t{}\n" \
               "\t     dmg:\t{}\n" \
               "\t  recoil:\t{}\n".format(self.name,
                                          self.weight, self.spt, self.barrel_len, self.projectile_v, self.projectile_w,
                                          self.acc, self.dmg, self.recoil)
