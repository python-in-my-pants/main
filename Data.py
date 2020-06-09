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

import ctypes
import sys
import time

if sys.platform == "win32":
    true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    # TODO put out, just for debugging
    true_res = [1280, 720]
else:
    true_res = [1920, 1080]  # just set the res manually for linux, maybe adjust later?


font = "bahnschrift"
master_volume = 0.0
char_cap_divisor = 500
points_per_field = 0.245
speed_multiplier = 0.1
velocity_decay_factor = 0.2
def_elem_size = 50


def get_max_chars_per_team(x, y):
    return int(points_to_spend_per_team(x, y) / (class_stats[0][-1]) + 1)  # plus pistol cost of 1


def points_to_spend_per_team(x, y):
    return int(x * y * points_per_field * 0.5)


#serverIP = "78.47.178.105"


serverIP = "localhost"


# <editor-fold desc="material">
mat_colour = {
    "sandstone": (255, 140, 0),
    "border": (199, 80, 80),
    "dirt": (66, 33, 33),
    "oak wood": (99, 33, 33),
    0: (0, 255, 0),  # team 0
    "team_0": (0, 255, 0),  # team 0
    1: (0, 0, 255),
    "team_1": (0, 0, 255),
    "team_2": (255, 0, 0),
    "team_3": (0, 7, 0),
    "team_4": (255, 255, 255),
    "bush": (0, 87, 0),
    "boulder": (149, 148, 139),
    "ruined_wood": (92, 64, 51),
    "default": (255, 20, 147)
}

material_codes = {
    "grass": 0,
    "sandstone": 1,
    "border": 2,
    "dirt": 3,
    "oak wood": 4,
    "bush": 5,
    "player": 6,
    "boulder": 7,
    "ruined_wood": 8,
    "puddel": 9,
    "area1": 10,
    "area2": 11,
    "default": -1
}
# </editor-fold>

# <editor-fold desc="characters">

default_hp = [35, 100, 100, 100, 100, 100]
base_chances = [.25, .40, .40, 1, .50, .50]

# shooting constants
k1 = 0.42           # controls dmg falloff behind effective range, lower = steeper falloff
k2 = 5.58           # controls influence of speed; the higher the value, the lower the influence
k3 = 200            # influences barrel len effect
k4 = 3.4            # a
k5 = 17.9           # impact of recoil
k6 = 1200           # max muzzle velocity
k9 = 0.189          # strength influence
k10 = 0.95          # body part influence (target)
k11 = 2.1           # dmg multiplier for base dmg

character_classes = {
    0: "Pawn",           # basic stats
    1: "Light",          # fast and nimble
    2: "Heavy",          # slow and strong, heavily armed
    3: "Medic",          # fast and lightly armed
    4: "Sniper",         # high acc
    5: "Spezi",          # idk
    6: "Commander"       # higher stats than normal but more expensive
}

class_stats = {
    #  [stamina, speed, dexterity, strength, weight, cost]
    0: [50,         40,        35,       35,     70,   14],
    1: [55,         70,        45,       35,     80,   21],
    2: [40,         30,        50,       80,    100,   33],
    3: [70,         50,        35,       50,     60,   28],
    4: [70,         40,        70,       35,     75,   39],
    5: [70,         50,        35,       50,     75,   25]
}

weapon_stats = {
    #   name         cost   weight    mag    spt   bar_len      pv     pw
    0: ["Pistol",      1,       1,    10,     3,      0.11,     300,    16],  # war 20
    1: ["MP",          2,     2.6,    30,    23,      0.20,     500,     7],  # war
    2: ["Sturmgewehr", 3,     3.5,    30,    21,      0.45,    1200,     4],
    3: ["Shotgun",     3,     2.8,     2,     2,      0.71,     415,    24],
    4: ["MG",          3,     6.4,   100,    25,      0.55,    1200,     4],
    5: ["Sniper",      4,     8.2,     1,     1,      0.69,     915,    50],
    6: ["RL",          5,     6.7,     1,     1,         1,     285,  1800]
}

gear_durability = {
    0: 50,
    1: 75,
    2: 100,
    3: 100
}


# </editor-fold>

# <editor-fold desc="network">
scc = {  # server control codes             message holds the following:
    "Host":                 b'host ',       # (name, game_map, points)
    "cancel hosting":       b'cHost',       # ""
    "Join":                 b'join ',       # name of the game to join
    "Turn":                 b'turn ',       # turn data object
    "get host list":        b'getHL',       # ""
    "control":              b'con  ',       # control message
    "char select ready":    b'csRdy',       # (ready, team)
    "hosting list":         b'hostl',       # hosting list object
    "end game":             b'endg ',       # TODO surely sth
    "game begins":          b'gbegi',       # final map, team 1, team 2
    "get turn":             b'gturn',       # ""
    "undefined":            b'undef',       # N/A
    "close connection":     b'close',       # ""
    "confirm":              b'confi',       # confirm msg with hash
    "get in game stat":     b'ginst',       # True or False
    "in game stat":         b'ingst',       # yes or no
    "message end":          b'XXXXX'        # not a control type but here anyway
}

arg_len = {
    b'host ': 3,  # (name, game_map, points)
    b'turn ': 2,  # turn data object and time
    b'csRdy': 2,  # (ready, team)
    b'hostl': 1,  # hosting list object
    b'gbegi': 2,  # final map, team 1, team 2
}

needs_confirm = {
    "Host":             True,
    "cancel hosting":   True,
    "Join":             True,
    "Turn":             True,
    "get host list":    True,
    "control":          True,
    "char select ready":False,
    "hosting list":     False,
    "end game":         True,
    "game begins":      True,
    "get turn":         True,
    "undefined":        False,
    "close connection": False,
    "get in game stat": True,
    "in game stat":     False,
    "confirm":          False
}

iscc = {v: k for k, v in scc.items()}  # inverted server control codes

unwrap_as_obj = [scc["Turn"],
                 scc["hosting list"],
                 scc["char select ready"],
                 scc["Host"],
                 scc["game begins"]]
unwrap_as_str = [scc["control"],
                 scc["close connection"],
                 scc["get host list"],
                 scc["undefined"],
                 scc["confirm"],
                 scc["get in game stat"],
                 scc["in game stat"],
                 scc["cancel hosting"],
                 scc["Join"],
                 scc["get turn"],
                 scc["end game"]]
# </editor-fold>

##############
# paths ######
##############

# <editor-fold desc="paths">

# visuals #

#   images
main_background = "assets/textures/background_art/main_background_02.png"
connection_setup_background = "assets/textures/background_art/notmikan02.jpg"
empty_af = "assets/empty_af.png"
bleed_drop = "assets/bleed_art.png"
host_banner = "assets/textures/background_images/host_banner.png"
client_banner = "assets/textures/background_images/client_banner.png"

#   buttons
blue_btn_menu = "assets/textures/buttons/blue_button_menu.jpg"
back_btn = "assets/textures/buttons/back_btn.png"

metal_btn = "assets/textures/background_images/metall.png"
rem_points = "assets/textures/background_images/remaining_points.png"
team_char_backgr = "assets/textures/background_images/team_char_back.png"
deco_banner = "assets/textures/background_images/deco_banner.png"
rusty_metal = "assets/textures/background_images/rusty_metal.jpg"

lose_banner_text = "assets/textures/buttons/lose_banner_text.png"
win_banner_text = "assets/textures/buttons/win_banner_text.png"

#   cards
# <editor-fold desc="cards">
cc_smol_prefix = "assets/textures/cards/cc/small/cc_"
wc_smol_prefix = "assets/textures/cards/wc/small/wc_"
gc_smol_prefix = "assets/textures/cards/gc/small/gc_"
ic_smol_prefix = "assets/textures/cards/ic/small/ic_"

cc_big_prefix = "assets/textures/cards/cc/cc_"
gc_big_prefix = "assets/textures/cards/gc/gc_"
wc_big_prefix = "assets/textures/cards/wc/wc_"
ic_big_prefix = "assets/textures/cards/ic/ic_"

cc_detail_prefix = "assets/textures/cards/cc/detail/cc_"
gc_detail_prefix = "assets/textures/cards/gc/detail/gc_"
wc_detail_prefix = "assets/textures/cards/wc/detail/wc_"
ic_detail_prefix = "assets/textures/cards/ic/detail/ic_"
# </editor-fold>

#   textures

grass_texture = "assets/textures/mats/Grass.png"
sandstone_texture = "assets/textures/mats/sandstone.png"
border_texture = "assets/textures/mats/border.png"
house_floor_texture = "assets/textures/mats/House_floor.png"
flooring_texture = "assets/textures/mats/Flooring.png"
bush_texture = "assets/textures/mats/bush.png"
boulder_texture = "assets/textures/mats/boulder.png"
ruin_floor_texture = "assets/textures/mats/Ruin_floor.png"
area_1 = "assets/textures/mats/area1.png"
area_2 = "assets/textures/mats/area2.png"

overlay_base = "assets/textures/overlay/dude.png"
head = "assets/textures/overlay/dude_kopf.png"
r_arm = "assets/textures/overlay/dude_rarm.png"
l_arm = "assets/textures/overlay/dude_larm.png"
torso = "assets/textures/overlay/dude_torso.png"
r_leg = "assets/textures/overlay/dude_rbein.png"
l_leg = "assets/textures/overlay/dude_lbein.png"

# <editor-fold desc="types">
bush_types = {
    0: "assets/textures/mats/Bush/Bush_1x1.png",
    1: "assets/textures/mats/Bush/Bush_1x2.png",
    2: "assets/textures/mats/Bush/Bush_2x1.png",
    3: "assets/textures/mats/Bush/Bush_2x2.png",
    4: "assets/textures/mats/Bush/Bush_2x3.png",
    5: "assets/textures/mats/Bush/Bush_3x2.png"
}

puddel_types = {
    0: "assets/textures/mats/Puddel/Puddel_1x1.png",
    1: "assets/textures/mats/Puddel/Puddel_1x2.png",
    2: "assets/textures/mats/Puddel/Puddel_2x1.png",
    3: "assets/textures/mats/Puddel/Puddel_2x2.png",
    4: "assets/textures/mats/Puddel/Puddel_2x3.png",
    5: "assets/textures/mats/Puddel/Puddel_3x2.png"
}

boulder_types = {
    0: "assets/textures/mats/Boulder/Boulder_1x1.png",
    1: "assets/textures/mats/Boulder/Boulder_1x2.png",
    2: "assets/textures/mats/Boulder/Boulder_2x1.png",
    3: "assets/textures/mats/Boulder/Boulder_2x2.png",
    4: "assets/textures/mats/Boulder/Boulder_2x3.png",
    5: "assets/textures/mats/Boulder/Boulder_3x2.png"
}

tree_types = {
    0: "assets/textures/mats/Tree/Tree_1x1.png",
    1: "assets/textures/mats/Tree/Tree_2x2.png"
}

# </editor-fold>

# audio #

#   sounds
button_click = "assets/sound/button_lick_02.wav"

#   music
menu_background_music = "assets/sound/ophelia.wav"  # Music: www.bensound.com
ingame_background_music = "assets/sound/epic.wav"   # Music: www.bensound.com

# </editor-fold>


def hostin_list_eq(dict1, dict2):
    try:
        if len(dict1) != len(dict2):
            return False
        for key, val in dict1.items():
            if not dict1[key] == dict2[key]:
                return False
        return True
    except KeyError as e:
        print("Key error: {}".format(e))
        return False
    except TypeError as e:
        print("Type error: {}".format(e))
        return False
    except Exception as e:
        print(e)
        return False


# this has to be here so that server AND client know what MatchData looks like
class MatchData:  # for hosting games

    def __init__(self, name, hosting_player, game_map, points):
        self.name = name
        self.hosting_player = hosting_player
        self.game_map = game_map
        self.points = points

    def __eq__(self, other):
        if self.name == other.name and self.hosting_player == other.hosting_player and \
           self.game_map == other.game_map and self.points == other.points:
            return True
        else:
            return False

    def to_string(self):
        return "{}, {}, {}".format(self.name, self.hosting_player, self.points)


class CustomTimer:

    def __init__(self, start=False):
        self.start_time = None
        self.last_time = None

    def t(self, name="This"):

        print("{:<20} takes:\t\t\t {:<25} s".format(name,
                                                    time.time() - self.last_time) if self.last_time else -1)
        self.last_time = time.time()

    def start(self):
        self.start_time = time.time()
        self.last_time = self.start_time

    def end(self):
        print(("\tTimer took:" + " "*21 + " {:<25} s").format(time.time() - self.start_time) if self.last_time else -1)
        self.last_time = time.time()
