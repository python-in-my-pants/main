# encoding: UTF-8

import os
import GUI
from Render import *

debug = True
counter = 0  # TODO out

# stuff to beautify rendering

if sys.platform == "win32":
    ctypes.windll.user32.SetProcessDPIAware()
ctypes.windll.user32.SetProcessDPIAware()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # make so that popping windows are centered

# obligatory pygame init

pg.init()
pg.mixer.find_channel()

role = "default role"
teams = []
# TODO still up to date?
map_data = []  # holds data of map received from server PLUS the team number you have
clock = pg.time.Clock()

active_window = None
main_sound_chan = None

main_window = MainWindow
connection_setup = ConnectionSetup
character_selection = CharacterSelection
in_game = InGame

#  --------------------------------------------------------------------------------------------------
while True:

    if not active_window:

        active_window = main_window()
        main_sound_chan = GUI.play_sound(Data.menu_background_music)

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
                                                       #  cheapest char but full equipped for all team members

            elif active_window.role is "client":

                # I am client
                map_data = active_window.game_map_string  # ToDo Network
                game_map = Map.Map(x_size=map_data[3],
                                   y_size=map_data[4],
                                   objects=map_data[1],
                                   characters=map_data[2],
                                   unique_pixels=map_data[0])

                points_to_spend = Data.board_size(game_map.size_x, game_map.size_y)

                new_target = active_window.new_window_target
                active_window.harakiri()

                game_map.draw_map()  # ToDO Sollte der Guest das hier scho haben

                active_window = new_target(points_to_spend=points_to_spend,  # ToDo Gleiche wie Map hat der Guest das überhaupt scho?
                                           team_numberr=active_window.team_number,
                                           game_map=game_map,
                                           client=client_var,   # ToDo Network
                                           role=role)  # TODO add after balancing dependent on desired_map_size
                                                        #  cheapest char but full equipped for all team members

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
            active_window = new_target(own_team=team, game_map=_map, client=client_var, mode="TDM")
            GUI.stop_sound(main_sound_chan)
            GUI.play_sound(Data.ingame_background_music)

        else:

            active_window.event_handling()
            active_window.update()

    if isinstance(active_window, in_game):

        if active_window.new_window_target:

            new_target = active_window.new_window_target  # should be in_game
            active_window.harakiri()
            active_window = new_target()
            GUI.stop_sound(main_sound_chan)
            GUI.play_sound(Data.menu_background_music)

        else:

            active_window.event_handling()
            active_window.update()

    clock.tick(60)  # controls max fps
    # print("FPS: " + str(clock.get_fps()) + "\n\n") if counter % 180 == 0 else (lambda: None)
    counter += 1
    counter %= 180
    pg.display.flip()
