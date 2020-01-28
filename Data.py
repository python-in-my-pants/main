import ctypes

true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
serverIP = "127.0.0.1"

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

scc = {  # server control codes
    "Host":                 b'host ',
    "cancel hosting":       b'cHost',
    "Join":                 b'join ',
    "Turn":                 b'turn ',
    "get host list":        b'getHL',
    "control":              b'con  ',
    "char select ready":    b'csRdy',
    "hosting list":         b'hostl',
    "end game":             b'endg ',
    "game begins":          b'gbegi',
}

iscc = {v: k for k, v in scc.items()}  # inverted server control codes
