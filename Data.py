import ctypes

true_res = (1600,900)#(ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))

mat_colour = {
    "sandstone": (255, 140, 0),
    "border": (199, 80, 80),
    "dirt": (66, 33, 33),
    "oak wood": (99, 33, 33),
    "team_0": (0, 255, 0),
    "team_1": (0, 0, 255),
    "team_2": (255, 0, 0),
    "team_3": (0, 7, 0),
    "team_4": (255, 255, 255),
    "bush": (0, 87, 0),
    "default": (255, 20, 147)
}

material_codes = {
    "sandstone": 1,
    "border": 2,
    "dirt": 3,
    "oak wood": 4,
    "bush": 5,
    "player": 6,
    "default": -1
}

character_classes = {
    0: "Rook",       # basic stats
    1: "Light Troop",          # lower than basic stats but with less cost to buy
    2: "Heavy Troop",        # high acc
    3: "Medic",         # fast and lightly armed
    4: "Sniper",         # slow and strong, heavily armed
    5: "Special Troop",     # idk
    6: "Commander"      # higher stats than normal but more expensive
}
