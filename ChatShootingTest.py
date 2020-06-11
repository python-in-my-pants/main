"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer                                                                                         #
#                                                                                                                      #
# Die durch die hier aufgeführten Autoren erstellten Inhalte und Werke unterliegen dem deutschen Urheberrecht.         #
# Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes  #
# bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.                                         #
#                                                                                                                      #
# Die Autoren räumen Dritten ausdrücklich kein Verwertungsrecht an der hier beschriebenen Software oder einer          #
# Kopie/Abwandlung dieser ein.                                                                                         #
#                                                                                                                      #
# Insbesondere untersagt ist das Entfernen und/oder Verändern dieses Hinweises.                                        #
#                                                                                                                      #
# Bei Zuwiderhandlung behalten die Autoren sich ausdrücklich die Einleitung rechtlicher Schritte vor.                  #
#                                                                                                                      #
########################################################################################################################
"""

from Characters import *
from Item import *
import numpy as np

head = 0
arm = 1
body = 3
leg = 5
body_parts = [head, arm, body, leg]

pawn = 0
light = 1
heavy = 2
medic = 3
sniper = 4
spezi = 5
commando = 6

pistol = 0
mp = 1
ar = 2
shotgun = 3
mg = 4
snipe = 5
rpg = 6


def build_char(team=0, helm_tier=3, weapon_id=0, leg_hp=200, arm_hp=200, class_id=0, v1=0, dist=10):
    char = Character(team=team,
                     class_id=class_id,
                     health=[default_hp[0],
                             arm_hp // 2,
                             arm_hp // 2,
                             default_hp[3],
                             leg_hp // 2,
                             leg_hp // 2],
                     dexterity=class_stats[class_id][2],
                     strength=class_stats[class_id][3],
                     weapons=[Weapon.make_weapon_by_id(weapon_id)],
                     gear=[make_gear_by_id(helm_tier-1), make_gear_by_id(3)])
    char.velocity = v1
    char.active_slot = char.weapons[0]
    char.pos = [0, 0 if team == 0 else dist]

    return char


def shooting_test(chara, charb, part):
    chance = chara.get_chance(charb, part)
    chara.shoot(charb, part)

    print("Chance:", chance)

    return chance


def test_case(body_part=body,
              d=10,

              helm_tier=3,
              west_tier=3,
              v2=0,
              weapon_id=0,

              leg_hp=200,
              arm_hp=200,
              class_id=0,
              v1=0,

              p=False):
    char1 = build_char(weapon_id=weapon_id, leg_hp=leg_hp, arm_hp=arm_hp, class_id=class_id, v1=v1)
    char2 = build_char(team=1, helm_tier=helm_tier, v1=v2, dist=d)

    if p:
        print("\n{}"
              "\n\n --- attacks ---\n\n{}"
              "\n\n --- with weapon ---\n\n{}"
              "\n --- at a distance of ---\n\n{}".format(char1, char2, char1.active_slot, d))

    chance = shooting_test(char1, char2, body_part)

    if p:
        print("\n --- with a chance of ---\n\n[Chance:   {},\n    Dmg:   {}]"
              "\n\n --- and did ---\n\n{}".format(chance[0], chance[1], char2))

    return chance


"""
    0: "Pawn",           # basic stats
    1: "Light",    # fast and nimble
    2: "Heavy",    # slow and strong, heavily armed
    3: "Medic",          # fast and lightly armed
    4: "Sniper",         # high acc
    5: "Spezi",  # idk
    6: "Commander"       # higher stats than normal but more expensive
    
    #   name         cost   weight    mag    spt  bar_len      pv     pw
    0: ["Pistol",      1,       1,    10,     3,      11,     300,    21],
    1: ["MP",          2,     2.6,    30,    23,      20,     500,    22],
    2: ["Sturmgewehr", 3,     3.5,    30,    21,      45,    1200,    11],
    3: ["Shotgun",     3,     2.8,     2,     2,      71,     415,    24],
    4: ["MG",          3,     6.4,   100,    25,      55,    1200,    11],
    5: ["Sniper",      4,     8.2,     1,     1,      69,     915,    50],
    6: ["RL",          5,     6.7,     1,     1,     100,     285,  1800]
"""


def print_weapon_recoil_stats():

    for w in range(7):
        pw = weapon_stats[w][-1]
        pv = weapon_stats[w][-2]
        m = weapon_stats[w][2]
        spt = weapon_stats[w][4]

        recoil_energy_per_shot = ((pw/1000)**2 * pv**2)/(2*m)
        recoil_energy_per_turn = recoil_energy_per_shot * spt
        weapon = Weapon.make_weapon_by_id(class_id=w)
        dmg_per_turn = weapon.dmg * weapon.spt * weapon.acc

        strength = 100

        def sign(x):

            if x < 0:
                return -1
            if x == 0:
                return 0
            if x > 0:
                return 1

        f_recoil = (2 * max(sign(spt-1)/2, 0)) * (6.9/((-0.008 * strength + 1) * recoil_energy_per_turn)) + 1 - (2 * max(sign(spt-1)/2, 0))

        print(weapon)
        print("in Pixel: "+str(weapon.dmg/400))
        print("---dmg per turn------------->  ", dmg_per_turn)
        print("---resulting cost----------->  ", dmg_per_turn//40)
        print("Recoil of {:12}: \t{:>}\t\t\t\t{:>}".format(weapon_stats[w][0], recoil_energy_per_turn, f_recoil))
        print("-----------------------------------------------------------------------------------------")


#test_case(class_id=sniper, weapon_id=rpg, d=44, p=True, body_part=body)
print_weapon_recoil_stats()
