import ctypes
import sys

if sys.platform == "win32":
    true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
else:
    true_res = [1920, 1080]  # just set the res manually for linux, maybe adjust later?

#serverIP = "88.150.32.237"


#serverIP = "78.47.178.105"


serverIP = "localhost"

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
    "sandstone": 1,
    "border": 2,
    "dirt": 3,
    "oak wood": 4,
    "bush": 5,
    "player": 6,
    "boulder": 7,
    "ruined_wood": 8,
    "default": -1
}

character_classes = {
    0: "Rook",           # basic stats
    1: "Light Troop",    # fast and nimble
    2: "Heavy Troop",    # slow and strong, heavily armed
    3: "Medic",          # fast and lightly armed
    4: "Sniper",         # high acc
    5: "Special Troop",  # idk
    6: "Commander"       # higher stats than normal but more expensive
}

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
                 scc["in game stat"]]


# this has to be here so that server AND client know what MatchData looks like
class MatchData:  # for hosting games

    def __init__(self, name, hosting_player, game_map, points):
        self.name = name
        self.hosting_player = hosting_player
        self.game_map = game_map
        self.points = points
