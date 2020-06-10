"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer, Christian Loose                                                                        #
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

import Map
from NewClient import *
from GUI import *
from Team import *
from Characters import *
from TTimer import *
from Turn import *
import time
import ctypes
import traceback

if sys.platform == "win32":
    ctypes.windll.user32.SetProcessDPIAware()

debug = False


class MainWindow:

    def __init__(self):  # creates main window with contents -> "mainscreen"
        size = Data.true_res
        # print("MainWindow thinks the size is: " + str(size))

        self.new_window_target = None
        self.screen = pg.display.set_mode(true_res)  # , pg.RESIZABLE | pg.FULLSCREEN)  # TODO put back in

        main_background_img = pg.image.load(Data.main_background)

        # set window name
        pg.display.set_caption("nAme;Rain - Mainscreen")

        # scale image to desired size
        main_background_img = fit_surf(self.screen, main_background_img)

        # draw background image on screen
        self.screen.blit(main_background_img, blit_centered_pos(self.screen, main_background_img))

        self.buttons = None
        # ------------------------------------------------------
        # set up GUI

        self.buttons = []

        def button_fkt():
            # pg.mixer.music.load("assets/ass.mp3")  # TODO replace with omae wa mou and play on window open in loop
            # pg.mixer.music.play(0)
            # time.sleep(2.5)

            # go to different window and kill this one
            self.new_window_target = ConnectionSetup

        btn = Button([int(0.2 * size[0]), int(0.069 * size[1])], pos=[size[0] / 2 - int(0.2 * size[0]) / 2,
                                                                      size[1] / 2 - int(0.069 * size[1]) / 2 + 200],
                     img_uri=rusty_metal, text="Play", name="Button 1", action=button_fkt)

        # render Button to screen
        self.screen.blit(btn.surf, btn.pos)
        # add button to button list
        self.buttons.append(btn)

    def update(self):

        pass

    def event_handling(self):

        # event handling
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()
                for button in self.buttons:
                    if button.is_focused(p):
                        button.action()

    def harakiri(self):
        del self


class ConnectionSetup:

    def __init__(self):

        self.new_window_target = None
        self.role = "unknown"
        self.field_size = 0
        self.client = NetworkClient()
        self.client.get_hosting_list_from_server()

        self.host_thread = 0
        self.join_thread = 0
        self.map_points = None
        self.team_number = 0

        # TODO maybe make a focus list if buttons become more?
        self.ip_focus = False
        self.size_focus = False
        self.first_click = True
        self.board_first_click = True

        self.hosting_list = {}
        self.get_hosting_list_counter = 0
        self.game_to_join = None

        # self.ip_field_text = ...  # TODO change; this will be a button in a list of games to join marking the game as the game to join
        self.desi_board_text = "35"  # TODO change; here you should also enter the game name -> GameName, size, e.g. Dungeon, 50

        self.game_map_string = None

        self.main_background_img = pg.transform.scale(pg.image.load(Data.connection_setup_background).convert_alpha(),
                                                      true_res)

        # self.main_background_img = fit_surf(pg.Surface(true_res), self.main_background_img)

        # create window
        self.screen = pg.display.set_mode(true_res)  # , pg.RESIZABLE | pg.FULLSCREEN)  # TODO put back in
        self.screen.blit(self.main_background_img, blit_centered_pos(self.screen, self.main_background_img))
        # TODO remove
        self.c = CustomTimer()

        # set up GUI ---------------------------------------------------------------------------------------------------

        # <editor-fold desc="Setting up surfaces">
        # set up surfaces
        # we need 2 surfaces that are transparent
        self.left_surf = pg.Surface([int(true_res[0] / 2), true_res[1]])
        self.left_surf.fill((255, 12, 255))
        self.left_surf.set_colorkey((255, 12, 255))

        self.right_surf = pg.Surface([int(true_res[0] / 2), true_res[1]])
        self.right_surf.fill((255, 12, 255))
        self.right_surf.set_colorkey((255, 12, 255))

        surfs_size = [self.left_surf.get_width(), self.left_surf.get_height()]  # only 1 because they are equally big
        self.surfs_size = surfs_size
        # </editor-fold>

        # Buttons
        # <editor-fold desc="Host buttons">
        # define buttons and put them on their surface

        # define list of buttons
        self.buttons = []

        self.desired_board_size_button = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                                pos=[int(surfs_size[0] / 4),
                                                     int(surfs_size[1] * 0.7)],
                                                color=(255, 255, 255), text="35", name="board_size_button",
                                                action=self.desired_board_size_button_fkt)

        # append later to not mess up indices

        self.host_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                               pos=[int(surfs_size[0] / 4),
                                    int(surfs_size[1] / 6)],
                               color=(135, 206, 235), text="Host", name="host_btn",
                               action=self.host_btn_fkt)

        self.buttons.append(self.host_btn)

        self.host_stat_btn = Button([int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                    pos=[int(surfs_size[0] / 4),
                                         int(surfs_size[1] * 0.43)],
                                    color=(135, 206, 235), text="Host proposed <3",
                                    name="host_stat", action=(lambda: None))

        self.buttons.append(self.host_stat_btn)

        self.host_cancel_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                      pos=[int(surfs_size[0] / 4),
                                           int(surfs_size[1] * 0.84)],
                                      color=(250, 128, 114), text="Cancel",
                                      name="cancel_host", action=self.cancel_host_fkt)

        self.buttons.append(self.host_cancel_btn)

        self.back_btn = Button(dim=[int(true_res[0] * 0.03), int(true_res[0] * 0.03)], pos=[0, 0],
                               img_uri=Data.back_btn, text="", name="back_btn",
                               use_dim=True, action=self.back_fkt)

        self.buttons.append(self.back_btn)
        # </editor-fold>

        # <editor-fold desc="Join Buttons">
        self.join_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                               pos=[int(surfs_size[0] / 4),
                                    int(surfs_size[1] / 6)],
                               real_pos=[int(surfs_size[0] / 4) +
                                         self.left_surf.get_width(),
                                         int(surfs_size[1] / 6)],
                               color=(135, 206, 235), text="Join", name="join_btn",
                               action=self.join_btn_fkt)

        self.buttons.append(self.join_btn)

        self.join_stat_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                    pos=[int((surfs_size[0] / 2) / 2),
                                         int(surfs_size[1] * 0.43)],
                                    real_pos=[int((self.right_surf.get_width() - (surfs_size[0] / 2)) / 2) +
                                              self.left_surf.get_width(), int(surfs_size[1] * 0.43)],
                                    color=(135, 206, 235),
                                    text="Join a game UwU", name="join_stat", action=(lambda: None))

        self.buttons.append(self.join_stat_btn)

        # ToDo Rename in Lobby list or create new one
        self.ip_to_join_btn = Button([int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                     pos=[int((self.right_surf.get_width() - (surfs_size[0] / 2)) / 2),
                                          int(surfs_size[1] * 0.7)],
                                     real_pos=[int((self.right_surf.get_width() - (surfs_size[0] / 2)) / 2) +
                                               self.left_surf.get_width(), int(surfs_size[1] * 0.7)],
                                     color=(255, 255, 255),
                                     text="No games hosted", name="ip_to_join_btn", action=self.ip_field_fkt)

        self.buttons.append(self.ip_to_join_btn)
        # this is here for a reason, just don't know which that is
        self.buttons.append(self.desired_board_size_button)

        self.join_cancel_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                      pos=[int((self.right_surf.get_width() - (surfs_size[0] / 2)) / 2),
                                           int(surfs_size[1] * 0.84)],
                                      real_pos=[int((self.right_surf.get_width() - (surfs_size[0] / 2)) / 2) +
                                                self.left_surf.get_width(),
                                                int(surfs_size[1] * 0.84)], color=(250, 128, 114), text="Cancel",
                                      name="cancel_join", action=self.cancel_join_fkt)

        self.buttons.append(self.join_cancel_btn)

        # </editor-fold>

        self.content_changed = True
        self.update()

    def update(self):

        # <editor-fold desc="Get and fill hosting list">
        # Asking for tha hosting list all 3 seconds assuming 60 FPS

        # this number has to be big enough to receive the list meanwhile
        if self.get_hosting_list_counter >= 42:  # no pun intended number has a calculation behind it

            new_list = self.client.get_hosting_list()

            # check if hosting list is new
            if not Data.hostin_list_eq(new_list,
                                       self.hosting_list):  # TODO does think that a new list came after reconnecting to server
                self.hosting_list = new_list

                if bool(self.hosting_list):  # if it is full
                    # TODO this is hardcoded; always choosing game 1 from hosting list
                    self.game_to_join = self.hosting_list["Dungeon"]
                    # change text of field in future list
                    self.change_btn_text(self.ip_to_join_btn,
                                         "{}, {} Points".format(self.game_to_join.name, self.game_to_join.points))
                else:

                    self.game_to_join = None
                    self.change_btn_text(self.ip_to_join_btn, "No games hosted")

                self.content_changed = True

            '''print("-"*30 + "\nRec log len:", self.client.connection.get_rec_log_len())
            for elem in self.client.connection.get_rec_log_fast(5):
                print("\n", elem.to_string())
            print()'''

            self.get_hosting_list_counter = 0
        else:
            self.get_hosting_list_counter += 1

            ''' At a later point, the ip_to_join_button should be reworked as a list, containing 1 button per 
            game in the hosting list. If you click the button, the corresponding game should be game_to_join. 
            Clicking the join button should do the joining then'''

        # </editor-fold>

        if self.size_focus or self.ip_focus:
            self.content_changed = True

        if self.content_changed:
            self.reblit()

    def reblit(self):

        self.left_surf.blit(self.host_btn.surf, self.host_btn.pos)
        self.left_surf.blit(self.desired_board_size_button.surf, self.desired_board_size_button.pos)
        self.left_surf.blit(self.host_stat_btn.surf, self.host_stat_btn.pos)
        self.left_surf.blit(self.host_cancel_btn.surf, self.host_cancel_btn.pos)

        self.right_surf.blit(self.join_btn.surf, self.join_btn.pos)
        self.right_surf.blit(self.join_stat_btn.surf, self.join_stat_btn.pos)
        self.right_surf.blit(self.join_cancel_btn.surf, self.join_cancel_btn.pos)
        self.right_surf.blit(self.ip_to_join_btn.surf, self.ip_to_join_btn.pos)

        self.left_surf.blit(self.back_btn.surf, self.back_btn.pos)
        # put right and left surface to screen

        self.screen.blit(self.left_surf, (0, 0))
        self.screen.blit(self.right_surf, (self.surfs_size[0], 0))

        self.content_changed = False

    def event_handling(self):

        ret = False

        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                '''self.host_thread = 0
                self.join_thread = 0
                self.client.kill_connection()'''
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            if event.type == pg.KEYDOWN:
                ret = True
                prev_desi_board_text = self.desi_board_text
                if event.key == pg.K_KP0:
                    if self.ip_focus:
                        self.ip_field_text += "0"
                    elif self.size_focus:
                        self.desi_board_text += "0"
                    else:
                        pass

                if event.key == pg.K_KP1:
                    if self.ip_focus:
                        self.ip_field_text += "1"
                    elif self.size_focus:
                        self.desi_board_text += "1"
                    else:
                        pass

                if event.key == pg.K_KP2:
                    if self.ip_focus:
                        self.ip_field_text += "2"
                    elif self.size_focus:
                        self.desi_board_text += "2"
                    else:
                        pass

                if event.key == pg.K_KP3:
                    if self.ip_focus:
                        self.ip_field_text += "3"
                    elif self.size_focus:
                        self.desi_board_text += "3"
                    else:
                        pass

                if event.key == pg.K_KP4:
                    if self.ip_focus:
                        self.ip_field_text += "4"
                    elif self.size_focus:
                        self.desi_board_text += "4"
                    else:
                        pass

                if event.key == pg.K_KP5:
                    if self.ip_focus:
                        self.ip_field_text += "5"
                    elif self.size_focus:
                        self.desi_board_text += "5"
                    else:
                        pass

                if event.key == pg.K_KP6:
                    if self.ip_focus:
                        self.ip_field_text += "6"
                    elif self.size_focus:
                        self.desi_board_text += "6"
                    else:
                        pass

                if event.key == pg.K_KP7:
                    if self.ip_focus:
                        self.ip_field_text += "7"
                    elif self.size_focus:
                        self.desi_board_text += "7"
                    else:
                        pass

                if event.key == pg.K_KP8:
                    if self.ip_focus:
                        self.ip_field_text += "8"
                    elif self.size_focus:
                        self.desi_board_text += "8"
                    else:
                        pass

                if event.key == pg.K_KP9:
                    if self.ip_focus:
                        self.ip_field_text += "9"
                    elif self.size_focus:
                        self.desi_board_text += "9"
                    else:
                        pass

                if event.key == pg.K_0:
                    if self.ip_focus:
                        self.ip_field_text += "0"
                    elif self.size_focus:
                        self.desi_board_text += "0"
                    else:
                        pass

                if event.key == pg.K_1:
                    if self.ip_focus:
                        self.ip_field_text += "1"
                    elif self.size_focus:
                        self.desi_board_text += "1"
                    else:
                        pass

                if event.key == pg.K_2:
                    if self.ip_focus:
                        self.ip_field_text += "2"
                    elif self.size_focus:
                        self.desi_board_text += "2"
                    else:
                        pass

                if event.key == pg.K_3:
                    if self.ip_focus:
                        self.ip_field_text += "3"
                    elif self.size_focus:
                        self.desi_board_text += "3"
                    else:
                        pass

                if event.key == pg.K_4:
                    if self.ip_focus:
                        self.ip_field_text += "4"
                    elif self.size_focus:
                        self.desi_board_text += "4"
                    else:
                        pass

                if event.key == pg.K_5:
                    if self.ip_focus:
                        self.ip_field_text += "5"
                    elif self.size_focus:
                        self.desi_board_text += "5"
                    else:
                        pass

                if event.key == pg.K_6:
                    if self.ip_focus:
                        self.ip_field_text += "6"
                    elif self.size_focus:
                        self.desi_board_text += "6"
                    else:
                        pass

                if event.key == pg.K_7:
                    if self.ip_focus:
                        self.ip_field_text += "7"
                    elif self.size_focus:
                        self.desi_board_text += "7"
                    else:
                        pass

                if event.key == pg.K_8:
                    if self.ip_focus:
                        self.ip_field_text += "8"
                    elif self.size_focus:
                        self.desi_board_text += "8"
                    else:
                        pass

                if event.key == pg.K_9:
                    if self.ip_focus:
                        self.ip_field_text += "9"
                    elif self.size_focus:
                        self.desi_board_text += "9"
                    else:
                        pass

                for char in "abcdefghijklmnopqrstuvwxyz":
                    if event.key == ord(char) and self.ip_focus:
                        self.ip_field_text += str(char)

                if event.key == pg.K_PERIOD:
                    self.ip_field_text += "."
                if event.key == pg.K_KP_PERIOD:
                    self.ip_field_text += "."

                if event.key == pg.K_BACKSPACE:

                    if self.ip_focus:
                        self.ip_field_text = self.ip_field_text[:-1]
                    elif self.size_focus:
                        self.desi_board_text = self.desi_board_text[:-1]
                    else:
                        pass

                '''if self.ip_focus:
                    self.buttons[6].update_text()
                if self.size_focus:
                    self.buttons[7].update_text()'''
                if prev_desi_board_text != self.desi_board_text:
                    self.desired_board_size_button.change_text(self.desi_board_text)
                    self.content_changed = True

            if event.type == pg.MOUSEBUTTONDOWN:
                ret = True
                if pg.mouse.get_pressed()[0]:
                    for b in self.buttons:
                        if b.is_focused(pg.mouse.get_pos()):
                            b.action()
                            self.content_changed = True

        return ret

    # <editor-fold desc="Host button functions">
    # button functions need to be defined before buttons

    def desired_board_size_button_fkt(self):

        self.size_focus = True
        self.ip_focus = False

        if self.board_first_click:
            self.desi_board_text = ""  # TODO still needed?
            self.desired_board_size_button.change_text("")
            self.board_first_click = False

    def host_btn_fkt(self):
        self.size_focus = False
        self.ip_focus = False
        if not self.host_thread:
            self.host_thread = start_new_thread(self.host_btn_fkt, ())
            return
        if self.host_thread and get_ident() == self.host_thread:

            # do not host while the size is not entered yet
            invalid_map_size = True
            while invalid_map_size:
                try:
                    self.field_size = max(int(self.desi_board_text), 23)  # TODO split by ", " and get name too
                    invalid_map_size = False
                except ValueError:
                    print("")
                    traceback.print_exc()
                    print("Exception in Render in line 556!")
                    self.change_btn_text(self.host_stat_btn, "Enter map size!")
                    return

            self.change_btn_text(self.host_stat_btn, "Generating map...")

            # generate Map for the game
            # TODO generate map png and attach it to map for better rendering performance
            self.game_map_string = Map.MapBuilder().build_map(self.field_size)
            self.map_points = Data.points_to_spend_per_team(self.game_map_string.size_x, self.game_map_string.size_y)

            self.change_btn_text(self.host_stat_btn, "Hosting ...")

            # send the data to the server
            self.client.host_game("Dungeon", self.game_map_string.get_map(), self.map_points)

            # start getting in game stat
            self.client.get_in_game_stat_from_server(True)

            self.change_btn_text(self.host_stat_btn, "Waiting for opp..")

            # while you are not in a game yet (aka nobody has joined your hosted game)
            # while True:  # TODO change back ... wtf of this is changed back, cancel doesn't work anymore
            while not self.client.get_in_game_stat():
                # kill the thread if outer conditions changed
                if self.host_thread == 0:
                    return
                time.sleep(0.5)

            self.client.get_hosting_list_from_server(False)
            self.client.get_in_game_stat_from_server(False)

            self.role = "host"
            # host is always team 0
            self.team_number = 0
            # go to char select if somebody has joined your game
            self.new_window_target = CharacterSelection
            return

    def cancel_host_fkt(self):
        self.size_focus = False
        self.ip_focus = False

        if self.host_thread:
            self.host_thread = 0
            self.client.cancel_hosting()
            self.change_btn_text(self.host_stat_btn, "Cancelled, fucker!")

    def back_fkt(self):
        self.size_focus = False
        self.ip_focus = False
        self.new_window_target = MainWindow

    # </editor-fold>

    # <editor-fold desc="Join Button functions">
    def join_btn_fkt(self):
        self.size_focus = False
        self.ip_focus = False
        if not self.join_thread:
            self.join_thread = start_new_thread(self.join_btn_fkt, ())
            return
        if self.join_thread and get_ident() == self.join_thread:

            # no game was selected
            if not self.game_to_join:
                self.change_btn_text(self.join_stat_btn, "Select a game first!")
                return

            # set the map to hosted map
            self.game_map_string = self.game_to_join.game_map
            self.map_points = self.game_to_join.points

            self.client.join(self.game_to_join.name)
            self.client.get_in_game_stat_from_server(True)

            self.change_btn_text(self.join_stat_btn, "Joining...")

            # wait until the server thinks that I am in a game
            while not self.client.get_in_game_stat():
                if not self.join_thread:
                    return
                time.sleep(0.05)

            self.client.get_hosting_list_from_server(False)
            self.client.get_in_game_stat_from_server(False)

            self.role = "client"
            self.team_number = 1
            self.new_window_target = CharacterSelection

    def cancel_join_fkt(self):  # TODO add network communication?
        self.size_focus = False
        self.ip_focus = False
        self.join_thread = 0
        self.change_btn_text(self.join_stat_btn, "Cancelled!")
        self.content_changed = True

    def hosted_game_fkt(self):
        self.size_focus = False
        self.ip_focus = False
        self.content_changed = True  # TODO put this where it belongs (after screen change is intended)
        # TODO select corresponding game from button text as game to join
        pass

    def ip_field_fkt(self):
        # on first click erase content, else do nothing
        self.size_focus = False
        self.ip_focus = True
        if self.first_click:
            self.first_click = False

    def change_btn_text(self, btn, text):
        btn.change_text(text)
        self.content_changed = True

    # </editor-fold>

    def harakiri(self):
        del self


class CharacterSelection:  # commit comment

    def __init__(self, points_to_spend, game_map, role="unknown", team_numberr=0, client=None):
        # let only those things be here that are not to be reset every frame, so i.e. independent of window size

        # <editor-fold desc="vars">
        size = true_res

        self.points_to_spend = points_to_spend
        self.game_map = game_map
        self.role = role
        self.client = client
        self.new_window_target = None
        self.spent_points = 0
        self.screen = pg.display.set_mode(true_res)  # , pg.RESIZABLE | pg.FULLSCREEN) # TODO put back in
        self.team_numberr = team_numberr
        self.ownTeam = Team(team_number=team_numberr)  # ToDo Network Team?
        self.ready_thread = 0
        self.selectedChar = None
        self.weapons = []
        self.gear = []
        self.items = []
        self.ready = None
        self.ready_checker_counter = 0
        self.cc_num = 6  # number of character cards
        self.gc_num = 4
        self.wc_num = 7
        self.ic_num = 3
        self.timer_list = TTimer(3)  # too expensive, already ready, point limit reached
        self.font_surf = None

        self.render_char_ban = True
        self.char_banner_clicked = False
        self.render_gear_ban = True
        self.gear_banner_clicked = False
        self.render_weap_ban = True
        self.weapon_banner_clicked = False
        self.render_item_ban = True
        self.item_banner_clicked = False

        self.scroll_offset = 0
        self.scroll = False
        self.invisible = -10000
        # </editor-fold>

        # -------------------------------------------------------------------------------------------------------------
        # I'm gonna do what's called a pro gamer move: load assets in init!
        # -------------------------------------------------------------------------------------------------------------

        # <editor-fold desc="Just pro">
        self.cc_small_images = []
        for i in range(self.cc_num):
            # load small preview pics for buttons
            img = pg.image.load(Data.cc_smol_prefix + str(i) + ".png").convert_alpha()
            self.cc_small_images.append(img)

        self.gc_small_images = []
        for i in range(self.gc_num):
            # load small preview pics for buttons
            img = pg.image.load(Data.gc_smol_prefix + str(i) + ".png").convert_alpha()
            self.gc_small_images.append(img)

        self.wc_small_images = []
        for i in range(self.wc_num):
            img = pg.image.load(Data.wc_smol_prefix + str(i) + ".png").convert_alpha()
            self.wc_small_images.append(img)

        self.ic_small_images = []
        for i in range(self.ic_num):
            img = pg.image.load(Data.ic_smol_prefix + str(i) + ".png").convert_alpha()
            self.ic_small_images.append(img)

        # </editor-fold>

        # -------------------------------------------------------------------------------------------------------------
        # set up surfaces for screen
        # -------------------------------------------------------------------------------------------------------------

        #############
        # left side #
        #############

        # <editor-fold desc="left side">
        # character cards go here as buttons
        self.troop_overview = pg.Surface([int(0.7 * size[0]), size[1] * 10])  # make very long for scroll stuff

        self.player_overview = pg.Surface([int(0.3 * size[0]), size[1]])

        # some vars and constants
        self.character_cards = []
        self.weapon_cards = []
        self.item_cards = []
        self.gear_cards = []
        self.banners = []
        self.team_char_btns = []
        self.sel_item_btns = []

        # room between cards should be 1/8 of their width, 5 cards per line makes 6 spaces, so 5* 8/8 + 6 * 1/8
        # = 46/8, so the width has to be split in 46 equal parts where 1/46 makes the space between 2 cards
        # 46 = line_len * 9 + 1

        # to blit button on
        self.rem_points_back = pg.Surface([self.troop_overview.get_width(), int(size[1] * 0.1)])

        # to blit character_banner and character_content on
        self.line_len = 5
        self.card_w = int(self.troop_overview.get_width() * 8 / (self.line_len * 9 + 1))
        self.card_h = int(self.card_w * 1.457)
        self.gap_size = int(self.troop_overview.get_width() / (self.line_len * 9 + 1))

        # sneaky asset loading here bc now we know everything
        rusty_metal_img = pg.transform.smoothscale(
            pg.image.load(Data.rusty_metal),
            [int(self.troop_overview.get_width() * 0.9), int(self.card_h / 2)]
        )

        self.character_back = pg.Surface([self.troop_overview.get_width(),
                                          int(2 * self.gap_size +
                                              int(math.ceil(self.cc_num / self.line_len) * self.card_h) +
                                              int(self.cc_num / self.line_len) * self.gap_size +
                                              int(self.card_h * 0.5))])
        self.character_content = pg.Surface(
            [self.character_back.get_width(), self.character_back.get_height() - int(self.card_h / 2)])

        self.gear_back = pg.Surface([self.troop_overview.get_width(),
                                     int(2 * self.gap_size +
                                         int(math.ceil(self.gc_num / self.line_len) * self.card_h) +
                                         int(self.gc_num / self.line_len) * self.gap_size +
                                         int(self.card_h * 0.5))])
        self.gear_content = pg.Surface([self.gear_back.get_width(), self.gear_back.get_height() - int(self.card_h / 2)])

        self.weapon_back = pg.Surface([self.troop_overview.get_width(),
                                       int(2 * self.gap_size +
                                           int(math.ceil(self.wc_num / self.line_len) * self.card_h) +
                                           int(self.wc_num / self.line_len) * self.gap_size +
                                           int(self.card_h * 0.5))])
        self.weapon_content = pg.Surface(
            [self.weapon_back.get_width(), self.weapon_back.get_height() - int(self.card_h / 2)])

        self.item_back = pg.Surface([self.troop_overview.get_width(),
                                     int(2 * self.gap_size +
                                         int(math.ceil(self.ic_num / self.line_len) * self.card_h) +
                                         int(self.ic_num / self.line_len) * self.gap_size +
                                         int(self.card_h * 0.5))])
        self.item_content = pg.Surface([self.item_back.get_width(), self.item_back.get_height() - int(self.card_h / 2)])

        # </editor-fold>

        ##############
        # right side #
        ##############

        # <editor-fold desc="right side">
        mini = max(int(0.3 * size[0]), int(0.2 * size[1]))
        self.minimap_surf = pg.Surface([mini, mini])

        self.game_map.draw_map()
        self.map_surf = fit_surf(pg.Surface([self.minimap_surf.get_width(), int(self.minimap_surf.get_height() * 0.8)]),
                                 self.game_map.window)

        # ---------------

        self.selected_units_back = pg.Surface([int(0.3 * size[0]), int((size[1] - self.minimap_surf.get_height()) / 2)])
        if debug:
            self.selected_units_back.fill((255, 0, 0))
        '''
        # NEWWW
        sel_uni_back_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert_alpha(),
                                                         self.selected_units_back.get_size())
        self.selected_units_back.blit(sel_uni_back_back_img, [0, 0])
        '''

        self.selected_units_box = pg.Surface(
            [self.selected_units_back.get_width() - 10, self.selected_units_back.get_height() - 10])

        # NEWWW
        sel_uni_box_back_img = pg.transform.smoothscale(pg.image.load(Data.metal_btn).convert_alpha(),
                                                        self.selected_units_box.get_size())
        self.selected_units_box.blit(sel_uni_box_back_img, [0, 0])

        # --------------

        self.selected_weapons_back = pg.Surface(
            [int(0.3 * size[0]), int((size[1] - self.minimap_surf.get_height()) / 2)])
        if debug:
            self.selected_weapons_back.fill((0, 255, 0))

        self.selected_weapons_box = pg.Surface([self.selected_weapons_back.get_width() - 10,
                                                self.selected_weapons_back.get_height() - 10])

        # NEWWW
        sel_weap_box_back_img = pg.transform.smoothscale(pg.image.load(Data.metal_btn).convert_alpha(),
                                                         self.selected_weapons_box.get_size())
        self.selected_weapons_box.blit(sel_weap_box_back_img, [0, 0])

        # TODO: show items of selected char here

        # constants
        small_line_len = 3
        small_gap_size = int(self.selected_units_box.get_width() / (small_line_len * 9 + 1))
        w_small_card = int(self.selected_units_box.get_width() * 8 / (small_line_len * 9 + 1))
        h_small_card = w_small_card  # int(w_small_card * 1.457)

        # </editor-fold>

        # -------------------------------------------------------------------------------------------------------------
        # set up buttons
        # -------------------------------------------------------------------------------------------------------------

        ########
        # left #
        ########

        def get_points():
            return str(self.spent_points) + "/" + str(self.points_to_spend)

        # don't have to add scroll offset 'cause it's blitted to background
        self.points_btn = Button(dim=[int(self.troop_overview.get_width() * 0.21), int(size[1] * 0.05)], pos=[
            int((self.troop_overview.get_width() - int(self.troop_overview.get_width() * 0.21)) / 2), 0],
                                 font_color=(255, 255, 255), img_uri=Data.rem_points,
                                 text=get_points(), use_dim=True,
                                 action=(lambda: None))

        # #############################################################################################################
        # banners
        # #############################################################################################################

        # <editor-fold desc="Banners">
        def char_ban_func():
            if self.render_char_ban:
                self.character_back = resize_surface_height(self.character_back,
                                                            y_diff=-self.character_content.get_height())
            else:
                self.character_back = resize_surface_height(self.character_back,
                                                            y_diff=self.character_content.get_height())
            self.char_banner_clicked = True
            self.render_char_ban = not self.render_char_ban

        # hide or show character_content on click, height must be card_h/2 and y padding card_h/4
        self.character_banner = Button(dim=[int(self.troop_overview.get_width() * 0.9), int(self.card_h / 2)],
                                       pos=[int(self.troop_overview.get_width() * 0.05), 0],
                                       real_pos=[int(self.troop_overview.get_width() * 0.05),
                                                 self.rem_points_back.get_height() + self.scroll_offset],
                                       #color=(50, 30, 230),
                                       img_source=rusty_metal_img, text="Einheiten", action=char_ban_func)
        self.banners.append(self.character_banner)

        def gear_ban_func():
            if self.render_gear_ban:
                self.gear_back = resize_surface_height(self.gear_back,
                                                       y_diff=-self.gear_content.get_height())
            else:
                self.gear_back = resize_surface_height(self.gear_back,
                                                       y_diff=self.gear_content.get_height())

            self.gear_banner_clicked = True
            self.render_gear_ban = not self.render_gear_ban

        # hide or show content on click, height must be card_h/2 and y padding card_h/4
        self.gear_banner = Button(dim=[int(self.troop_overview.get_width() * 0.9), int(self.card_h / 2)],
                                  pos=[int(self.troop_overview.get_width() * 0.05), 0],
                                  real_pos=[int(self.troop_overview.get_width() * 0.05),
                                            self.rem_points_back.get_height() + self.character_back.get_height() +
                                            self.scroll_offset], #color=(50, 80, 230),
                                  img_source=rusty_metal_img, text="Armor", action=gear_ban_func)
        self.banners.append(self.gear_banner)

        def weap_ban_func():
            if self.render_weap_ban:
                self.weapon_back = resize_surface_height(self.weapon_back,
                                                         y_diff=-self.weapon_content.get_height())
            else:
                self.weapon_back = resize_surface_height(self.weapon_back,
                                                         y_diff=self.weapon_content.get_height())
            self.weapon_banner_clicked = True
            self.render_weap_ban = not self.render_weap_ban

        self.weapon_banner = Button(dim=[int(self.troop_overview.get_width() * 0.9), int(self.card_h / 2)],
                                    pos=[int(self.troop_overview.get_width() * 0.05), 0],
                                    real_pos=[int(self.troop_overview.get_width() * 0.05),
                                              self.rem_points_back.get_height() + self.character_back.get_height() +
                                              self.gear_back.get_height() + self.scroll_offset], #color=(230, 50, 30),
                                    img_source=rusty_metal_img, text="Weapons", action=weap_ban_func)
        self.banners.append(self.weapon_banner)

        def item_ban_func():
            if self.render_item_ban:
                self.item_back = resize_surface_height(self.item_back,
                                                       y_diff=-self.item_content.get_height())
            else:
                self.item_back = resize_surface_height(self.item_back,
                                                       y_diff=self.item_content.get_height())
            self.item_banner_clicked = True
            self.render_item_ban = not self.render_item_ban

        self.item_banner = Button(dim=[int(self.troop_overview.get_width() * 0.9), int(self.card_h / 2)],
                                  pos=[int(self.troop_overview.get_width() * 0.05), 0],
                                  real_pos=[int(self.troop_overview.get_width() * 0.05),
                                            self.rem_points_back.get_height() + self.character_back.get_height() +
                                            self.gear_back.get_height() + self.weapon_back.get_height() +
                                            self.scroll_offset], #color=(30, 230, 50),
                                  img_source=rusty_metal_img, text="Items", action=item_ban_func)
        self.banners.append(self.item_banner)

        # </editor-fold>

        # #############################################################################################################
        # character cards big
        # #############################################################################################################

        # <editor-fold desc="Peaky Binders and their buttons">
        # for push-
        def character_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    char = create_character(card_num, self.team_numberr)
                    if self.spent_points + char.cost <= self.points_to_spend and len(self.ownTeam.characters) < \
                            Data.get_max_chars_per_team(self.game_map.size_x, self.game_map.size_y):
                        self.ownTeam.add_char(char)
                        self.spent_points += char.cost
                        self.selectedChar = char
                    else:
                        # TODO: take out
                        print("Too expensive, cannot buy")
                        self.timer_list.set_timer(0, 2.1)
                else:
                    self.timer_list.set_timer(1, 2.1)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.cc_num):
            w_pos = self.gap_size + ((i % self.line_len) * (self.card_w + self.gap_size))

            h_pos = 2 * self.gap_size + int(i / self.line_len) * self.card_h + (
                    int(i / self.line_len) - 1) * self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos],
                              real_pos=[w_pos,
                                        h_pos +
                                        self.rem_points_back.get_height() +
                                        self.character_banner.dim[1] +
                                        self.scroll_offset],
                              img_uri=(Data.cc_big_prefix + str(i) + ".png"), use_dim=True, text="",
                              action=character_function_binder("cc_btn_function_" + str(i), i))

            self.character_cards.append(card_btn)

        # gear cards big
        def gear_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    btn_gear = make_gear_by_id(card_num)
                    if self.spent_points + btn_gear.cost <= self.points_to_spend and self.selectedChar and \
                            len(self.selectedChar.gear) < 2:
                        got_helmet = False
                        got_armor = False
                        for g in self.selectedChar.gear:
                            if isinstance(g, Helm):
                                got_helmet = True
                            if isinstance(g, Armor):
                                got_armor = True
                        if (isinstance(btn_gear, Helm) and not got_helmet) or \
                                (isinstance(btn_gear, Armor) and not got_armor):
                            self.selectedChar.gear.append(btn_gear)
                            self.spent_points += btn_gear.cost
                    else:
                        self.timer_list.set_timer(0, 2.1)
                else:
                    self.timer_list.set_timer(1, 2.1)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.gc_num):
            w_pos = self.gap_size + ((i % self.line_len) * (self.card_w + self.gap_size))

            h_pos = 2 * self.gap_size + int(i / self.line_len) * self.card_h + (
                    int(i / self.line_len) - 1) * self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos], real_pos=[w_pos,
                                                                                            h_pos +
                                                                                            self.rem_points_back.get_height() +
                                                                                            self.character_back.get_height() +
                                                                                            self.gear_banner.dim[1],
                                                                                            self.scroll_offset],
                              img_uri=(Data.gc_big_prefix + str(i) + ".png"), use_dim=True, text="",
                              action=gear_function_binder("gc_btn_function_" + str(i), i))

            self.gear_cards.append(card_btn)

        # weapon cards big
        def weapon_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    weap = Weapon.make_weapon_by_id(card_num)  # TODO: add function call to get instance of corresponding class
                    if self.spent_points + weap.cost <= self.points_to_spend and self.selectedChar and \
                            len(self.selectedChar.weapons) < 3:
                        self.selectedChar.weapons.append(weap)
                        self.spent_points += weap.cost
                    else:
                        # TODO: take out
                        print("cannot buy")
                        self.timer_list.set_timer(0, 2.1)
                else:
                    self.timer_list.set_timer(1, 2.1)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.wc_num):
            w_pos = self.gap_size + ((i % self.line_len) * (self.card_w + self.gap_size))

            h_pos = 2 * self.gap_size + int(i / self.line_len) * self.card_h + (
                    int(i / self.line_len) - 1) * self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos], real_pos=[w_pos,
                                                                                            h_pos +
                                                                                            self.rem_points_back.get_height() +
                                                                                            self.character_back.get_height() +
                                                                                            self.gear_back.get_height() +
                                                                                            self.weapon_banner.dim[1] +
                                                                                            self.scroll_offset],
                              img_uri=(Data.wc_big_prefix + str(i) + ".png"), use_dim=True, text="",
                              action=weapon_function_binder("wc_btn_function_" + str(i), i))

            self.weapon_cards.append(card_btn)

        # item cards big
        def item_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    item = make_item_by_id(card_num)  # TODO: add function call to get instance of corresponding class
                    if self.spent_points + item.cost <= self.points_to_spend and self.selectedChar and \
                            len(self.selectedChar.items) < 5:
                        self.selectedChar.items.append(item)
                        self.spent_points += item.cost
                    else:
                        # TODO: take out
                        print("Too expensive, cannot buy")
                        self.timer_list.set_timer(0, 2.1)
                else:
                    self.timer_list.set_timer(1, 2.1)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.ic_num):
            w_pos = self.gap_size + ((i % self.line_len) * (self.card_w + self.gap_size))

            #               height of point counter + line_len_factor         *  card height plus gap
            h_pos = 2 * self.gap_size + int(i / self.line_len) * self.card_h + (
                    int(i / self.line_len) - 1) * self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos], real_pos=[w_pos,
                                                                                            h_pos +
                                                                                            self.rem_points_back.get_height() +
                                                                                            self.character_back.get_height() +
                                                                                            self.gear_back.get_height() +
                                                                                            self.weapon_back.get_height() +
                                                                                            self.item_banner.dim[1] +
                                                                                            self.scroll_offset],
                              img_uri=(Data.ic_big_prefix + str(i) + ".png"), use_dim=True, text="",
                              action=item_function_binder("ic_btn_function_" + str(i), i))

            self.item_cards.append(card_btn)

        # </editor-fold>

        #########
        # right #
        #########

        def ready_up():
            self.ready = not self.ready
            self.client.send_char_select_ready(self.ready, self.ownTeam)

        def get_text():
            return "Unready" if self.ready else "Ready!"

        self.ready_btn = Button(
            dim=[int(self.minimap_surf.get_size()[0] * 0.9), int(self.minimap_surf.get_size()[1] * 0.2)],
            pos=[int(self.minimap_surf.get_size()[0] * 0.05), int(self.minimap_surf.get_size()[1] * 0.8)],
            real_pos=[int(self.minimap_surf.get_size()[0] * 0.05) +
                      self.troop_overview.get_size()[0],
                      int(self.minimap_surf.get_size()[1] * 0.8)], img_uri=rusty_metal,
            text=get_text(), action=ready_up)

        # rest has to be handled in update

        self.update()

    # <editor-fold desc="Function binder">
    def cc_function_binder(self, name, unique_char_id):

        def btn_fkt(button):

            if button == 1:
                # show characters items in selected_weapons_box and set him as selected char
                self.selectedChar = self.ownTeam.get_char_by_unique_id(unique_char_id)
            if button == 3:
                # sell this character
                char = self.ownTeam.get_char_by_unique_id(unique_char_id)
                del self.team_char_btns[self.ownTeam.get_index_by_obj(char)]
                self.ownTeam.remove_char_by_obj(char)

                if self.ownTeam.characters.__len__() > 0:
                    self.selectedChar = self.ownTeam.characters[0]
                else:
                    self.selectedChar = None

                self.spent_points -= char.cost
                for g in char.gear:
                    self.spent_points -= g.cost
                for w in char.weapons:
                    self.spent_points -= w.cost
                for i in char.items:
                    self.spent_points -= i.cost

                # self.points_to_spend += char.cost

        btn_fkt.__name__ = name
        return btn_fkt

    def ic_function_binder(self, name, _category, _id):

        def btn_fkt(button=1):
            if button == 3:

                # sell this item
                if _category == "gear":
                    for g in self.gear:
                        if g.my_id == _id:
                            thing_to_sell = g
                            self.spent_points -= thing_to_sell.cost
                            self.gear.remove(g)

                if _category == "weapon":
                    for w in self.weapons:
                        if w.class_id == _id:
                            thing_to_sell = w
                            self.spent_points -= thing_to_sell.cost
                            self.weapons.remove(w)

                if _category == "item":
                    for item in self.items:
                        if item.my_id == _id:
                            thing_to_sell = item
                            self.spent_points -= thing_to_sell.cost
                            self.items.remove(item)

        btn_fkt.__name__ = name
        return btn_fkt

    # </editor-fold>

    def update(self):  # TODO for better performance render only things that changed
        # TODO adjust size of small teamcharbtn dpendent on map points <- NO
        if self.ready:
            if self.ready_checker_counter == 69:  # CHECK EVERY n Seconds
                team_list = self.client.check_for_game_begin()
                if team_list is not None:
                    self.game_map = Map.Map.combine_map(self.game_map, team_list[0], team_list[1])
                    self.new_window_target = InGame
                self.ready_checker_counter = 0
            else:
                self.ready_checker_counter += 1

        # update buttons real positions
        if self.scroll:
            for btn in self.character_cards:
                btn.set_offsets(y_offset=self.scroll_offset)
            for btn in self.weapon_cards:
                btn.set_offsets(y_offset=self.scroll_offset)
            for btn in self.item_cards:
                btn.set_offsets(y_offset=self.scroll_offset)
            for btn in self.gear_cards:
                btn.set_offsets(y_offset=self.scroll_offset)
            for btn in self.banners:
                btn.set_offsets(y_offset=self.scroll_offset)
            self.scroll = False

        # hide'n'seek

        if self.char_banner_clicked:

            for btn in self.character_cards:
                btn.update_real_position(-self.invisible if self.render_char_ban else self.invisible)

            if not self.render_char_ban:
                # change all following real button positions
                self.gear_banner.update_real_position(-self.character_content.get_height())
                for btn in self.gear_cards:
                    btn.update_real_position(-self.character_content.get_height())

                self.weapon_banner.update_real_position(-self.character_content.get_height())
                for btn in self.weapon_cards:
                    btn.update_real_position(-self.character_content.get_height())

                self.item_banner.update_real_position(-self.character_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(-self.character_content.get_height())
            else:
                self.gear_banner.update_real_position(self.character_content.get_height())
                for btn in self.gear_cards:
                    btn.update_real_position(self.character_content.get_height())

                self.weapon_banner.update_real_position(self.character_content.get_height())
                for btn in self.weapon_cards:
                    btn.update_real_position(self.character_content.get_height())

                self.item_banner.update_real_position(self.character_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(self.character_content.get_height())

            self.char_banner_clicked = False

        if self.gear_banner_clicked:
            for btn in self.gear_cards:
                btn.update_real_position(-self.invisible if self.render_gear_ban else self.invisible)

            if not self.render_gear_ban:

                self.weapon_banner.update_real_position(-self.gear_content.get_height())
                for btn in self.weapon_cards:
                    btn.update_real_position(-self.gear_content.get_height())

                self.item_banner.update_real_position(-self.gear_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(-self.gear_content.get_height())

            else:

                self.weapon_banner.update_real_position(self.gear_content.get_height())
                for btn in self.weapon_cards:
                    btn.update_real_position(self.gear_content.get_height())

                self.item_banner.update_real_position(self.gear_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(self.gear_content.get_height())

            self.gear_banner_clicked = False

        if self.weapon_banner_clicked:
            for btn in self.weapon_cards:
                btn.update_real_position(-self.invisible if self.render_weap_ban else self.invisible)

            if not self.render_weap_ban:

                self.item_banner.update_real_position(-self.weapon_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(-self.weapon_content.get_height())

            else:

                self.item_banner.update_real_position(self.weapon_content.get_height())
                for btn in self.item_cards:
                    btn.update_real_position(self.weapon_content.get_height())

            self.weapon_banner_clicked = False

        if self.item_banner_clicked:
            for btn in self.item_cards:
                btn.update_real_position(-self.invisible if self.render_item_ban else self.invisible)
            self.item_banner_clicked = False

        # -------------------------------------------------------------------------------------------------------------
        # own team
        # -------------------------------------------------------------------------------------------------------------

        # constants
        char_small_line_len = 5 if self.ownTeam.characters.__len__() <= 10 else int(
            self.ownTeam.characters.__len__() / 2 + 0.5)
        char_small_gap_size = int(self.selected_units_box.get_width() / (char_small_line_len * 9 + 1))
        char_w_small_card = int(self.selected_units_box.get_width() * 8 / (char_small_line_len * 9 + 1))
        char_h_small_card = char_w_small_card  # int(w_small_card * 1.457)

        self.team_char_btns = []
        for i in range(self.ownTeam.characters.__len__()):
            pos_w = char_small_gap_size + ((i % char_small_line_len) * (char_w_small_card + char_small_gap_size))
            pos_h = 2 * char_small_gap_size + int(i / char_small_line_len) * char_h_small_card + (
                    int(i / char_small_line_len) - 1) * char_small_gap_size

            class_num = self.ownTeam.characters[i].class_id

            btn = Button(dim=[char_w_small_card, char_h_small_card],
                         pos=[pos_w, pos_h],
                         real_pos=[pos_w +
                                   int((self.selected_units_back.get_width() -
                                        self.selected_units_box.get_width()) / 2) +
                                   self.troop_overview.get_width(),
                                   pos_h +
                                   int((self.selected_units_back.get_height() -
                                        self.selected_units_box.get_height()) / 2) +
                                   self.minimap_surf.get_height()],
                         img_uri=(Data.cc_smol_prefix + str(class_num) + ".png"),
                         use_dim=True,
                         text="",
                         action=self.cc_function_binder("cc_small_btn_func" + str(i), self.ownTeam.characters[i].idi))

            self.team_char_btns.append(btn)

        # ----------------------------------------------------------
        # equipped items and stuff
        # ----------------------------------------------------------

        if self.selectedChar is not None:
            self.gear = self.selectedChar.gear
            self.weapons = self.selectedChar.weapons
            self.items = self.selectedChar.items
        else:
            self.gear = []
            self.weapons = []
            self.items = []

        gear_small_line_len = 5 if self.gear.__len__() + self.weapons.__len__() + self.items.__len__() <= 10 else \
            int(self.gear.__len__() / 2 + 0.5)
        gear_small_gap_size = int(self.selected_units_box.get_width() / (gear_small_line_len * 9 + 1))
        gear_w_small_card = int(self.selected_units_box.get_width() * 8 / (gear_small_line_len * 9 + 1))
        gear_h_small_card = gear_w_small_card  # int(w_small_card * 1.457)

        self.sel_item_btns = []
        for i in range(self.gear.__len__() + self.weapons.__len__() + self.items.__len__()):

            pos_w = gear_small_gap_size + ((i % gear_small_line_len) * (gear_w_small_card + gear_small_gap_size))
            pos_h = 2 * gear_small_gap_size + int(i / gear_small_line_len) * gear_h_small_card + (
                    int(i / gear_small_line_len) - 1) * gear_small_gap_size

            img_source = ""
            cat = None
            my_id = 0

            if i < self.gear.__len__():
                my_id = self.gear[i].my_id
                img_source = self.gc_small_images[my_id]
                cat = "gear"

            if self.gear.__len__() <= i < self.weapons.__len__() + self.gear.__len__():
                my_id = self.weapons[i - self.gear.__len__()].class_id  # TODO list index out of range???
                img_source = self.wc_small_images[my_id]
                cat = "weapon"

            if i >= self.gear.__len__() + self.weapons.__len__():
                my_id = self.items[i - self.gear.__len__() - self.weapons.__len__()].my_id
                img_source = self.ic_small_images[my_id]
                cat = "item"

            btn = Button(dim=[gear_w_small_card, gear_h_small_card], pos=[pos_w, pos_h], real_pos=
            [pos_w +
             self.troop_overview.get_width() +
             int((self.selected_weapons_back.get_width() - self.selected_weapons_box.get_width()) / 2),
             pos_h +
             self.minimap_surf.get_height() +
             self.selected_units_back.get_height() +
             int((self.selected_weapons_back.get_height() - self.selected_weapons_box.get_height()) / 2)],
                         text="", img_source=img_source, use_dim=True,
                         action=self.ic_function_binder("ic_small_btn_func" + str(i), _category=cat, _id=my_id))

            self.sel_item_btns.append(btn)

        # -------------------------------------------------------------------------------------------------------------
        # now blit everything to the desired position
        # -------------------------------------------------------------------------------------------------------------

        ########
        # left #
        ########

        # TODO: blit background image

        # maybe add big image of selected char and selected weap at left side ...
        # or maybe not 'cause you'd have to rework button positions again

        # cards and banners
        # <editor-fold desc="cards and banners">
        self.character_back.blit(self.character_banner.surf, self.character_banner.pos)
        if self.render_char_ban:
            if debug:
                self.character_content.fill((8, 63, 240))
            for char_btn in self.character_cards:
                self.character_content.blit(char_btn.surf, char_btn.pos)
            self.character_back.blit(self.character_content, [0, self.character_banner.dim[1]])

        self.gear_back.blit(self.gear_banner.surf, self.gear_banner.pos)
        if self.render_gear_ban:
            if debug:
                self.gear_content.fill((78, 76, 56))
            for gear_btn in self.gear_cards:
                self.gear_content.blit(gear_btn.surf, gear_btn.pos)
            self.gear_back.blit(self.gear_content, [0, self.gear_banner.dim[1]])

        self.weapon_back.blit(self.weapon_banner.surf, self.weapon_banner.pos)
        if self.render_weap_ban:
            if debug:
                self.weapon_content.fill((63, 240, 8))
            for weapon_btn in self.weapon_cards:
                self.weapon_content.blit(weapon_btn.surf, weapon_btn.pos)
            self.weapon_back.blit(self.weapon_content, [0, self.weapon_banner.dim[1]])

        self.item_back.blit(self.item_banner.surf, self.item_banner.pos)
        if self.render_item_ban:
            if debug:
                self.item_content.fill((240, 8, 63))
            for item_btn in self.item_cards:
                self.item_content.blit(item_btn.surf, item_btn.pos)
            self.item_back.blit(self.item_content, [0, self.item_banner.dim[1]])
        # </editor-fold>

        # TODO fill here with background image

        self.troop_overview.fill((0, 0, 0))

        self.troop_overview.blit(self.character_back, dest=[0, self.rem_points_back.get_height()])
        self.troop_overview.blit(self.gear_back, dest=[0, self.rem_points_back.get_height() +
                                                       self.character_back.get_height()])
        self.troop_overview.blit(self.weapon_back, dest=[0, self.rem_points_back.get_height() +
                                                         self.character_back.get_height() +
                                                         self.gear_back.get_height()])
        self.troop_overview.blit(self.item_back,
                                 dest=[0, self.rem_points_back.get_height() + self.character_back.get_height() +
                                       self.gear_back.get_height() + self.weapon_back.get_height()])

        if any(self.timer_list.timers):

            text = "Error"
            if self.timer_list.timers[0]:
                text = "Punktelimit erreicht! (That will never fit, senpai >///<)"
            if self.timer_list.timers[1]:
                text = "Du bist schon bereit! Klicke \"Unready\" um deine Armee zu ändern"

            font_size = int(0.025 * true_res[0])
            font = pg.font.SysFont("comicsansms", font_size)

            self.font_surf = font.render(text, True, (255, 0, 0))
            self.screen.blit(self.font_surf, blit_centered_pos(back=self.screen, surf=self.font_surf))

        #########
        # right #
        #########

        # map and ready btn

        self.minimap_surf.blit(self.map_surf,
                               dest=[int((self.minimap_surf.get_width() - self.map_surf.get_width()) / 2),
                                     int((int(self.minimap_surf.get_height() * 0.8) -
                                          self.map_surf.get_height()) / 2)])
        self.ready_btn.set_text("Ready!" if not self.ready else "Unready")
        self.ready_btn.update_text()

        self.minimap_surf.blit(self.ready_btn.surf, self.ready_btn.pos)

        self.player_overview.blit(self.minimap_surf, dest=[0, 0])

        # selected units
        # if not self.team_char_btns:  # was sel item btns

        # self.selected_units_box.fill((0, 0, 0))
        # NEWWW
        sel_uni_box_back_img = pg.transform.smoothscale(pg.image.load(Data.metal_btn).convert_alpha(),
                                                        self.selected_units_box.get_size())
        self.selected_units_box.blit(sel_uni_box_back_img, [0, 0])

        for sm_char_btn in self.team_char_btns:
            self.selected_units_box.blit(sm_char_btn.surf, sm_char_btn.pos)

        self.selected_units_back.blit(self.selected_units_box, dest=
        [int((self.selected_units_back.get_width() -
              self.selected_units_box.get_width()) / 2),
         int((self.selected_units_back.get_height() -
              self.selected_units_box.get_height()) / 2)])

        self.player_overview.blit(self.selected_units_back, dest=[0, self.minimap_surf.get_height()])

        # selected weapons

        # self.selected_weapons_box.fill((0, 0, 0))

        # NEWWW
        sel_weap_box_back_img = pg.transform.smoothscale(pg.image.load(Data.metal_btn).convert_alpha(),
                                                         self.selected_weapons_box.get_size())
        self.selected_weapons_box.blit(sel_weap_box_back_img, [0, 0])

        for sel_item_btn in self.sel_item_btns:
            self.selected_weapons_box.blit(sel_item_btn.surf, sel_item_btn.pos)

        self.selected_weapons_back.blit(self.selected_weapons_box, dest=blit_centered_pos(self.selected_weapons_back,
                                                                                          self.selected_weapons_box))

        self.player_overview.blit(self.selected_weapons_back, dest=
        [0, self.minimap_surf.get_height() + self.selected_units_back.get_height()])

        ###########################
        # right and left together #
        ###########################

        self.screen.blit(self.troop_overview, [0, self.scroll_offset])

        # points button
        self.points_btn.set_text((str(self.spent_points) + "/" + str(self.points_to_spend)))
        self.points_btn.update_text()
        '''self.rem_points_back.fill((1, 1, 1))
        self.rem_points_back.set_colorkey((1, 1, 1))'''
        self.rem_points_back.blit(self.points_btn.surf, dest=self.points_btn.pos)
        self.screen.blit(self.rem_points_back, dest=[int((self.troop_overview.get_width() -
                                                          self.rem_points_back.get_width()) / 2), 0])

        self.screen.blit(self.player_overview, [self.troop_overview.get_width(), 0])  # make

        if any(self.timer_list.timers):
            self.screen.blit(self.font_surf, blit_centered_pos(back=self.screen, surf=self.font_surf))

    def event_handling(self):
        # TODO only request char buttons if theirs rect is contained in map_surf
        # event handling
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:

                if event.key == ord("q"):
                    pg.quit()
                    sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()

                if event.button == 1:  # on left click
                    for banner_btn in self.banners:
                        if banner_btn.is_focused(p):
                            banner_btn.action()

                    for button in self.character_cards:
                        if button.is_focused(p):
                            button.action()

                    for button in self.gear_cards:
                        if button.is_focused(p):
                            button.action()

                    for button in self.weapon_cards:
                        if button.is_focused(p):
                            button.action()

                    for button in self.item_cards:
                        if button.is_focused(p):
                            button.action()

                    for button in self.team_char_btns:
                        if button.is_focused(p):
                            button.action(1)

                    for button in self.sel_item_btns:
                        if button.is_focused(p):
                            button.action()

                    if self.ready_btn.is_focused(p):
                        self.ready_btn.action()

                if event.button == 3:  # on right click

                    for button in self.team_char_btns:
                        if button.is_focused(p):
                            button.action(3)

                    for button in self.sel_item_btns:
                        if button.is_focused(p):
                            button.action(3)

                if event.button == 4:  # scroll up

                    self.scroll = True
                    self.scroll_offset += 300
                    self.scroll_offset = min(self.scroll_offset, 0)

                if event.button == 5:  # scroll down

                    self.scroll = True
                    self.scroll_offset -= 300
                    self.scroll_offset = max(self.scroll_offset, -(max(self.character_back.get_height() +
                                                                       self.gear_back.get_height() +
                                                                       self.weapon_back.get_height() +
                                                                       self.item_back.get_height() -
                                                                       true_res[1] + self.rem_points_back.get_height(),
                                                                       0)))

    def harakiri(self):
        del self


class InGame:

    def __init__(self, own_team, game_map, client=None, mode="TDM"):

        # <editor-fold desc="Initialisation">

        self.game_map = game_map
        self.client = client
        self.game_mode = mode
        self.own_team = Team(self.client.live_data["game_begin"][own_team.team_num].characters, own_team.team_num)

        self.cc_num = 6
        self.gc_num = 4
        self.wc_num = 7
        self.ic_num = 7

        w = true_res[0]
        h = true_res[1]

        self.new_window_target = None
        self.char_prev_selected = False  # holds whether own team character is already selected
        self.r_fields = []

        self.element_size = (true_res[0] * 9) / (16 * max(self.game_map.size_y, self.game_map.size_x))  # was int
        self.current_element_size = self.element_size
        self.dest = [0, 0]

        self.zoom_factor = 1
        self.mouse_pos = pg.mouse.get_pos()
        self.zoomed = False
        self.amount = [0, 0]
        self.old_factor = 1

        self.move_char = False  # has a char moved? used for rendering
        self.used_chars = []  # holds list of chars that already made an action this turn and are not usable anymore

        self.lines = []
        self.current_line = None

        self.turn_wait_counter = 0
        self.turn_get_thread = 0

        self.opp_turn_applying = False  # enemy turn is displayed atm
        self.is_it_my_turn = self.own_team.team_num == 0
        self.own_turn = Turn()
        self.opps_turn = None
        self.opp_turn_list = []
        self.opp_turn_timestamp = -1
        self.moved_chars = dict()
        self.shot_chars = dict()

        self.overlay = None
        self.overlay_btn = []
        self.dmg_done_timer = 0
        self.dmg_done_ = None

        self.shifting = False
        self.shift_start = [0, 0]
        self.con_shift_offset = [0, 0]  # constant offset from shifting the map

        self.screen = pg.display.set_mode(true_res)  # , pg.RESIZABLE | pg.FULLSCREEN)
        # </editor-fold>

        # <editor-fold desc="Place characters on map">
        for char in self.client.live_data["game_begin"][0].characters:
            # first game objs should always be spawning areas
            self.game_map.objects[0].place_character(char)
            # assuming exactly 2 players
            self.game_map.objects.append(char)
            char.confirm()
            self.game_map.characters.append(self.game_map.objects.__len__() - 1)

        for char in self.client.live_data["game_begin"][1].characters:
            # first game objs should always be spawning areas
            self.game_map.objects[1].place_character(char)
            # assuming exactly 2 players
            self.game_map.objects.append(char)
            char.confirm()
            self.game_map.characters.append(self.game_map.objects.__len__() - 1)
        # </editor-fold>

        # holds selected char of own team
        self.selected_own_char = None  # self.own_team.characters[0]

        # holds selected char (maybe from opponent team)
        self.selected_char = self.selected_own_char

        self.selected_own_char_overlay = None

        self.active_slot = None

        self.v_mat = self.game_map.get_vmat()

        # -------------------------------------------------------------------------------------------------------------
        # render image lists
        # -------------------------------------------------------------------------------------------------------------

        # <editor-fold desc="Render image setup">
        self.detail_size = [int((7 / 32) * w - 20), int((4 / 10) * h - 20)]
        self.small_size = [int((5 / 32) * 7 * w / 32), int((5 / 32) * 7 * w / 32)]

        self.detail_char = []
        self.small_char = []
        for i in range(self.cc_num):
            """img = pg.transform.smoothscale(pg.image.load(Data.cc_detail_prefix + str(i) + ".png").convert_alpha(),
                                           self.detail_size)
            self.detail_char.append(img)
            img = pg.transform.smoothscale(pg.image.load(Data.cc_smol_prefix + str(i) + ".png").convert_alpha(),
                                           self.small_size)
            self.small_char.append(img)"""

            debug_img_size = pg.image.load(Data.cc_big_prefix + str(i) + ".png").get_size()
            img = fit_surf(surf=pg.image.load(Data.cc_big_prefix + str(i) + ".png"), size=self.detail_size)
            self.detail_char.append(img)

            """img = fit_surf(surf=pg.image.load(Data.cc_big_prefix + str(i) + ".png"), size=self.small_size)
            self.small_char.append(img)"""

            img = pg.transform.smoothscale(pg.image.load(Data.cc_smol_prefix + str(i) + ".png").convert_alpha(),
                                           self.small_size)
            self.small_char.append(img)

        self.detail_gear = []
        self.small_gear = []
        for i in range(self.gc_num):
            img = pg.transform.smoothscale(pg.image.load(Data.gc_detail_prefix + str(i) + ".png").convert_alpha(),
                                           self.detail_size)
            self.detail_gear.append(img)
            img = pg.transform.smoothscale(pg.image.load(Data.gc_smol_prefix + str(i) + ".png").convert_alpha(),
                                           self.small_size)
            self.small_gear.append(img)

        self.detail_weapon = []
        self.small_weapon = []
        for i in range(self.wc_num):
            img = pg.transform.smoothscale(pg.image.load(Data.wc_detail_prefix + str(i) + ".png").convert_alpha(),
                                           self.detail_size)
            self.detail_weapon.append(img)
            img = pg.transform.smoothscale(pg.image.load(Data.wc_smol_prefix + str(i) + ".png").convert_alpha(),
                                           self.small_size)
            self.small_weapon.append(img)

        self.detail_item = []
        self.small_item = []
        for i in range(self.ic_num):
            img = pg.transform.smoothscale(pg.image.load(Data.ic_detail_prefix + str(i) + ".png").convert_alpha(),
                                           self.detail_size)
            self.detail_item.append(img)
            img = pg.transform.smoothscale(pg.image.load(Data.ic_smol_prefix + str(i) + ".png").convert_alpha(),
                                           self.small_size)
            self.small_item.append(img)

        self.map_char_imgs = []
        for i in range(self.cc_num):
            img = pg.image.load(
                Data.cc_smol_prefix + str(i) + ".png").convert_alpha()  # TODO change to actual right images
            self.map_char_imgs.append(img)

        self.detail_back_metall = pg.image.load(Data.metal_btn).convert_alpha()

        self.win_banner = pg.image.load(Data.win_banner_text).convert_alpha()  # add super win banner here
        self.lose_banner = pg.image.load(Data.lose_banner_text).convert_alpha()

        # </editor-fold>

        # -------------------------------------------------------------------------------------------------------------
        # set up surfaces
        # -------------------------------------------------------------------------------------------------------------

        # <editor-fold desc="left">
        # -------------- left -------------------------------

        # surface 1.0 and 1.1
        self.char_detail_back = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        # self.char_detail_back.fill((98, 70, 230))
        self.char_stat_card = self.detail_char[0]

        # surface 2 and subsurfaces
        self.char_inventory_back = pg.Surface([int(7 * w / 32), int(4 * h / 18)])
        self.inventory_gear_weapons_surf = pg.Surface(
            [int(7 * w / 32), int(0.34 * 4 * h / 18)])  # 2 first are gear, last 3 are weapons
        self.inventory_items_surf = pg.Surface([int(7 * w / 32), int(0.66 * 4 * h / 18)])  # 2 rows high

        self.item_detail_back = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        self.item_stat_card = pg.image.load(Data.empty_af).convert_alpha() # was self.detail_item[0]
        self.item_stat_card_type = None
        self.gear_bar = None
        # </editor-fold>

        # <editor-fold desc="mid">
        # -------------- mid ----------------------------------

        own_team_height = 2 * int((1 / 32) * 7 * w / 32) + \
                          int((self.own_team.characters.__len__() / 10) + 1) * \
                          ((int((1 / 32) * 7 * w / 32) +  # number of lines * gap size
                            int(1.6 * (5 / 32) * 7 * w / 32)))  # button + hp bar

        self.map_surface = pg.Surface([int(9 * w / 16), h])
        self.game_map.selective_draw_map(team_num=self.own_team.team_num)
        self.map_content = fit_surf(surf=self.game_map.window, back=self.map_surface)

        self.emptiness_of_darkness_of_doom = pg.image.load(Data.empty_af).convert_alpha()
        # convert here, scale returns new copy of emptines, so og remains unchanged and can be reused
        self.opp_turn_surf = pg.transform.scale(self.emptiness_of_darkness_of_doom, self.game_map.window.get_size())

        self.own_team_stats = pg.Surface([int(self.map_surface.get_width() * 0.9), own_team_height])

        # try on blitting alpha
        self.own_team_stats.fill((255, 0, 0))
        self.own_team_stats.set_colorkey((255, 0, 0))

        self.own_team_stats_back_img = pg.transform.smoothscale(
            pg.image.load(Data.team_char_backgr).convert_alpha(),
            self.own_team_stats.get_size())
        # </editor-fold>

        # <editor-fold desc="right">
        # -------------- right ----------------------------------

        # self.player_banners = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        if self.own_team.team_num == 0:
            self.player_banners = pg.transform.scale(pg.image.load(host_banner), [int(7 * w / 32), int(7 * h / 18)])
        else:
            self.player_banners = pg.transform.scale(pg.image.load(client_banner), [int(7 * w / 32), int(7 * h / 18)])

        self.minimap_surf = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        self.done_btn_surf = pg.Surface([int(7 * w / 32), int(4 * h / 18)])

        # </editor-fold>

        # -------------------------------------------------------------------------------------------------------------
        # BUTTONS
        # -------------------------------------------------------------------------------------------------------------

        # <editor-fold desc="button functions">
        # button functions

        def sel_own_char_binder(name, _char):

            def other_func():

                if _char == self.selected_own_char:  # unselect if he was selected
                    self.selected_own_char = None
                    self.selected_char = None
                    self.r_fields = []
                    return

                if _char.is_dead():
                    self.r_fields = []
                    return

                self.selected_own_char = _char
                self.selected_own_char_overlay = _char
                self.selected_char = self.selected_own_char

                self.active_slot = self.selected_own_char.get_active_slot()

                # highlight reachable fields by blitting green transparent stuff over them
                # returns list of tuples
                self.r_fields = self.game_map.get_reachable_fields(self.selected_own_char)

            other_func.__name__ = name
            return other_func

        def done_button_action():
            if self.turn_get_thread == 0:
                self.turn_get_thread = start_new_thread(done_button_action, ())
                return
            else:
                # send the turn out
                self.is_it_my_turn = False
                self.timer.stop_timer()
                self.client.send_turn(self.own_turn, int(round(time.time() * 1000)))
                time.sleep(1)
                return

        self.timer = VisualTimer(amount=60, pos=(0, 0), action=done_button_action)

        # </editor-fold>

        # <editor-fold desc="button inits">
        self.gear_buttons = []
        self.weapon_buttons = []
        self.item_buttons = []

        self.own_team_stat_buttons = []
        self.hp_bars = []

        self.char_map_buttons = []

        # constants
        self.btn_w = int((5 / 32) * 7 * w / 32)
        self.btn_h = self.btn_w
        # self.inventory_gap_size = int((1 / 32) * 7 * w / 32)
        self.inventory_gap_size = int((self.inventory_gear_weapons_surf.get_height() - self.btn_h) / 2)
        self.inventory_line_len = 5
        # </editor-fold>

        # left (inventory buttons moved to update)

        # <editor-fold desc="mid">

        # hp bars, blit to own team stats
        for i in range(self.own_team.characters.__len__()):

            pos_w = self.btn_w + (i % 10) * (self.btn_w + self.inventory_gap_size)
            # pos_h = self.inventory_gap_size + \
            pos_h = int((1 / 32) * 7 * w / 32) + self.btn_h + int(i / 10) * \
                    (self.btn_h + int((1 / 32) * 7 * w / 32) + self.btn_h * 0.8)

            bars = []

            for j in range(6):
                hp_bar = HPBar(dim=[self.btn_w if j>0 else (self.btn_w*default_hp[0])//100, int(0.1 * self.btn_h)],
                               pos=[pos_w, int(pos_h + j * 0.108 * self.btn_h)],  # TODO maybe better number?
                               curr=self.own_team.characters[i].health[j],
                               end=default_hp[j])
                bars.append(hp_bar)

            self.hp_bars.append(bars)

        # team buttons in overview
        for i in range(self.own_team.characters.__len__()):
            pos_w = self.btn_w + (i % 10) * (self.btn_w + self.inventory_gap_size)
            pos_h = self.inventory_gap_size + int(i / 10) * (self.btn_h + self.inventory_gap_size + self.btn_h * 0.6)

            btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                         real_pos=[pos_w +
                                   self.char_detail_back.get_width() +
                                   int(self.map_surface.get_width() * 0.05),
                                   pos_h],
                         img_uri=(Data.cc_smol_prefix + str(self.own_team.characters[i].class_id) + ".png"),
                         text="", name="char btn " + str(self.own_team.characters[i].class_id),
                         action=sel_own_char_binder("char_btn_" + str(self.own_team.characters[i].idi),
                                                    self.own_team.characters[i]))

            self.own_team_stat_buttons.append(btn)

        # chars on map
        v_chars = self.game_map.get_visible_chars_ind(self.own_team.team_num)
        for index in v_chars:
            char = self.game_map.objects[index]
            if not isinstance(char, Character):
                print("Warning! InGame init: sth that is not a char is returned by get_visible_chars_ind!")
                continue
            btn = Button(dim=[int(self.current_element_size), int(self.current_element_size)],

                         pos=[char.get_pos(0) * self.current_element_size,  # no zoom size or anything bc we're in init
                              char.get_pos(1) * self.current_element_size],

                         real_pos=[
                             int((char.get_pos(0) * self.current_element_size) + self.char_detail_back.get_width()),
                             int((char.get_pos(1) * self.current_element_size))],

                         # img_uri="assets/char/" + str(char.unit_class) + ".png",
                         img_source=self.map_char_imgs[char.class_id],
                         action=self.sel_char_binder("map_char_btn_" + str(char.idi), char))

            self.char_map_buttons.append(btn)
        # </editor-fold>

        # <editor-fold desc="right">

        # done button
        self.done_btn = Button(dim=[int(7 * w / 32), int(4 * h / 18)], pos=[0, 0], text="Done",
                               real_pos=[self.char_detail_back.get_width() +
                                         self.map_surface.get_width(),
                                         self.player_banners.get_height() +
                                         self.minimap_surf.get_height()],
                               img_uri=rusty_metal,
                               name="Done", action=done_button_action)
        # </editor-fold>

    def sel_char_binder(self, name, char):

        def func():

            if char.team == self.own_team.team_num:  # own char

                if char == self.selected_own_char:  # unselect if he was selected
                    self.selected_own_char = None
                    self.selected_char = None
                    self.r_fields = []
                    return

                if char.is_dead():
                    self.r_fields = []
                    return

                self.selected_own_char = char
                self.selected_own_char_overlay = char
                self.selected_char = self.selected_own_char

                self.active_slot = self.selected_own_char.get_active_slot()

                # highlight reachable fields by blitting green transparent stuff over them
                # returns list of tuples
                if not (self.selected_own_char.idi in self.moved_chars and self.selected_own_char.idi in self.shot_chars):
                    self.r_fields = self.game_map.get_reachable_fields(self.selected_own_char)

            elif char.team != self.own_team.team_num and self.selected_own_char:  # opp. char

                slot = self.selected_own_char.get_active_slot()

                # attack routine
                current_pos = pg.mouse.get_pos()
                if current_pos[1] >= 400:
                    current_pos = [current_pos[0], current_pos[1] - 375]
                if current_pos[0] >= true_res[0] - self.minimap_surf.get_width() - 150:
                    current_pos = [current_pos[0] - 150, current_pos[1]]

                self.overlay = Overlay((current_pos[0], current_pos[1]), char)
                self.overlay_btn = []
                for i in range(6):
                    btn = Button(dim=self.overlay.btn_dim[i], pos=self.overlay.btn_pos[i],
                                 real_pos=[self.overlay.btn_pos[i][0] - self.char_detail_back.get_width(),
                                           self.overlay.btn_pos[i][1]], name=str(i))
                    self.overlay_btn.append(btn)

            elif char.team != self.own_team.team_num and not self.selected_own_char:

                # just select him as selected char
                self.selected_char = char

            print(self.selected_char)

        func.__name__ = name
        return func

    def inventory_function_binder(self, name, _id, item_type):

        def func_1(mouse_button):

            for i, weapon in enumerate(self.selected_char.weapons):  # was selected char
                if weapon.class_idi == _id:

                    # if you click on the inventory, have an own char selected and not also an enemy char selected
                    if self.selected_own_char and self.is_it_my_turn:

                        self.selected_own_char.change_active_slot("Weapon", i)
                        self.active_slot = self.selected_own_char.get_active_slot()

                    self.item_stat_card = self.detail_weapon[weapon.class_id]
                    self.item_stat_card_type = "Weapon"
                    return

        def func_2(mouse_button):

            if mouse_button == 1:  # left click selects item

                if not self.selected_char:
                    return

                for i, item in enumerate(self.selected_char.items):  # was selected char
                    if item.idi == _id:

                        if self.selected_own_char is self.selected_char:
                            self.selected_own_char.change_active_slot("Item", i)
                            self.active_slot = self.selected_own_char.get_active_slot()

                        self.item_stat_card = self.detail_item[item.my_id]
                        self.item_stat_card_type = "Item"

                        return

            if mouse_button == 3:  # right click uses item

                if not self.selected_own_char:
                    return

                for i, item in enumerate(self.selected_own_char.items):  # was selected char

                    if item.idi == _id:

                        if self.selected_own_char and self.is_it_my_turn:

                            # no need to change active slot here if all items only need 1 turn for usage,
                            # DON'T TAKE THIS COMMENT OUT
                            #   self.selected_own_char.change_active_slot("Item", i)
                            #   self.active_slot = self.selected_own_char.get_active_slot()

                            # you can only use items if you did not move and did not shoot
                            if self.selected_own_char.idi not in self.moved_chars and \
                                    self.selected_own_char.idi not in self.shot_chars:

                                prev_hp = self.selected_own_char.health[:]
                                self.selected_own_char.use_item(i)

                                print("You healed yourself from {} to {}".format(prev_hp, self.selected_own_char.health))

                                for k in range(self.hp_bars.__len__()):
                                    for j in range(6):
                                        self.hp_bars[k][j].update(self.own_team.characters[k].health[j])

                                action = Action(player_a=self.selected_own_char,
                                                dmg2a=[prev_hp[i] - self.selected_own_char.health[i] for i in range(6)],
                                                used_item_index=i)
                                self.own_turn.add_action(action)

                                if self.selected_own_char.items[i].depletes:
                                    del self.selected_own_char.items[i]

                                self.moved_chars[self.selected_own_char.idi] = True
                                self.shot_chars[self.selected_own_char.idi] = True
                                self.selected_own_char = None
                                self.selected_char = None
                                self.r_fields = []

                        return

        if item_type == "weapon":
            func_1.__name__ = name
            return func_1
        if item_type == "item":
            func_2.__name__ = name
            return func_2

    def shoot(self, where):

        if not self.is_it_my_turn:
            return "It's not your turn!"

        if not self.selected_own_char:
            return "No character selected"

        if self.selected_own_char.is_dead():
            return "Your character is dead!"

        if not self.selected_own_char.can_shoot():
            return "Character cannot shoot"

        shoot_impossible = self.selected_own_char.shooting_impossible(self.overlay.boi_to_attack)
        if shoot_impossible:
            return shoot_impossible

        if self.selected_own_char_overlay.idi in self.shot_chars:
            return "You cannot shoot anymore"

        # check if shooter can see target
        shooter_index = self.game_map.get_char_index(self.selected_own_char)
        target_index = self.game_map.get_char_index(self.overlay.boi_to_attack)

        if not self.v_mat[(shooter_index, target_index)][1]:
            return "Cannot see character"

        if self.selected_own_char.shooting_impossible(self.overlay.boi_to_attack):
            return self.selected_own_char.shooting_impossible(self.overlay.boi_to_attack)

        dmg, dmg_done = self.selected_own_char.shoot(self.overlay.boi_to_attack, where)

        self.shot_chars[self.selected_own_char.idi] = True  # (self.selected_own_char, self.overlay.boi_to_attack)

        self.own_turn.add_action(Action(self.selected_own_char, self.overlay.boi_to_attack, dmg2b=dmg_done))

        # unselect char after shooting
        # TODO maybe put back in
        if self.selected_own_char.idi in self.moved_chars:

            self.selected_own_char = None
            self.selected_char = None
            self.r_fields = []

        return dmg

    def apply_opp_turn(self, opp_turn):  # applies changes from opp turn to own game state

        """
        only apply results of changes, not changes (or actions such as use item) themselves except for move

        :param opp_turn:
        :return:
        """

        if opp_turn.win:
            # opp says you win! :)

            self.screen.blit(self.win_banner, blit_centered_pos(self.screen, self.win_banner))
            pg.display.flip()
            time.sleep(8)
            self.client.send_endgame()

            # this exits out of the screen
            self.new_window_target = MainWindow
            return

        # prepare surface
        self.opp_turn_surf = pg.transform.scale(self.emptiness_of_darkness_of_doom, self.game_map.window.get_size())

        opp_char_list = list(filter((lambda a: a.team != self.own_team),
                                    [self.game_map.objects[x] for x in self.game_map.characters]))

        for action in opp_turn.actions:

            opp_char = None
            for c in opp_char_list:
                if c.rand_id == action.player_a.rand_id:
                    opp_char = c

            # copy stats
            opp_char.clone_from_other(action.player_a)

            # this has to stand before moving as moving will change potentially false velocities to the right value
            if action.velocityraptor is not None:  # should only be not none if char did not move
                opp_char.velocity = action.velocityraptor

            if action.path:

                # get this before moving, only draw line if you could see the char from the beginning of the movement
                visible_char_indices = self.game_map.get_visible_chars_ind(self.own_team.team_num)

                opp_char.move(action.player_a.pos)

                # index in game objects
                opp_char_index = self.game_map.get_char_index(opp_char)

                if opp_char_index in visible_char_indices:  # draw movement path

                    pg.draw.aalines(self.opp_turn_surf, (0, 230, 230), False,
                                    [[x[0]*Data.def_elem_size + (Data.def_elem_size//2),
                                      x[1]*Data.def_elem_size + (Data.def_elem_size//2)] for x in action.path], 0)
                    pg.draw.circle(self.opp_turn_surf, (0, 230, 230),
                                   list(
                                       map((lambda x: x * Data.def_elem_size + (Data.def_elem_size // 2)),
                                           action.path[0])),
                                   Data.def_elem_size // 2 // 2)

            if action.player_b:  # there is a second player involved

                my_char = None
                for c in self.own_team.characters:
                    if c.rand_id == action.player_b.rand_id:
                        my_char = c

                if action.dmg2b:
                    my_char.apply_hp_change(action.dmg2b)
                    # blit lines indicating movement and shots
                    self.draw_line_(self.opp_turn_surf, my_char.pos, opp_char.pos, (255, 0, 0))

            if action.dmg2a:
                # he healed himself
                opp_char.apply_hp_change(action.dmg2a)

            # deplete used item
            if action.used_item_index is not None and opp_char.items[action.used_item_index].depletes:
                del opp_char.items[action.used_item_index]

            for i in self.game_map.characters:
                if self.game_map.objects[i].get_bleed():
                    self.game_map.objects[i].timer_tick()

            for i in range(self.hp_bars.__len__()):
                for j in range(6):
                    self.hp_bars[i][j].update(self.own_team.characters[i].health[j])

        # --- check if you win ---
        if self.own_team.all_dead():

            # declare win
            self.own_turn = Turn()
            self.own_turn.win = True  # send opp that he wins
            # send the turn out
            start_new_thread(self.client.send_turn, (self.own_turn, int(round(time.time() * 1000))))

            # prepare showing loss to player
            self.main_blit()
            self.screen.blit(self.lose_banner, blit_centered_pos(self.screen, self.lose_banner))
            pg.display.flip()
            time.sleep(8)
            self.client.send_endgame()

            # exit out
            self.new_window_target = MainWindow
            return

        # --- call tick function for every char from own team ---
        # this is executed if it's your turn AGAIN, not when your turn begins
        for c in self.own_team.characters:
            c.timer_tick()

            # decay velocity for all characters that did not move this turn
            if c.idi not in self.moved_chars:
                c.decay_velocity()
                self.own_turn.add_action(Action(c, velocityraptor=c.velocity))

        # now set v_mat bc positions are set and we only need this once per turn
        self.v_mat = self.game_map.get_vmat()

        # --- reset stuff ---
        self.opp_turn_applying = False
        self.is_it_my_turn = True

        for own_char in self.own_team.characters:
            own_char.moved = False
            own_char.shot = False

        self.moved_chars = dict()
        self.shot_chars = dict()
        self.own_turn = Turn()

        self.timer.start_timer(60)

    def main_blit(self):

        # <editor-fold desc="Render stuff">
        self.mouse_pos = pg.mouse.get_pos()

        """print("\nself.selected_own_char\n",
              self.selected_own_char,
              "\nself.selected_char\n",
              self.selected_char,
              "\nself.active_slot\n",
              self.active_slot,
              "\n")"""

        # <editor-fold desc="build dotted line">
        # build dotted line positions
        if self.selected_own_char and not \
                (self.selected_own_char.idi in self.shot_chars and self.selected_own_char.idi in self.moved_chars):
            start_point = self.mouse_pos

            end_point = [self.current_element_size * self.selected_own_char.pos[0] + self.dest[0] +
                         self.char_detail_back.get_width(),
                         self.current_element_size * self.selected_own_char.pos[1] + self.dest[1]]

            # adjust to middle of field instead of upper left
            end_point = [int(ep + (self.current_element_size / 2)) for ep in end_point]

            line_points = [start_point]
            end_min_start = [end_point[i] - start_point[i] for i in range(start_point.__len__())]

            num_of_parts = 8
            for i in range(1, num_of_parts):
                offset = [int((i / num_of_parts) * x) for x in end_min_start]
                line_points.append([start_point[i] + offset[i] for i in range(len(start_point))])

        else:
            line_points = []
        # </editor-fold>der

        # clear list :)
        self.char_map_buttons = []
        self.gear_buttons = self.item_buttons = self.weapon_buttons = []

        # <editor-fold desc="zoom and shift">
        if self.shifting:
            # current shift offset of this frame?
            shift_offset = [self.mouse_pos[0] - self.shift_start[0],
                            self.mouse_pos[1] - self.shift_start[1]]
        else:
            shift_offset = [0, 0]

        if self.zoomed:  # if zoom was made since last update, set values
            # was 7/32 * w instead of char detail back
            rel_mouse_pos = [self.mouse_pos[0] - self.char_detail_back.get_width(), self.mouse_pos[1]]

            self.current_element_size = self.zoom_factor * self.element_size

            self.amount = [rel_mouse_pos[0] - (self.zoom_factor * rel_mouse_pos[0]),
                           rel_mouse_pos[1] - (self.zoom_factor * rel_mouse_pos[1])]

            self.zoomed = False

        # </editor-fold>

        # <editor-fold desc="char ui left">

        # inventory buttons (left side)
        self.gear_buttons = []
        self.weapon_buttons = []
        self.item_buttons = []

        if self.selected_char:

            if self.selected_char.gear:  # character has gear
                # gear buttons
                for i in range(self.selected_char.gear.__len__()):
                    pos_w = (i + 1) * self.inventory_gap_size + i * self.btn_w
                    pos_h = self.inventory_gap_size

                    def f(_i):  # just change image, dont change held item
                        def inner_func():

                            if self.selected_char:
                                self.item_stat_card = self.detail_gear[self.selected_char.gear[_i].my_id]
                                self.item_stat_card_type = "Gear"

                                self.gear_bar = HPBar(dim=[self.item_detail_back.get_height(),
                                                           self.item_detail_back.get_width()/15],
                                                      curr=self.selected_char.gear[_i].durability,
                                                      end=gear_durability[self.selected_char.gear[_i].my_id],
                                                      vertical=True)

                                self.gear_bar.update(self.selected_char.gear[_i].durability)

                        return inner_func

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w, pos_h + self.char_detail_back.get_height()],
                                 # img_uri="assets/gc/small/gc_" + str(self.selected_own_char.gear[i].my_id) + ".png",
                                 img_source=self.small_gear[self.selected_char.gear[i].my_id], text="",
                                 name=("gear " + str(self.selected_char.gear[i].my_id) + " button"), action=f(i))

                    self.gear_buttons.append(btn)

            if self.selected_char.weapons:
                # weapon buttons
                for i in range(self.selected_char.weapons.__len__()):
                    pos_w = 2 * self.btn_w + 4 * self.inventory_gap_size + i * (self.inventory_gap_size + self.btn_w)
                    pos_h = self.inventory_gap_size

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w,
                                           pos_h +
                                           self.char_detail_back.get_height()],
                                 img_source=self.small_weapon[self.selected_char.weapons[i].class_id],
                                 text="", name=("weapon " + str(self.selected_char.weapons[i].class_id) + ".png"),
                                 action=self.inventory_function_binder(
                                     "weapon " + str(self.selected_char.weapons[i].class_idi),
                                     self.selected_char.weapons[i].class_idi, item_type="weapon"))

                    self.weapon_buttons.append(btn)

            if self.selected_char.items:
                # item buttons
                for i in range(self.selected_char.items.__len__()):
                    pos_w = self.inventory_gap_size + (i % 5) * (self.btn_w + self.inventory_gap_size)
                    pos_h = self.inventory_gap_size + int(i / 5) * (self.btn_h + self.inventory_gap_size)

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w,
                                           pos_h +
                                           self.char_detail_back.get_height() +
                                           self.inventory_gear_weapons_surf.get_height()],
                                 # ="assets/ic/small/ic_" + str(self.selected_own_char.items[i].my_id) + ".png",
                                 img_source=self.small_item[self.selected_char.items[i].my_id], text="",
                                 name=("item " + str(self.selected_char.items[i].my_id) + ".png"),
                                 action=self.inventory_function_binder(
                                     "item " + str(self.selected_char.items[i].idi),
                                     self.selected_char.items[i].idi, item_type="item"))

                    self.item_buttons.append(btn)

        # </editor-fold>

        if self.move_char:  # you have to move the char now

            self.move_char = False
            if self.is_it_my_turn and self.selected_own_char and \
                    (self.selected_own_char.idi not in self.moved_chars):

                # move to clicked field if it is reachable
                rel_mouse_pos = [self.mouse_pos[0] - self.char_detail_back.get_width(),
                                 self.mouse_pos[1]]
                dists_mouse_p_dest = [abs(rel_mouse_pos[0] - self.dest[0]),
                                      abs(rel_mouse_pos[1] - self.dest[1])]
                percentual_mouse_pos_map_len = [dmpd / (self.zoom_factor * self.element_size) for dmpd in
                                                dists_mouse_p_dest]

                # coords of clicked field (potential movement target)
                clicked_coords = [int(x) for x in percentual_mouse_pos_map_len]

                if tuple(clicked_coords) in self.r_fields:

                    prev_pos = self.selected_own_char.pos

                    # turn stuff
                    path = self.game_map.get_path(prev_pos, clicked_coords)
                    self.selected_own_char.dist_moved = len(path) - 1

                    # move char
                    self.selected_own_char.move(list(clicked_coords))
                    self.selected_own_char.moved = True

                    # remember that he already moved
                    self.moved_chars[self.selected_own_char.idi] = path

                    # build an action for turn
                    self.own_turn.add_action(Action(self.selected_own_char, path=path))

                    self.r_fields = []

                    if self.selected_own_char.idi in self.shot_chars:

                        # unselect char after movement if he cannot shoot anymore
                        self.selected_own_char = None
                        self.selected_char = None

                    self.v_mat = self.game_map.get_vmat()

            # you have already moved this char
            elif self.is_it_my_turn and self.selected_own_char and \
                    (self.selected_own_char.idi in self.moved_chars):

                self.r_fields = []
                if self.selected_own_char.idi in self.shot_chars:
                    self.selected_own_char = None
                    self.selected_char = None

                """
                print("Greed is a sin against God,\n "
                      "just as all mortal sins,\n "
                      "in as much as man condemns things\n "
                      "eternal for the sake of temporal things.")"""

            elif not self.is_it_my_turn and self.selected_own_char:

                self.r_fields = []
                self.selected_own_char = None

        ##############################################################################################################
        # blit everything to positions
        ##############################################################################################################

        # <editor-fold desc="left side">
        # ----- left -----

        self.char_detail_back.blit(fit_surf(back=self.char_detail_back, surf=self.detail_back_metall), dest=[0, 0])

        if self.selected_char:
            self.char_stat_card = self.detail_char[self.selected_char.class_id]
            self.char_detail_back.blit(self.char_stat_card, dest=blit_centered_pos(self.char_detail_back,
                                                                                   self.char_stat_card))
            if self.selected_char.get_bleed():
                bleed_drop_surf = pg.transform.scale(pg.image.load(bleed_drop),
                                                     (int(self.char_detail_back.get_width() / 6),
                                                      int(self.char_detail_back.get_height() / 4)))
                self.char_detail_back.blit(bleed_drop_surf, dest=[int(self.char_detail_back.get_width() -
                                                                      self.char_detail_back.get_width()/6), 0])

            dex_hand_surf = pg.transform.scale(pg.transform.rotate(pg.image.load(dex_hand), 45),
                                               (int(self.char_detail_back.get_width() / 6),
                                                int(self.char_detail_back.get_height() / 6)))
            self.char_detail_back.blit(dex_hand_surf, dest=[int(self.char_detail_back.get_width() -
                                                                self.char_detail_back.get_width()/6),
                                                            int(self.char_detail_back.get_height()/3)])

            dex_text_surf = self.timer.myfont_2.render(str(self.selected_char.dexterity), False, (0, 0, 0))
            self.char_detail_back.blit(dex_text_surf, dest=[int(self.char_detail_back.get_width() -
                                                                self.char_detail_back.get_width()/6.8),
                                                            int(self.char_detail_back.get_height() / 3 +
                                                            dex_hand_surf.get_height())])

            str_weight_surf = pg.transform.scale(pg.image.load(str_weight), (int(self.char_detail_back.get_width()/6),
                                                                             int(self.char_detail_back.get_height()/6)))
            self.char_detail_back.blit(str_weight_surf, dest=[int(self.char_detail_back.get_width() -
                                                                  self.char_detail_back.get_width()/6),
                                                              int(self.char_detail_back.get_height() / 3 +
                                                              dex_hand_surf.get_height()*1.25 +
                                                                  dex_text_surf.get_height())])

            str_text_durf = self.timer.myfont_2.render(str(self.selected_char.strength), False, (0, 0, 0))
            self.char_detail_back.blit(str_text_durf, dest=[int(self.char_detail_back.get_width() -
                                                                self.char_detail_back.get_width()/6.8),
                                                            int(self.char_detail_back.get_height() / 3 +
                                                                dex_hand_surf.get_height()*1.25 +
                                                                dex_text_surf.get_height() +
                                                                str_weight_surf.get_height())])

        r_metal = pg.image.load(Data.rusty_metal)
        self.inventory_gear_weapons_surf.blit(stretch_surf(self.inventory_gear_weapons_surf, r_metal), dest=(0, 0))
        self.inventory_items_surf.blit(stretch_surf(self.inventory_items_surf, r_metal), dest=(0, 0))

        if self.selected_char:
            for btn in self.gear_buttons:
                self.inventory_gear_weapons_surf.blit(btn.surf, btn.pos)

            for btn in self.weapon_buttons:
                self.inventory_gear_weapons_surf.blit(btn.surf, btn.pos)

            for btn in self.item_buttons:
                self.inventory_items_surf.blit(btn.surf, btn.pos)

        self.char_inventory_back.blit(fit_surf(back=self.char_inventory_back, surf=self.detail_back_metall),
                                      dest=[0, 0])
        self.char_inventory_back.blit(self.inventory_gear_weapons_surf, dest=[0, 0])
        self.char_inventory_back.blit(self.inventory_items_surf, dest=[0,
                                                                       self.inventory_gear_weapons_surf.get_height()])

        self.item_detail_back.blit(fit_surf(back=self.item_detail_back, surf=self.detail_back_metall), dest=[0, 0])
        self.item_detail_back.blit(self.item_stat_card, dest=blit_centered_pos(self.item_detail_back,
                                                                               self.item_stat_card))
        if self.item_stat_card_type == "Gear" and self.gear_bar:
            self.item_detail_back.blit(pg.transform.rotate(self.gear_bar.surf, 180), dest=(0, 0))

        # </editor-fold>

        # <editor-fold desc="Mid">

        # <editor-fold desc="map blitting">

        # draw visible chars
        self.game_map.selective_draw_map(team_num=self.own_team.team_num)

        # fit map content to map surface
        # self.map_content = fit_surf(surf=self.game_map.window, size=self.map_surface.get_size())
        self.game_map.window.blit(self.opp_turn_surf, dest=(0, 0))

        self.map_content = self.game_map.window

        # map cannot disappear from zooming out
        var = pg.transform.smoothscale(self.map_content,
                                       (max(1, int(self.map_surface.get_width() * self.zoom_factor)),
                                        max(1, int(self.map_surface.get_height() * self.zoom_factor))))

        # set destination
        if self.zoom_factor >= 1:
            self.dest = [self.amount[0] + self.con_shift_offset[0] + shift_offset[0],
                         self.amount[1] + self.con_shift_offset[1] + shift_offset[1]]
        else:  # just center map if zoomed out
            self.dest = blit_centered_pos(self.map_surface, var)

        # calc (visible) char on map buttons here
        v_chars = self.game_map.get_visible_chars_ind(self.own_team.team_num)
        for index in v_chars:

            if self.game_map.objects[index].render_type != "blit":
                continue

            char = self.game_map.objects[index]

            #           upper left     offset from upper left map corner
            position = [int(self.dest[0] + (char.get_pos(0) * self.current_element_size)),
                        int(self.dest[1] + (char.get_pos(1) * self.current_element_size))]

            real_position = [int(self.dest[0] + (char.get_pos(0) * self.current_element_size) +
                                 self.char_detail_back.get_width()),
                             int(self.dest[1] + (char.get_pos(1) * self.current_element_size))]

            btn = Button(dim=[int(self.current_element_size), int(self.current_element_size)],
                         pos=position, real_pos=real_position, img_source=self.map_char_imgs[char.class_id],
                         action=self.sel_char_binder("map_char_btn_" + str(char.idi), char))

            self.char_map_buttons.append(btn)

        # redraw background here
        self.map_surface.fill((0, 0, 17))

        # self.map_surface.convert()

        # TODO blit only area that is actually visible for better fps
        self.map_surface.blit(var, dest=[int(x) for x in self.dest])

        # blitting indicator for reachable fields
        if self.r_fields:
            r_surf = pg.Surface(self.game_map.window.get_size())  # same size as map surface before resizing
            r_surf.convert()
            r_surf.set_colorkey((144, 238, 144))
            r_surf.set_alpha(170)

            # blit green squares to it
            sq = pg.Surface((Data.def_elem_size, Data.def_elem_size))
            sq.fill((144, 238, 144))

            for field in self.r_fields:
                _pos = (field[0] * Data.def_elem_size, field[1] * Data.def_elem_size)
                r_surf.blit(sq, _pos)

            # now resize
            r_surf = fit_surf(surf=r_surf, size=self.map_surface.get_size())

            r_surf = pg.transform.smoothscale(r_surf,
                                              (max(1, int(self.map_surface.get_width() * self.zoom_factor)),
                                               max(1, int(self.map_surface.get_height() * self.zoom_factor))))
            # blit transparent surface with half transparent squares onto map
            self.map_surface.blit(r_surf, [int(x) for x in self.dest])

        # </editor-fold>

        # <editor-fold desc="blend out team stats">
        # blend out team stats if mouse is not up
        mouse_up = self.mouse_pos[1] < self.own_team_stats.get_height() - 15
        self.own_team_stats.blit(self.own_team_stats_back_img, dest=[0, 0])
        if mouse_up:
            for btn in self.own_team_stat_buttons:
                btn.activate()
                self.own_team_stats.blit(btn.surf, btn.pos)

            for bar in self.hp_bars:
                for b in bar:
                    self.own_team_stats.blit(b.surf, b.pos)
        else:
            for b in self.own_team_stat_buttons:
                b.deactivate()

        # beware of 0.05 as constant
        self.map_surface.blit(self.own_team_stats, dest=[int(0.05 * self.map_surface.get_width()), 0 if mouse_up else
                                                         -self.own_team_stats.get_height() + 15])
        # </editor-fold>

        # </editor-fold>

        # <editor-fold desc="right side">
        # ----- right -----

        self.minimap_surf.blit(fit_surf(back=self.minimap_surf, surf=self.map_content), dest=[0, 0])

        if not self.is_it_my_turn:
            self.done_btn.deactivate()
        else:
            self.done_btn.activate()
        self.done_btn_surf.blit(self.done_btn.surf, self.done_btn.pos)
        # </editor-fold>

        ###################

        # <editor-fold desc="all together">

        #####
        # mid

        self.screen.blit(self.map_surface, dest=[self.char_detail_back.get_width(), 0])

        #   own char is selected       map surface is focused
        if self.selected_own_char and self.map_surface.get_rect().collidepoint(
                self.mouse_pos[0] - self.char_detail_back.get_width(), self.mouse_pos[1]):
            self._draw_dotted_line(self.screen, line_points)

        if self.overlay and self.overlay_btn:
            self.overlay.newblit = False
            if self.dmg_done_timer < time.time() and self.dmg_done_ is not None:
                self.overlay = None
                self.overlay_btn = None
                self.dmg_done_ = None
            if self.dmg_done_ is not None:
                self.overlay.update_info(self.dmg_done_)

            if self.overlay and self.overlay_btn:
                for btn in self.overlay_btn:
                    if btn.is_focused([self.mouse_pos[0] - self.char_detail_back.get_width(), self.mouse_pos[1]]):
                        self.overlay.surf = self.overlay.type[btn.name]
                        self.overlay.part_to_attack = int(btn.name)
                        self.overlay.newblit = True
                    if not self.overlay.newblit:
                        self.overlay.surf = self.overlay.type["6"]
                if self.selected_own_char:
                    if self.selected_own_char.idi in self.shot_chars and self.dmg_done_timer < time.time():
                        self.overlay.update_info("You already shot!")

                    if self.dmg_done_ is None:
                        self.overlay.update_info(self.selected_own_char.get_chance(self.overlay.boi_to_attack,
                                                                                   self.overlay.part_to_attack))
                self.screen.blit(self.overlay.surf, dest=self.overlay.pos)
                self.screen.blit(self.overlay.info_tafel, dest=self.overlay.info_pos)

        #####
        # left

        self.screen.blit(self.char_detail_back, dest=[0, 0])
        self.screen.blit(self.char_inventory_back, dest=[0, self.char_detail_back.get_height()])
        self.screen.blit(self.item_detail_back, dest=[0, self.char_detail_back.get_height() +
                                                      self.char_inventory_back.get_height()])

        #####
        # right

        self.screen.blit(self.player_banners,
                         dest=[self.char_detail_back.get_width() + self.map_surface.get_width(), 0])

        if self.timer.amount >= 0 and self.is_it_my_turn:
            self.timer.update()
            self.screen.blit(self.timer.surf, dest=[self.char_detail_back.get_width() + self.map_surface.get_width() +
                                                    (self.player_banners.get_width() - self.timer.surf.get_width())//2,
                                                    (self.player_banners.get_height() -
                                                     (self.timer.surf.get_height()) + self.timer.surf.get_height()/8)])
        else:
            self.screen.blit(self.timer.myfont_2.render("Opponent's Turn", False, (0, 130, 0)),
                             dest=[self.char_detail_back.get_width() + self.map_surface.get_width() +
                                   self.timer.surf.get_width()//10, (self.player_banners.get_height() -
                                                                     (self.timer.surf.get_height()) +
                                                                     self.timer.surf.get_height()/2)])

        self.screen.blit(self.minimap_surf, dest=[self.char_detail_back.get_width() + self.map_surface.get_width(),
                                                  self.player_banners.get_height()])
        self.screen.blit(self.done_btn_surf, dest=[self.char_detail_back.get_width() + self.map_surface.get_width(),
                                                   self.player_banners.get_height() + self.minimap_surf.get_height()])

        # </editor-fold>

        # </editor-fold>

    def update(self):

        if self.opp_turn_applying:
            self.apply_opp_turn(self.opps_turn)

            if self.own_turn.win or self.opps_turn.win:
                return

        elif self.is_it_my_turn:

            self.main_blit()

        else:  # opps turn

            self.main_blit()

            # try to receive opps turn here
            opp_turn, t = self.client.get_turn()

            # if turn is NOT the new turn we're waiting for
            if (not opp_turn) or (self.opps_turn and (opp_turn.rand_id in self.opp_turn_list)):

                # todo this spams network traffic, too many requests for one turn
                if self.turn_wait_counter >= 300:  # check for turn every ... frames
                    self.client.get_turn_from_server()
                    self.turn_wait_counter = 0
                else:
                    self.turn_wait_counter += 1

            else:
                self.turn_wait_counter = 0
                # holds last new opp turn
                self.opps_turn = opp_turn
                self.opp_turn_list.append(self.opps_turn.rand_id)
                self.opp_turn_applying = True

    def event_handling(self):

        team_stat_button_focused = False
        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:

                if event.key == ord("q"):
                    pg.quit()
                    sys.exit()

            if event.type == pg.MOUSEBUTTONUP:
                p = list(pg.mouse.get_pos())
                self.mouse_pos = p

                if event.button == 3:  # right button release
                    if self.zoom_factor >= 1:
                        self.shifting = False
                        self.con_shift_offset = [self.con_shift_offset[0] + p[0] - self.shift_start[0],
                                                 self.con_shift_offset[1] + p[1] - self.shift_start[1]]

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()
                self.mouse_pos = p

                if event.button == 1:  # on left click

                    if self.overlay and self.overlay_btn:

                        for btn in self.overlay_btn:

                            # overlay button is clicked, we want to attack
                            if btn.is_focused([self.mouse_pos[0]-self.char_detail_back.get_width(), self.mouse_pos[1]])\
                                    and self.selected_own_char:

                                self.dmg_done_ = int(self.shoot(int(btn.name)))
                                self.dmg_done_timer = time.time() + 3

                    if self.overlay:
                        if not (self.overlay.pos[0] + 100 >= p[0] >= self.overlay.pos[0]) or\
                           not (self.overlay.pos[1] + 200 >= p[1] >= self.overlay.pos[1]):

                            self.overlay = None
                            #self.selected_own_char = None TODO maybe put back in

                    for button in self.gear_buttons:
                        if button.is_focused(p):
                            button.action()

                    for button in self.weapon_buttons:
                        if button.is_focused(p):
                            button.action(1)

                    for button in self.item_buttons:
                        if button.is_focused(p):
                            button.action(1)

                    if self.done_btn.is_focused(p):
                        self.done_btn.action()

                    if event.button == 1:
                        for button in self.own_team_stat_buttons:
                            if button.is_focused(p):
                                team_stat_button_focused = True
                                button.action()

                    # own char is selected and might want to move
                    if self.r_fields and self.selected_own_char and not team_stat_button_focused:
                        self.move_char = True

                    # if map surface is focused
                    if self.map_surface.get_rect().collidepoint(p[0] - self.char_detail_back.get_width(), p[1]):

                        for button in self.char_map_buttons:
                            if button.is_focused(p):
                                button.action()

                if event.button == 2:  # on mid click
                    pass

                if event.button == 3:  # on right click
                    if self.zoom_factor >= 1:
                        self.shift_start = p
                        self.shifting = True

                    for button in self.gear_buttons:
                        if button.is_focused(p):
                            button.action()

                    for button in self.weapon_buttons:
                        if button.is_focused(p):
                            button.action(3)

                    for button in self.item_buttons:
                        if button.is_focused(p):
                            button.action(3)

                if event.button == 4:  # scroll up

                    self.old_factor = self.zoom_factor
                    self.zoom_factor += 0.1
                    self.mouse_pos = p
                    self.zoomed = True

                if event.button == 5:  # scroll down

                    if self.zoom_factor - 0.1 >= 0.5:
                        self.old_factor = self.zoom_factor
                        self.zoom_factor -= 0.1

                    if self.zoom_factor <= 1:
                        self.shift_start = p
                        self.con_shift_offset = [0, 0]

                    self.zoomed = True

    # <editor-fold desc="Helper">
    def draw_line_pix_coords(self, surf, start, end, color):  # draws line from start to end on game_map.window
        start_point = start
        end_point = end

        # adjust to middle of field instead of upper left
        end_point = [int(ep + (Data.def_elem_size / 2)) for ep in end_point]

        line_points = [start_point]
        end_min_start = [end_point[i] - start_point[i] for i in range(start_point.__len__())]

        num_of_parts = 8
        for i in range(1, num_of_parts):
            offset = [int((i / num_of_parts) * x) for x in end_min_start]
            line_points.append([start_point[i] + offset[i] for i in range(len(start_point))])

        pl = line_points
        for p in range(0, len(pl), 2):
            pg.draw.aaline(surf, color, pl[p], pl[p + 1], 1)

        return surf

    def draw_line_(self, surf, start, end, color):
        start_point = self._map_to_pix_coord_def_size(start)
        end_point = self._map_to_pix_coord_def_size(end)

        pg.draw.aaline(surf, color, start_point, end_point)

        return surf

    def draw_line_map_coords(self, surf, start, end, color, num_of_parts=8):
        start_point = self._map_to_pix_coord(start)
        end_point = self._map_to_pix_coord(end)

        # adjust to middle of field instead of upper left
        end_point = [int(ep + (self.current_element_size / 2)) for ep in end_point]

        line_points = [start_point]
        end_min_start = [end_point[i] - start_point[i] for i in range(start_point.__len__())]

        for i in range(1, num_of_parts):
            offset = [int((i / num_of_parts) * x) for x in end_min_start]
            line_points.append([start_point[i] + offset[i] for i in range(len(start_point))])

        pl = line_points
        for p in range(0, len(pl), 2):
            pg.draw.aaline(surf, color, pl[p], pl[p + 1], 1)

        return surf

    @staticmethod
    def _draw_dotted_line(surf, pl, color=(255, 0, 0)):
        """
        :param surf: surf to draw on
        :param pl: point list for the line
        :param color: color
        :return: surface with line
        """
        if not len(pl) % 2 == 0:
            print("Error in Ingame_draw_dotted_line! Number of points must be even")
            return

        for p in range(0, len(pl), 2):
            pg.draw.aaline(surf, color, pl[p], pl[p + 1], 1)

        return surf

    def _map_to_pix_coord(self, pos):
        return [self.current_element_size * pos[0] + self.dest[0] +
                self.char_detail_back.get_width(),
                self.current_element_size * pos[1] + self.dest[1]] \
            if self.zoom_factor <= 1 else \
               [self.current_element_size * pos[0] + self.dest[0] +
                self.char_detail_back.get_width(),
                self.current_element_size * pos[1] + self.dest[1]]

    @staticmethod
    def _map_to_pix_coord_def_size(pos):
        return [def_elem_size * pos[0] + 25,
                def_elem_size * pos[1] + 25]
    # </editor-fold>

    def harakiri(self):
        del self

# <editor-fold desc="Helper functions">


def resize_surface_height(surf, y_diff=0):
    new = pg.Surface([surf.get_width(), surf.get_height() + y_diff])
    new.blit(surf, dest=[0, 0], area=(0, 0, new.get_width(), new.get_height()))
    return new


def stretch_surf(back=None, surf=None):
    if back is None or surf is None:
        return None
    return pg.transform.smoothscale(surf, back.get_size())


def fit_surf(back=None, surf=None, x_back=0, y_back=0, size=None):  # scales second surface to fit in first

    if back:
        background = pg.Surface(back.get_size())
    elif size:
        background = pg.Surface(size)
    else:
        if x_back > 0 and y_back > 0:
            background = pg.Surface([x_back, y_back])
        else:
            background = back
    surface = surf

    # case 1: back is bigger than surf
    if background.get_height() >= surface.get_height() and background.get_width() >= surface.get_width():
        w_diff = background.get_width() - surface.get_width()
        h_diff = background.get_height() - surface.get_height()
        w_lim = w_diff / surface.get_width()
        h_lim = h_diff / surface.get_height()

        if w_lim <= h_lim:
            # w is scaling limit
            target_size = [background.get_width(),
                           int((background.get_width() * surface.get_height()) / surface.get_width())]
        else:
            # h is scaling limit
            target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                           background.get_height()]

        return pg.transform.smoothscale(surf, target_size)

    # case 2: back is smaller than surf
    elif background.get_height() <= surface.get_height() and background.get_width() <= surface.get_width():
        if background.get_height() <= background.get_width():
            # wider than high, so height is smallest
            target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                           background.get_height()]
        else:
            # higher than wide
            target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                           background.get_height()]

        return pg.transform.smoothscale(surf, target_size)

    # case 3: back is wider than surf
    elif background.get_width() >= surface.get_width() and background.get_height() <= surface.get_height():
        target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                       background.get_height()]

        return pg.transform.smoothscale(surf, target_size)

    # case 4: back is higher than surf
    elif background.get_width() <= surface.get_width() and background.get_height() >= surface.get_height():
        target_size = [background.get_width(),
                       int((background.get_width() * surface.get_height()) / surface.get_width())]

        return pg.transform.smoothscale(surf, target_size)

    else:
        print("you missed an edge case boi")


def blit_centered_pos(back, surf):
    return [int((back.get_width() - surf.get_width()) / 2),
            int((back.get_height() - surf.get_height()) / 2)]


def threaded_timer(period):
    time.sleep(period)
# </editor-fold>
