# encoding: UTF-8

import pygame as pg
from pygame.locals import *
from skimage.draw import line_aa
from threading import Timer
import numpy as np
import sys
import pickle
import time
import subprocess
import os
import ctypes

from _thread import *
from network import *
from Game_objects import *
from GUI import *
from Data import *
from GUI import *
from Map import *
from Render import *
from Characters import Character

debug = True
counter = 0
timee = True
# TODO throw out
c = CustomTimer()

# stuff to beautify rendering

if sys.platform == "win32":
    ctypes.windll.user32.SetProcessDPIAware()
ctypes.windll.user32.SetProcessDPIAware()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # make so that popping windows are centered

# obligatory pygame init

pg.init()

# client / server stuff
# os.startfile("server.py")
# net = Network(get('https://api.ipify.org').text)
# start_new_thread(net.routine_threaded_listener, ())
role = "nobody"
teams = []
# TODO still up to date?
map_data = []  # holds data of map received from server PLUS the team number you have

select = False
clock = pg.time.Clock()

#  --------------------------------------------------------------------------------------------

mon = pg.display.Info()
screen_h = int(mon.current_h)
screen_w = int(mon.current_w)
fields_x = 30  # width
fields_y = 30  # height
elem_size = int(screen_w/fields_x) if int(screen_w/fields_x) < int(screen_h/fields_y) else int(screen_h/fields_y)
x = elem_size * fields_x  # mult of 10
y = elem_size * fields_y  # mult of 10

active_window = None

main_window = MainWindow
connection_setup = ConnectionSetup
character_selection = CharacterSelection
in_game = InGame

#  --------------------------------------------------------------------------------------------------
while True:

    if not active_window:

        active_window = main_window()

    if isinstance(active_window, main_window):

        if active_window.new_window_target:  # should be connection setup

            new_target = active_window.new_window_target
            active_window.harakiri()
            active_window = new_target()

        else:  # if no new target is set, stay

            active_window.event_handling()
            active_window.update()

    if isinstance(active_window, connection_setup):

        if active_window.new_window_target:  # should be character selection

            client_var = active_window.client
            role = active_window.role

            if active_window.role is "host":

                # I am host
                # -> generate map
                new_target = active_window.new_window_target
                points_to_spend = active_window.map_points
                game_map = active_window.game_map_string
                # int(((game_map.size_x * game_map.size_y) / 500) * 16.6)  # TODO change maybe
                active_window.harakiri()

                active_window = new_target(points_to_spend=points_to_spend,
                                           team_numberr=active_window.team_number,
                                           game_map=game_map,
                                           client=client_var,  # ToDo Network
                                           role=role)  # TODO add after balancing dependent on desired_map_size
                                                       # cheapest char but full equipped for all team members

            elif active_window.role is "client":

                # I am client
                map_data = active_window.game_map_string  # ToDo Network
                game_map = Map.Map(x_size=map_data[3],
                                   y_size=map_data[4],
                                   elem_size=elem_size,
                                   objects=map_data[1],
                                   characters=map_data[2],
                                   unique_pixels=map_data[0])

                points_to_spend = int(((game_map.size_x * game_map.size_y) / 500) * 16.6)   # TODO change maybe

                new_target = active_window.new_window_target
                active_window.harakiri()

                game_map.draw_map()  # ToDO Sollte der Guest das hier scho haben

                active_window = new_target(points_to_spend=points_to_spend,  # ToDo Gleiche wie Map hat der Guest das überhaupt scho?
                                           team_numberr=active_window.team_number,
                                           game_map=game_map,
                                           client=client_var,   # ToDo Network
                                           role=role)  # TODO add after balancing dependent on desired_map_size
                                                        # cheapest char but full equipped for all team members

            elif active_window.role == "unknown":

                new_target = active_window.new_window_target
                active_window.harakiri()
                active_window = new_target()

            else:
                print("Something went wrong assigning the role!")

        else:

            active_window.event_handling()
            active_window.update()

    if isinstance(active_window, character_selection):

        if active_window.new_window_target:

            client_var = active_window.client

            new_target = active_window.new_window_target  # should be in_game
            team = active_window.ownTeam
            _map = active_window.game_map
            active_window.harakiri()
            active_window = new_target(own_team=team, game_map=_map, client=client_var)

        else:

            active_window.event_handling()
            active_window.update()

    if isinstance(active_window, in_game):

        if active_window.new_window_target:

            new_target = active_window.new_window_target  # should be in_game
            active_window.harakiri()
            active_window = new_target()

        else:

            active_window.event_handling()
            active_window.update()

    clock.tick(60)  # controls max fps
    # print("FPS: " + str(clock.get_fps()) + "\n\n") if counter % 180 == 0 else (lambda: None)
    counter += 1
    counter %= 180
    pg.display.flip()
