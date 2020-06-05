from Characters import *
from Item import *

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
    _, dmg_done = chara.shoot(charb, part)
    chance = chara.get_chance(charb, part)

    return chance, dmg_done


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

    chance, dmg = shooting_test(char1, char2, body_part)

    if p:
        print("\n{}"
              "\n\n --- attacked ---\n\n{}"
              "\n\n --- with a chance of ---\n\n[Chance:   {},\n    Dmg:   {}]"
              "\n\n --- at a distance of ---\n\n{}"
              "\n\n --- and did {} damage\n".format(char1, char2, chance[0], chance[1], d, dmg))

    return chance, dmg


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

test_case(class_id=sniper, weapon_id=snipe, d=50, p=True)
