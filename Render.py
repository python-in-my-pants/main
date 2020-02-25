"""
Gives general classes and functions for rendering on screen
"""

import Item
import Map
import pygame as pg
import os
from pickle import *
import numpy
from _thread import *
from NewClient import *
from GUI import *
from Team import *
from Data import *
from Characters import *
from TTimer import *
import time
import copy
import ctypes

ctypes.windll.user32.SetProcessDPIAware()

debug = False


class MainWindow:

    def __init__(self):  # creates main window with contents -> "mainscreen"

        size = [pg.display.Info().current_w, pg.display.Info().current_h]
        print("MainWindow thinks the size is: " + str(size))

        self.new_window_target = None
        self.screen = pg.display.set_mode(true_res, pg.RESIZABLE | pg.FULLSCREEN)

        main_background_img = pg.image.load("assets/rose.png")

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
            pg.mixer.music.load("assets/ass.mp3")  # TODO replace with omae wa mou and play on window open in loop
            #pg.mixer.music.play(0)
            # time.sleep(2.5)

            # go to different window and kill this one
            self.new_window_target = ConnectionSetup

        btn = Button([int(0.2 * size[0]), int(0.069 * size[1])], pos=[size[0] / 2 - int(0.2 * size[0]) / 2,
                                                                      size[1] / 2 - int(0.069 * size[1]) / 2 + 200],
                     img_uri="assets/blue_button_menu.jpg", text="Play", name="Button 1", action=button_fkt)

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


# TODO save last entered ip in file and fill ip field with it
class ConnectionSetup:

    def __init__(self):

        self.new_window_target = None
        self.role = "unknown"
        self.field_size = 0
        self.client = NetworkClient()

        self.join_stat = "Join Status"
        self.host_stat = "Host Status"
        self.host_thread = 0
        self.join_thread = 0
        #self.map = None
        self.map_points = None
        self.team_number = 0

        self.ip_focus = False
        self.size_focus = False

        self.first_click = True
        self.board_first_click = True

        self.get_hosting_list_counter = 170
        self.game_to_join = None

        self.screen = None
        self.buttons = None

        self.ip_field_text = "No games available"  # TODO change; this will be a button in a list of games to join marking the game as the game to join
        self.desi_board_text = "50"#"Enter board size"  # TODO change; here you should also enter the game name -> GameName, size, e.g. Dungeon, 50
        self.game_map_string = None

        self.main_background_img = pg.image.load("assets/rose.png").convert()
        self.main_background_img = fit_surf(pg.Surface(true_res), self.main_background_img)

        # create window
        self.screen = pg.display.set_mode(true_res, pg.RESIZABLE | pg.FULLSCREEN)

        self.screen.blit(self.main_background_img, blit_centered_pos(self.screen, self.main_background_img))

        self.update()

    def update(self):

        size = true_res

        # Asking for tha hosting list all 3 seconds assuming 60 FPS

        # this number has to be big enough to receive the list meanwhile
        if self.get_hosting_list_counter >= 180:  # TODO maybe lower this number to 1s?
            hosting_list = self.client.get_hosting_list()
            # print("host list:", hosting_list)

            print("-"*30 + "\nRec log len:", self.client.connection.get_rec_log_len())
            for elem in self.client.connection.get_rec_log()[-10:]:
                print("\n", elem.to_string())
            print()

            if hosting_list:
                # print("---> Full hosting list received! <---")
                # TODO this is hardcoded; always choosing game 1 from hosting list
                self.game_to_join = hosting_list["Dungeon"]
                self.ip_field_text = "{}, {} Points".format(self.game_to_join.name, self.game_to_join.points)

                ''' At a later point, the ip_to_join_button should be reworked as a list, containing 1 button per 
                game in the hosting list. If you click the button, the corresponding game should be game_to_join. 
                Clicking the join button should do the joining then'''
            else:
                self.game_to_join = None
                self.ip_field_text = "No games available"
            self.get_hosting_list_counter = 0
        else:
            self.get_hosting_list_counter += 1

        # set up GUI ---------------------------------------------------------------------------------------------------

        # we need 2 surfaces that are transparent

        left_surf = pg.Surface([int(size[0] / 2), size[1]])  # TODO: is it working?
        left_surf.fill((255, 12, 255))
        left_surf.set_colorkey((255, 12, 255))

        right_surf = pg.Surface([int(size[0] / 2), size[1]])
        right_surf.fill((255, 12, 255))
        right_surf.set_colorkey((255, 12, 255))

        surfs_size = [left_surf.get_width(), left_surf.get_height()]  # only 1 because they are equally big

        # define list of buttons

        self.buttons = []

        # button functions need to be defined before buttons

        def desired_board_size_button_fkt():

            self.size_focus = True
            self.ip_focus = False

            if self.board_first_click:
                self.desi_board_text = ""
                self.board_first_click = False

        def host_btn_fkt():
            if not self.host_thread:
                self.host_thread = start_new_thread(host_btn_fkt, ())
                return
            if self.host_thread and get_ident() == self.host_thread:

                # do not host while the size is not entered yet
                invalid_map_size = True
                while invalid_map_size:
                    self.host_stat = "Enter map size"
                    try:
                        self.field_size = int(self.desi_board_text)  # TODO split by ", " and get name too
                        invalid_map_size = False
                    except ValueError:
                        pass

                self.host_stat = "Generating map..."

                # generate Map for the game
                self.game_map_string = Map.MapBuilder().build_map(self.field_size)
                self.map_points = int(((self.game_map_string.size_x * self.game_map_string.size_y) / 500) * 16.6)

                self.host_stat = "Hosting..."

                # send the data to the server
                self.client.host_game("Dungeon", self.game_map_string.get_map(), self.map_points)

                self.host_stat = "Waiting for opp..."

                # while you are not in a game yet (aka nobody has joined your hosted game)
                while not self.client.get_join_stat():
                    # kill the thread if outer conditions changed
                    if self.host_thread == 0:
                        return

                self.role = "host"
                # host is always team 0
                self.team_number = 0
                # go to char select if somebody has joined your game
                self.host_stat = "Let's start!"
                self.new_window_target = CharacterSelection
                return

        def cancel_host_fkt():
            if self.host_thread:
                self.host_thread = 0
                self.host_stat = "Cancelling ..."
                self.client.cancel_hosting()
                self.host = "unknown"
                self.host_stat = "Hosting canceled!"

        def back_fkt():
            self.new_window_target = MainWindow

        # define buttons and put them on their surface

        desired_board_size_button = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                           pos=[int((left_surf.get_width() - int(surfs_size[0] / 3)) / 2),
                                                int(surfs_size[1] * 0.7)],
                                           real_pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2),
                                                     int(surfs_size[1] * 0.7)], color=(255, 255, 255),
                                           text=self.desi_board_text, name="board_size_button",
                                           action=desired_board_size_button_fkt)

        # append later to not mess up indices

        host_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                          pos=[int((left_surf.get_width() - int(surfs_size[0] / 3)) / 2),
                               int(surfs_size[1] / 6)], color=(135, 206, 235), text="Host", name="host_btn",
                          action=host_btn_fkt)

        self.buttons.append(host_btn)

        host_stat_btn = Button([int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                               pos=[int((left_surf.get_width() - int(surfs_size[0] / 3)) / 2),
                                    int(surfs_size[1] * 0.43)], color=(135, 206, 235), text=self.host_stat,
                               name="host_stat", action=(lambda: None))

        self.buttons.append(host_stat_btn)

        host_cancel_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                 pos=[int((left_surf.get_width() - int(surfs_size[0] / 3)) / 2),
                                      int(surfs_size[1] * 0.84)],
                                 real_pos=[int((left_surf.get_width() - int(surfs_size[0] / 3)) / 2),
                                           int(surfs_size[1] * 0.84)], color=(250, 128, 114), text="Cancel",
                                 name="cancel_host", action=cancel_host_fkt)

        self.buttons.append(host_cancel_btn)

        back_btn = Button(dim=[int(size[0] * 0.03), int(size[0] * 0.03)], pos=[0, 0], real_pos=[0, 0],
                          img_uri="assets/back_btn.png", text="", name="back_btn", use_dim=True, action=back_fkt)

        self.buttons.append(back_btn)

        # -------------------------------------------------------------------------------------------------------------

        def join_btn_fkt():
            if not self.join_thread:
                self.join_thread = start_new_thread(join_btn_fkt, ())
                return
            if self.join_thread and get_ident() == self.join_thread:  # TODO join self.game_to_join on click

                # no game was selected
                if not self.game_to_join:
                    self.join_stat = "Select a game first"
                    return

                # set the map to hosted map
                self.game_map_string = self.game_to_join.game_map
                self.map_points = self.game_to_join.points

                # TODO hardcoded game name for testing
                self.client.join("Dungeon")
                # wait until the server thinks that I am in a game
                while not self.client.get_join_stat():
                    pass

                self.role = "client"
                self.team_number = 1
                self.new_window_target = CharacterSelection

        def cancel_join_fkt():  # ToDo Rework for later KAPPA
            #self.net = None
            #self.role = "unknown"
            #self.join_thread = 0
            self.join_stat = "Cancelled"

        def ip_field_fkt():
            # on first click erase content, else do nothing
            self.size_focus = False
            self.ip_focus = True
            if self.first_click:
                self.ip_field_text = ""
                self.first_click = False

        join_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                          pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2),
                               int(surfs_size[1] / 6)],
                          real_pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2) +
                                    left_surf.get_width(),
                                    int(surfs_size[1] / 6)], color=(135, 206, 235), text="Join", name="join_btn",
                          action=join_btn_fkt)

        self.buttons.append(join_btn)

        join_stat_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                               pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2),
                                    int(surfs_size[1] * 0.43)],
                               real_pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2) +
                                         left_surf.get_width(), int(surfs_size[1] * 0.43)], color=(135, 206, 235),
                               text=self.join_stat, name="join_stat", action=(lambda: None))

        self.buttons.append(join_stat_btn)

        # ToDo Rename in Lobby list or create new one
        ip_to_join_btn = Button([int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2),
                                     int(surfs_size[1] * 0.7)],
                                real_pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2) +
                                          left_surf.get_width(), int(surfs_size[1] * 0.7)], color=(255, 255, 255),
                                text=self.ip_field_text, name="ip_to_join_btn", action=ip_field_fkt)

        self.buttons.append(ip_to_join_btn)
        self.buttons.append(desired_board_size_button)

        join_cancel_btn = Button(dim=[int(surfs_size[0] / 2), int(surfs_size[1] * 0.07)],
                                 pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2),
                                      int(surfs_size[1] * 0.84)],
                                 real_pos=[int((right_surf.get_width() - (surfs_size[0] / 3)) / 2) +
                                           left_surf.get_width(),
                                           int(surfs_size[1] * 0.84)], color=(250, 128, 114), text="Cancel",
                                 name="cancel_join", action=cancel_join_fkt)

        self.buttons.append(join_cancel_btn)

        # ----------------------------------------------------------------------------------------------------------

        left_surf.blit(host_btn.surf, host_btn.pos)
        left_surf.blit(desired_board_size_button.surf, desired_board_size_button.pos)
        left_surf.blit(host_stat_btn.surf, host_stat_btn.pos)
        left_surf.blit(host_cancel_btn.surf, host_cancel_btn.pos)
        left_surf.blit(back_btn.surf, back_btn.pos)

        right_surf.blit(join_btn.surf, join_btn.pos)
        right_surf.blit(join_stat_btn.surf, join_stat_btn.pos)
        right_surf.blit(join_cancel_btn.surf, join_cancel_btn.pos)
        right_surf.blit(ip_to_join_btn.surf, ip_to_join_btn.pos)

        # put right and left surface to screen

        self.screen.blit(left_surf, (0, 0))
        self.screen.blit(right_surf, (surfs_size[0], 0))

    def event_handling(self):

        ret = False

        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                if self.role == "host":
                    self.client.kill_connection()
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            if event.type == pg.KEYDOWN:
                ret = True
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

            if event.type == pg.MOUSEBUTTONDOWN:
                ret = True
                if pg.mouse.get_pressed()[0]:
                    for b in self.buttons:
                        if b.is_focused(pg.mouse.get_pos()):
                            b.action()

        return ret

    def harakiri(self):
        del self


class CharacterSelection:  # commit comment

    def __init__(self, points_to_spend, game_map, role="unknown", team_numberr=0, client=None):
        # let only those things be here that are not to be reset every frame, so i.e. independent of window size

        size = true_res

        self.points_to_spend = points_to_spend  # TODO
        self.game_map = game_map
        self.role = role
        self.client = client
        self.new_window_target = None
        self.spent_points = 0
        self.screen = pg.display.set_mode(true_res, pg.RESIZABLE | pg.FULLSCREEN)
        self.team_numberr = team_numberr
        self.ownTeam = Team(team_number=team_numberr)    # ToDo Network Team?
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
        self.ic_num = 7
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

        # -------------------------------------------------------------------------------------------------------------
        # I'm gonna do what's called a pro gamer move: load assets in init!
        # -------------------------------------------------------------------------------------------------------------

        self.cc_small_images = []
        for i in range(self.cc_num):
            # load small preview pics for buttons
            img = pg.image.load("assets/cc/small/cc_" + str(i) + ".png").convert()
            self.cc_small_images.append(img)

        self.gc_small_images = []
        for i in range(self.gc_num):
            # load small preview pics for buttons
            img = pg.image.load("assets/gc/small/gc_" + str(i) + ".png").convert()
            self.gc_small_images.append(img)

        self.wc_small_images = []
        for i in range(self.wc_num):
            img = pg.image.load("assets/wc/small/wc_" + str(i) + ".png").convert()
            self.wc_small_images.append(img)

        self.ic_small_images = []
        for i in range(self.ic_num):
            img = pg.image.load("assets/ic/small/ic_" + str(i) + ".png").convert()
            self.ic_small_images.append(img)

        # -------------------------------------------------------------------------------------------------------------
        # set up surfaces for screen
        # -------------------------------------------------------------------------------------------------------------

        #############
        # left side #
        #############

        # character cards go here as buttons
        self.troop_overview = pg.Surface([int(0.7 * size[0]), size[1] * 10])  # make very long for scroll stuff

        '''
        # NEWWW
        troop_overview_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                           self.troop_overview.get_size())
        self.troop_overview.blit(troop_overview_back_img, [0, 0])
        '''

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

        self.character_back = pg.Surface([self.troop_overview.get_width(),
                                          int(2 * self.gap_size +
                                              int(math.ceil(self.cc_num / self.line_len) * self.card_h) +
                                              int(self.cc_num / self.line_len) * self.gap_size +
                                              int(self.card_h * 0.5))])
        self.character_content = pg.Surface(
            [self.character_back.get_width(), self.character_back.get_height() - int(self.card_h / 2)])

        '''
        # NEWWW
        c_con_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                  self.character_content.get_size())
        self.character_content.blit(c_con_back_img, [0, 0])
        '''

        self.gear_back = pg.Surface([self.troop_overview.get_width(),
                                     int(2 * self.gap_size +
                                         int(math.ceil(self.gc_num / self.line_len)*self.card_h) +
                                         int(self.gc_num / self.line_len) * self.gap_size +
                                         int(self.card_h * 0.5))])
        self.gear_content = pg.Surface([self.gear_back.get_width(), self.gear_back.get_height() - int(self.card_h / 2)])

        '''
        # NEWWW
        g_con_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                  self.gear_content.get_size())
        self.gear_content.blit(g_con_back_img, [0, 0])
        '''

        self.weapon_back = pg.Surface([self.troop_overview.get_width(),
                                       int(2 * self.gap_size +
                                           int(math.ceil(self.wc_num / self.line_len) * self.card_h) +
                                           int(self.wc_num / self.line_len) * self.gap_size +
                                           int(self.card_h * 0.5))])
        self.weapon_content = pg.Surface(
            [self.weapon_back.get_width(), self.weapon_back.get_height() - int(self.card_h / 2)])

        '''
        # NEWWW
        w_con_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                  self.weapon_content.get_size())
        self.weapon_content.blit(w_con_back_img, [0, 0])
        '''

        self.item_back = pg.Surface([self.troop_overview.get_width(),
                                     int(2 * self.gap_size +
                                         int(math.ceil(self.ic_num / self.line_len)*self.card_h) +
                                         int(self.ic_num / self.line_len) * self.gap_size +
                                         int(self.card_h * 0.5))])
        self.item_content = pg.Surface([self.item_back.get_width(), self.item_back.get_height() - int(self.card_h / 2)])

        '''
        # NEWWW
        i_con_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                  self.item_content.get_size())
        self.item_content.blit(i_con_back_img, [0, 0])
        '''

        ##############
        # right side #
        ##############

        mini = max(int(0.3 * size[0]), int(0.2*size[1]))
        self.minimap_surf = pg.Surface([mini, mini])
        if debug:
            self.minimap_surf.fill((10, 11, 12))
        '''
        # NEWWW
        minimap_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                    self.minimap_surf.get_size())
        self.minimap_surf.blit(minimap_back_img, [0, 0])
        '''

        self.game_map.draw_map()
        self.map_surf = fit_surf(pg.Surface([self.minimap_surf.get_width(), int(self.minimap_surf.get_height()*0.8)]),
                                 self.game_map.window)

        # ---------------

        self.selected_units_back = pg.Surface([int(0.3 * size[0]), int((size[1] - self.minimap_surf.get_height())/2)])
        if debug:
            self.selected_units_back.fill((255, 0, 0))
        '''
        # NEWWW
        sel_uni_back_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                         self.selected_units_back.get_size())
        self.selected_units_back.blit(sel_uni_back_back_img, [0, 0])
        '''

        self.selected_units_box = pg.Surface(
                [self.selected_units_back.get_width() - 10, self.selected_units_back.get_height() - 10])

        # NEWWW
        sel_uni_box_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                        self.selected_units_box.get_size())
        self.selected_units_box.blit(sel_uni_box_back_img, [0, 0])

        # --------------

        self.selected_weapons_back = pg.Surface([int(0.3 * size[0]), int((size[1] - self.minimap_surf.get_height())/2)])
        if debug:
            self.selected_weapons_back.fill((0, 255, 0))
        '''
        # NEWWW
        sel_weap_back_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                          self.selected_weapons_back.get_size())
        self.selected_weapons_back.blit(sel_weap_back_back_img, [0, 0])
        '''

        self.selected_weapons_box = pg.Surface([self.selected_weapons_back.get_width() - 10,
                                                self.selected_weapons_back.get_height() - 10])

        # NEWWW
        sel_weap_box_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                         self.selected_weapons_box.get_size())
        self.selected_weapons_box.blit(sel_weap_box_back_img, [0, 0])

        # TODO: show items of selected char here

        # constants
        small_line_len = 3
        small_gap_size = int(self.selected_units_box.get_width() / (small_line_len * 9 + 1))
        w_small_card = int(self.selected_units_box.get_width() * 8 / (small_line_len * 9 + 1))
        h_small_card = w_small_card  # int(w_small_card * 1.457)

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
                                 font_color=(255, 255, 255), img_uri="assets/remaining_points.png",
                                 text=get_points(), use_dim=True,
                                 action=(lambda: None))

        # #############################################################################################################
        # banners
        # #############################################################################################################

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
                                       color=(50, 30, 230), text="Einheiten", action=char_ban_func)
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
                                            self.scroll_offset], color=(50, 80, 230), text="Rüstung",
                                  action=gear_ban_func)
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
                                              self.gear_back.get_height() + self.scroll_offset], color=(230, 50, 30),
                                    text="Waffen", action=weap_ban_func)
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
                                            self.scroll_offset], color=(30, 230, 50), text="Gegenstände",
                                  action=item_ban_func)
        self.banners.append(self.item_banner)

        # #############################################################################################################
        # character cards big
        # #############################################################################################################

        def character_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    char = create_character(card_num, self.net.team)    # ToDo Network
                    if self.spent_points + char.cost <= self.points_to_spend:
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

            h_pos = 2*self.gap_size + int(i / self.line_len)*self.card_h + (int(i/self.line_len)-1)*self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos],
                              real_pos=[w_pos,
                                        h_pos +
                                        self.rem_points_back.get_height() +
                                        self.character_banner.dim[1] +
                                        self.scroll_offset],
                              img_uri=("assets/cc/cc_" + str(i) + ".png"), use_dim=True, text="",
                              action=character_function_binder("cc_btn_function_" + str(i), i))

            self.character_cards.append(card_btn)

        # gear cards big
        def gear_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    btn_gear = make_gear_by_id(card_num)
                    if self.spent_points + btn_gear.cost <= self.points_to_spend and self.selectedChar:
                        self.selectedChar.gear.append(btn_gear)
                        self.spent_points += btn_gear.cost
                    else:
                        # TODO: take out
                        print("cannot buy")
                        self.timer_list.set_timer(0, 2.1)
                else:
                    self.timer_list.set_timer(1, 2.1)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.gc_num):
            w_pos = self.gap_size + ((i % self.line_len) * (self.card_w + self.gap_size))

            h_pos = 2*self.gap_size + int(i / self.line_len)*self.card_h + (int(i/self.line_len)-1)*self.gap_size

            card_btn = Button(dim=[self.card_w, self.card_h], pos=[w_pos, h_pos], real_pos=[w_pos,
                                                                                            h_pos +
                                                                                            self.rem_points_back.get_height() +
                                                                                            self.character_back.get_height() +
                                                                                            self.gear_banner.dim[1],
                                                                                            self.scroll_offset],
                              img_uri=("assets/gc/gc_" + str(i) + ".png"), use_dim=True, text="",
                              action=gear_function_binder("gc_btn_function_" + str(i), i))

            self.gear_cards.append(card_btn)

        # weapon cards big
        def weapon_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    weap = make_weapon_by_id(card_num)  # TODO: add function call to get instance of corresponding class
                    if self.spent_points + weap.cost <= self.points_to_spend and self.selectedChar:
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
                              img_uri=("assets/wc/wc_" + str(i) + ".png"), use_dim=True, text="",
                              action=weapon_function_binder("wc_btn_function_" + str(i), i))

            self.weapon_cards.append(card_btn)

        # item cards big
        def item_function_binder(name, card_num):

            def butn_fkt():

                if not self.ready:
                    item = make_item_by_id(card_num)  # TODO: add function call to get instance of corresponding class
                    if self.spent_points + item.cost <= self.points_to_spend and self.selectedChar:
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
                                                                                            self.gear_back.get_height()+
                                                                                            self.weapon_back.get_height() +
                                                                                            self.item_banner.dim[1] +
                                                                                            self.scroll_offset],
                              img_uri=("assets/ic/ic_" + str(i) + ".png"), use_dim=True, text="",
                              action=item_function_binder("ic_btn_function_" + str(i), i))

            self.item_cards.append(card_btn)

        #########
        # right #
        #########

        def ready_up():
            self.ready = not self.ready
            self.client.send_char_select_ready(self.ready, self.ownTeam)

        # old readychecker
        """
        def ready_checker():    # ToDo Network
            self.ready_thread = get_ident()
            while self.new_window_target != InGame:

                if self.role == "host":
                    self.net.send_control("Client_status")
                    if self.net.client_status == "Ready" and self.ready:

                        # TODO add own chars to map
                        for char in self.ownTeam.characters:
                            # first game objs should always be spawning areas
                            self.game_map.objects[self.net.team].place_character(char)
                            # assuming exactly 2 players
                            self.game_map.objects.append(char)
                            self.game_map.characters.append(self.game_map.objects.__len__() - 1)

                        self.net.send_data_pickle("Teeam", self.ownTeam.characters)

                        while not self.net.confirmation:
                            self.net.send_control("Fail?")
                            time.sleep(1)
                            if self.net.failsafe:
                                self.net.send_data_pickle("Teeam", self.ownTeam.characters)
                                self.net.failsafe = False
                        time.sleep(0.5)
                        self.net.confirmation = False

                        # get other team
                        while self.net.other_team.__len__ == 0:
                            self.net.send_control("Team_pls")
                            time.sleep(1)  # this must be at least 2!
                            pass  # I'm a Performanceartist!

                        while not isinstance(self.net.other_team, list):
                            try:
                                self.net.other_team = pickle.loads(self.net.other_team[6:])
                            except (pickle.UnpicklingError, EOFError):
                                self.net.send_control("Fail")
                                time.sleep(1)
                                self.net.send_control("Team_pls")
                                time.sleep(1)
                        self.net.send_control("Confirm")
                        print("LELELEL")
                        print(self.net.team)
                        print(self.net.o_team)
                        # wait for other team positions and put them in their spawn as well
                        for opp_char in self.net.other_team:
                            self.game_map.objects[self.net.o_team].place_character(opp_char)
                            self.game_map.objects.append(opp_char)
                            self.game_map.characters.append(self.game_map.objects.__len__() - 1)

                        if self.net.failsafe:
                            self.net.send_data_pickle("Teeam", self.ownTeam.characters)

                        self.new_window_target = InGame

                if self.role == "client":

                    self.net.send_control("Host_status")

                    print("!"*30)
                    print(self.net.host_status)
                    print(self.ready)

                    if self.net.host_status == "Ready" and self.ready:

                        print("branching")
                        # TODO add own chars to map
                        for char in self.ownTeam.characters:
                            # first game objs should always be spawning areas
                            self.game_map.objects[self.net.team].place_character(char)
                            # assuming exactly 2 players
                            self.game_map.objects.append(char)
                            self.game_map.characters.append(self.game_map.objects.__len__() - 1)

                        # get other team
                        print("GETTING TEAM")
                        while not isinstance(self.net.other_team, list):
                            try:
                                print(self.net.other_team)
                                print(len(self.net.other_team))

                                self.net.other_team = pickle.loads(self.net.other_team[6:])
                            except (pickle.UnpicklingError, EOFError):
                                self.net.send_control("Fail")
                                time.sleep(1)
                                self.net.send_control("Team_pls")
                                time.sleep(1)
                                print("LOL ERROR")
                        time.sleep(0.5)
                        self.net.send_control("Confirm")
                        time.sleep(0.5)
                        self.net.send_data_pickle("Teeam", self.ownTeam.characters)
                        print("Sending own Team")
                        while not self.net.confirmation:
                            self.net.send_control("Fail?")
                            time.sleep(1)
                            if self.net.failsafe:
                                self.net.send_data_pickle("Teeam", self.ownTeam.characters)
                                self.net.failsafe = False
                        time.sleep(0.5)
                        self.net.confirmation = False

                        # wait for other team positions and put them in their spawn as well
                        for opp_char in self.net.other_team:
                            self.game_map.objects[self.net.o_team].place_character(opp_char)
                            self.game_map.objects.append(opp_char)
                            self.game_map.characters.append(self.game_map.objects.__len__() - 1)

                        if self.net.failsafe:
                            self.net.send_data_pickle("Teeam", self.ownTeam.characters)
                        self.new_window_target = InGame
        """
        def get_text():
            return "Unready" if self.ready else "Ready!"

        self.ready_btn = Button(
            dim=[int(self.minimap_surf.get_size()[0] * 0.9), int(self.minimap_surf.get_size()[1] * 0.2)],
            pos=[int(self.minimap_surf.get_size()[0] * 0.05), int(self.minimap_surf.get_size()[1]*0.8)],
            real_pos=[int(self.minimap_surf.get_size()[0] * 0.05) +
                      self.troop_overview.get_size()[0],
                      int(self.minimap_surf.get_size()[1]*0.8)], img_uri="assets/blue_button_menu.jpg",
            text=get_text(), action=ready_up)

        # rest has to be handled in update

        self.update()

    def cc_function_binder(self, name, unique_char_id):

        def btn_fkt(button):

            if button == 1:
                # show characters items in selected_weapons_box and set him as selected char
                self.selectedChar = self.ownTeam.get_char_by_unique_id(unique_char_id)
            if button == 3:
                # sell this character
                char = self.ownTeam.get_char_by_unique_id(unique_char_id)
                del self.team_char_btns[self.ownTeam.get_index_by_obj(char)]  # TODO if I reset team_char_btns ...
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

                #self.points_to_spend += char.cost

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

    def update(self):  # TODO for better performance render only things that changed
                        # TODO adjust size of small teamcharbtn dpendent on map oints
        if self.ready:
            if self.ready_checker_counter == 69:  # CHECKER EVERY Secondu
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
        char_small_line_len = 5 if self.ownTeam.characters.__len__() <= 10 else int(self.ownTeam.characters.__len__()/2+0.5)
        char_small_gap_size = int(self.selected_units_box.get_width() / (char_small_line_len * 9 + 1))
        char_w_small_card = int(self.selected_units_box.get_width() * 8 / (char_small_line_len * 9 + 1))
        char_h_small_card = char_w_small_card  # int(w_small_card * 1.457)

        self.team_char_btns = []
        for i in range(self.ownTeam.characters.__len__()):
            pos_w = char_small_gap_size + ((i % char_small_line_len) * (char_w_small_card + char_small_gap_size))
            pos_h = 2 * char_small_gap_size + int(i / char_small_line_len) * char_h_small_card + (
                        int(i / char_small_line_len) - 1) * char_small_gap_size

            class_num = self.ownTeam.characters[i].class_id

            btn = Button(dim=[char_w_small_card, char_h_small_card], pos=[pos_w, pos_h], real_pos=
                            [pos_w + int((self.selected_units_back.get_width() - self.selected_units_box.get_width())/2)+
                            self.troop_overview.get_width(),
                             pos_h + int((self.selected_units_back.get_height()-self.selected_units_box.get_height())/2)+
                             self.minimap_surf.get_height()],
                         img_uri=("assets/cc/small/cc_" + str(class_num) + ".png"), use_dim=True, text="",
                         action=self.cc_function_binder("assets/cc/cc_small_btn_func" + str(i),
                                                        self.ownTeam.characters[i].idi))

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
                              int((self.selected_weapons_back.get_width()-self.selected_weapons_box.get_width())/2),
                              pos_h +
                              self.minimap_surf.get_height() +
                              self.selected_units_back.get_height() +
                              int((self.selected_weapons_back.get_height()-self.selected_weapons_box.get_height())/2)],
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

        # TODO fill here with background image
        '''
        # NEWWW
        troop_overview_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
                                                           self.troop_overview.get_size())
        self.troop_overview.blit(troop_overview_back_img, [0, 0])
        '''
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

        self.minimap_surf.blit(self.map_surf, dest=[int((self.minimap_surf.get_width() - self.map_surf.get_width())/2),
                                                    int((int(self.minimap_surf.get_height()*0.8) -
                                                         self.map_surf.get_height()) / 2)])
        self.ready_btn.set_text("Ready!" if not self.ready else "Unready")
        self.ready_btn.update_text()

        self.minimap_surf.blit(self.ready_btn.surf, self.ready_btn.pos)

        self.player_overview.blit(self.minimap_surf, dest=[0, 0])

        # selected units
        # if not self.team_char_btns:  # was sel item btns

        # self.selected_units_box.fill((0, 0, 0))
        # NEWWW
        sel_uni_box_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
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
        sel_weap_box_back_img = pg.transform.smoothscale(pg.image.load("assets/metall.png").convert(),
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
                                                          self.rem_points_back.get_width())/2), 0])

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
                                                                   true_res[1] + self.rem_points_back.get_height(), 0)))

    def harakiri(self):
        del self


class InGame:

    def __init__(self, own_team, game_map, client=None):   # ToDo Turnsystem/Network not implemented yet

        # things to do here:
        # - put chars on spawning area

        self.own_team = own_team
        self.game_map = game_map
        self.client = client

        self.cc_num = 6
        self.gc_num = 4
        self.wc_num = 7
        self.ic_num = 7

        w = true_res[0]
        h = true_res[1]

        self.new_window_target = None
        self.char_prev_selected = False  # holds whether own team character is already selected

        self.element_size = int(true_res[0] * 9 / (16 * 30))  # default is 30 elem width
        self.zoom_factor = 1
        self.mouse_pos = pg.mouse.get_pos()
        self.zoomed = False
        self.amount = [0, 0]
        self.old_factor = 1

        self.shifting = False
        self.shift_start = [0, 0]
        self.con_shift_offset = [0, 0]

        self.screen = pg.display.set_mode(true_res, pg.RESIZABLE | pg.FULLSCREEN)

        # holds selected char of own team
        self.selected_own_char = self.own_team.characters[0]
        self.selected_item = None if not self.selected_own_char.items else self.selected_own_char.items[0]
        self.selected_weapon = None if not self.selected_own_char.weapons else self.selected_own_char.weapons[0]

        # holds selected char (maybe from opponent team)
        self.selected_char = self.selected_own_char

        # -------------------
        # render image lists
        # -------------------

        self.detail_size = [int((7/32) * w - 20), int((4/10) * h - 20)]
        self.small_size = [int((5 / 32) * 7 * w / 32), int((5 / 32) * 7 * w / 32)]

        self.detail_char = []
        self.small_char = []
        for i in range(self.cc_num):
            img = pg.transform.smoothscale(pg.image.load("assets/cc/detail/cc_" + str(i) + ".png").convert(),
                                           self.detail_size)
            self.detail_char.append(img)
            img = pg.transform.smoothscale(pg.image.load("assets/cc/small/cc_" + str(i) + ".png").convert(),
                                           self.small_size)
            self.small_char.append(img)

        self.detail_gear = []
        self.small_gear = []
        for i in range(self.gc_num):
            img = pg.transform.smoothscale(pg.image.load("assets/gc/detail/gc_" + str(i) + ".png").convert(),
                                           self.detail_size)
            self.detail_gear.append(img)
            img = pg.transform.smoothscale(pg.image.load("assets/gc/small/gc_" + str(i) + ".png").convert(),
                                           self.small_size)
            self.small_gear.append(img)

        self.detail_weapon = []
        self.small_weapon = []
        for i in range(self.wc_num):
            img = pg.transform.smoothscale(pg.image.load("assets/wc/detail/wc_" + str(i) + ".png").convert(),
                                           self.detail_size)
            self.detail_weapon.append(img)
            img = pg.transform.smoothscale(pg.image.load("assets/wc/small/wc_" + str(i) + ".png").convert(),
                                           self.small_size)
            self.small_weapon.append(img)

        self.detail_item = []
        self.small_item = []
        for i in range(self.ic_num):
            img = pg.transform.smoothscale(pg.image.load("assets/ic/detail/ic_" + str(i) + ".png").convert(),
                                           self.detail_size)
            self.detail_item.append(img)
            img = pg.transform.smoothscale(pg.image.load("assets/ic/small/ic_" + str(i) + ".png").convert(),
                                           self.small_size)
            self.small_item.append(img)

        self.map_char_imgs = []
        for i in range(self.cc_num):
            img = pg.image.load("assets/cc/small/cc_" + str(i) + ".png").convert_alpha()  # TODO change to actual right images
            self.map_char_imgs.append(img)

        self.detail_back_metall = pg.image.load("assets/metall.png").convert()

        # -------------------------------------------------------------------------------------------------------------
        # set up surfaces
        # -------------------------------------------------------------------------------------------------------------

        # -------------- left -------------------------------

        # surface 1.0 and 1.1
        self.char_detail_back = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        #self.char_detail_back.fill((98, 70, 230))
        self.char_stat_card = self.detail_char[0]  # TODO

        # surface 2 and subsurfaces
        self.char_inventory_back = pg.Surface([int(7 * w / 32), int(4 * h / 18)])
        self.inventory_gear_weapons_surf = pg.Surface([int(7 * w / 32), int(0.34 * 4 * h / 18)])  # 2 first are gear, last 3 are weapons
        self.inventory_items_surf = pg.Surface([int(7 * w / 32), int(0.66 * 4 * h / 18)])  # 2 rows high

        # TODO make so that actual stats are shown in character card instead of just standard stats
        self.item_detail_back = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        #self.item_detail_back.fill((77, 98, 219))
        #self.item_detail_back.fill((255, 0, 0))
        self.item_stat_card = self.detail_item[0]   # TODO

        # -------------- mid ----------------------------------

        own_team_height = 2 * int((1 / 32) * 7 * w / 32) + \
                          int((self.own_team.characters.__len__() / 10) + 1) *\
                          ((int((1 / 32) * 7 * w / 32) +  # number of lines * gap size
                           int(1.6 * (5 / 32) * 7 * w / 32)))  # button + hp bar

        self.map_surface = pg.Surface([int(9 * w / 16), h])
        # TODO place characters on map first
        self.game_map.selective_draw_map(team_num=self.net.team)# own_team.team_num)    # ToDo Network
        self.map_content = fit_surf(surf=self.game_map.window, size=self.map_surface.get_size())

        self.own_team_stats = pg.Surface([int(self.map_surface.get_width() * 0.9), own_team_height])

        # try on blitting alpha
        self.own_team_stats.fill((255, 0, 0))
        self.own_team_stats.set_colorkey((255, 0, 0))

        self.own_team_stats_back_img = pg.transform.smoothscale(pg.image.load("assets/team_char_back.png").convert_alpha(),
                                                                self.own_team_stats.get_size())  # TODO size from own team stats

        # -------------- right ----------------------------------

        self.player_banners = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        self.match_stats = pg.Surface([self.player_banners.get_width(), int(self.player_banners.get_height() * 0.2)])

        # TODO set content of minimap by blitting scaled map to it
        self.minimap_surf = pg.Surface([int(7 * w / 32), int(7 * h / 18)])
        self.done_btn_surf = pg.Surface([int(7 * w / 32), int(4 * h / 18)])

        # -------------------------------------------------------------------------------------------------------------

        # TODO check if this makes sense, coded when sick
        self.zoom_size = [int(((9 * w / 16) / (self.mouse_pos[0] - self.char_detail_back.get_width())) *
                              # TODO maybe not map surface but content
                              ((1.4142 / 2) * np.abs((self.zoom_factor - 1) * self.map_surface.get_width()))),
                          int((h / self.mouse_pos[1]) *
                              ((1.4142 / 2) * np.abs((self.zoom_factor - 1) * self.map_surface.get_height())))]

        # set up buttons
        # TODO characters on map must have buttons to select them as sel char
        # -------------------------------------------------------------------------------------------------------------

        # button functions

        def sel_own_char_binder(name, _id):

            def func():
                self.selected_own_char = self.own_team.get_char_by_unique_id(_id)

            func.__name__ = name
            return func

        def done_button_action():  # TODO

            pass

        # -------------------------------------------------------------------------------------------------------------
        # buttons and bars

        self.gear_buttons = []  # TODO buttons
        self.weapon_buttons = []
        self.item_buttons = []

        self.own_team_stat_buttons = []
        self.hp_bars = []

        self.char_map_buttons = []

        # constants, passt
        self.btn_w = int((5 / 32) * 7 * w / 32)
        self.btn_h = self.btn_w
        # self.inventory_gap_size = int((1 / 32) * 7 * w / 32)
        self.inventory_gap_size = int((self.inventory_gear_weapons_surf.get_height()-self.btn_h)/2)
        self.inventory_line_len = 5

        # ----- left -----

        # inventory buttons moved to update

        # ----- mid -----

        # hp bars, blit to own team stats
        # TODO update hp bars each tick
        for i in range(self.own_team.characters.__len__()):

            pos_w = self.btn_w + (i % 10) * (self.btn_w + self.inventory_gap_size)
            # pos_h = self.inventory_gap_size + \
            pos_h = int((1 / 32) * 7 * w / 32) + self.btn_h + int(i / 10) * \
                    (self.btn_h + int((1 / 32) * 7 * w / 32) + self.btn_h * 0.8)

            bars = []

            for j in range(6):
                hp_bar = HPBar(dim=[self.btn_w, int(0.1 * self.btn_h)],
                               pos=[pos_w, int(pos_h + j * 0.108 * self.btn_h)],  # TODO maybe better number?
                               curr=self.own_team.characters[i].health[j],
                               end=100)
                bars.append(hp_bar)

            self.hp_bars.append(bars)

        # team buttons in overview
        for i in range(self.own_team.characters.__len__()):
            pos_w = self.btn_w + (i % 10) * (self.btn_w + self.inventory_gap_size)
            pos_h = self.inventory_gap_size + int(i / 10) * (self.btn_h + self.inventory_gap_size + self.btn_h * 0.6)

            btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h], real_pos=[pos_w +
                                                                                     self.char_detail_back.get_width() +
                                                                                     int(self.map_surface.get_width() * 0.05),
                                                                                     pos_h],
                         img_uri=("assets/cc/small/cc_" + str(self.own_team.characters[i].class_id) + ".png"),
                         text="", name="char btn " + str(self.own_team.characters[i].class_id),
                         action=sel_own_char_binder("chat_btn_" + str(self.own_team.characters[i].idi),
                                                    self.own_team.characters[i].idi))

            self.own_team_stat_buttons.append(btn)

        # chars on map
        for index in self.game_map.characters:
            char = self.game_map.objects[index]  # TODO change real pos (scroll and zoom and so on)

            btn = Button(dim=[self.element_size * self.zoom_factor, self.element_size * self.zoom_factor],
                         pos=[char.get_pos(0) * self.element_size + self.zoom_size[0],
                              char.get_pos(1) * self.element_size + self.zoom_size[1]],
                         real_pos=[char.get_pos(0) * self.element_size +
                                   self.char_detail_back.get_width() +
                                   self.zoom_size[0],
                                   char.get_pos(1) * self.element_size +
                                   self.zoom_size[1]],
                                    # TODO img_uri="assets/char/" + str(char.unit_class) + ".png",
                                    img_source=self.map_char_imgs[char.class_id],
                         action=self.sel_char_binder("map_char_btn_" + str(char.idi), char.idi))

            self.char_map_buttons.append(btn)

        # ----- right -----

        # done button
        self.done_btn = Button(dim=[int(7 * w / 32), int(4 * h / 18)], pos=[0, 0],
                               real_pos=[self.char_detail_back.get_width() +
                                         self.map_surface.get_width(),
                                         self.player_banners.get_height() +
                                         self.minimap_surf.get_height()],
                               img_uri="assets/blue_button_menu.jpg",
                               name="Done Button", action=done_button_action)

    def sel_char_binder(self, name, char):

        def func():

            print("char button clicked")
            if char.team == self.net.team:  # own char
                self.selected_own_char = char
            if char.team == self.net.other_team and self.selected_own_char:  # opp. char
                # attack routine
                self.selected_own_char.shoot(char, 3)

        func.__name__ = name
        return func

    def inventory_function_binder(self, name, _id, item_type):

        def func():

            if item_type == "weapon":
                for i, weap in enumerate(self.selected_own_char.weapons):
                    if weap.class_idi == _id:
                        self.selected_own_char.change_active_slot(["Weapon", i])
                        return

            if item_type == "item":
                for i, item in enumerate(self.selected_own_char.items):
                    if item.idi == _id:
                        self.selected_own_char.change_active_slot(["Item", i])
                        return

        func.__name__ = name
        return func

    def update(self):

        w = true_res[0]
        h = true_res[1]

        if self.shifting:
            shift_offset = [pg.mouse.get_pos()[0] - self.shift_start[0],
                            pg.mouse.get_pos()[1] - self.shift_start[1]]
        else:
            shift_offset = [0, 0]

        # chars on map

        v_chars = self.game_map.get_visible_chars_ind(self.net.team)

        for index in v_chars:

            if self.game_map.objects[index].render_type is not "blit":
                continue

            char = self.game_map.objects[index]  # TODO change real pos (scroll and zoom and so on)

            p = [char.get_pos(0) * self.element_size + self.zoom_size[0],
                 char.get_pos(1) * self.element_size + self.zoom_size[1]]

            rp = [char.get_pos(0) * self.element_size +
                                    self.char_detail_back.get_width() +
                                    self.zoom_size[0],
                  char.get_pos(1) * self.element_size +
                                    self.zoom_size[1]]

            btn = Button(dim=[self.element_size * self.zoom_factor, self.element_size * self.zoom_factor],
                         pos=[char.get_pos(0) * self.element_size + self.zoom_size[0],
                              char.get_pos(1) * self.element_size + self.zoom_size[1]],
                         real_pos=[char.get_pos(0) * self.element_size +
                                   self.char_detail_back.get_width() +
                                   self.zoom_size[0],
                                   char.get_pos(1) * self.element_size +
                                   self.zoom_size[1]],
                         img_source=self.map_char_imgs[char.class_id],
                         action=self.sel_char_binder("map_char_btn_" + str(char.idi), char))

            self.char_map_buttons.append(btn)

        # inventory buttons

        if self.selected_own_char:

            self.gear_buttons = []
            if self.selected_own_char.gear:
                # gear buttons
                for i in range(self.selected_own_char.gear.__len__()):
                    pos_w = (i + 1) * self.inventory_gap_size + i * self.btn_w
                    pos_h = self.inventory_gap_size

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w,
                                           pos_h +
                                           self.char_detail_back.get_height()],
                                 #img_uri="assets/gc/small/gc_" + str(self.selected_own_char.gear[i].my_id) + ".png",
                                 img_source=self.small_gear[i],
                                 text="", name=("gear " + str(self.selected_own_char.gear[i].my_id) + " button"),
                                 action=(lambda: None))

                    self.gear_buttons.append(btn)

            self.weapon_buttons = []
            if self.selected_own_char.weapons:
                # weapon buttons
                for i in range(self.selected_own_char.weapons.__len__()):
                    pos_w = 2 * self.btn_w + 4 * self.inventory_gap_size + i * (self.inventory_gap_size + self.btn_w)
                    pos_h = self.inventory_gap_size

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w,
                                           pos_h +
                                           self.char_detail_back.get_height()],
                                 img_source=self.small_weapon[i],
                                 text="", name=("weapon " + str(self.selected_own_char.weapons[i].class_id) + ".png"),
                                 action=self.inventory_function_binder("weapon " + str(self.selected_own_char.weapons[i].class_idi),
                                                                       self.selected_own_char.weapons[i].class_idi, item_type="weapon"))

                    self.weapon_buttons.append(btn)

            self.item_buttons = []
            if self.selected_own_char.items:
                # item buttons
                for i in range(self.selected_own_char.items.__len__()):
                    pos_w = self.inventory_gap_size + (i % 5) * (self.btn_w + self.inventory_gap_size)
                    pos_h = self.inventory_gap_size + int(i/5) * (self.btn_h + self.inventory_gap_size)

                    btn = Button(dim=[self.btn_w, self.btn_h], pos=[pos_w, pos_h],
                                 real_pos=[pos_w,
                                           pos_h +
                                           self.char_detail_back.get_height() +
                                           self.inventory_gear_weapons_surf.get_height()],
                                 #="assets/ic/small/ic_" + str(self.selected_own_char.items[i].my_id) + ".png",
                                 img_source=self.small_item[i],
                                 text="",
                                 name=("item " + str(self.selected_own_char.items[i].my_id) + ".png"),
                                 action=self.inventory_function_binder("item " + str(self.selected_own_char.items[i].idi),
                                                                  self.selected_own_char.items[i].idi, item_type="item"))

                    self.item_buttons.append(btn)

        ##############################################################################################################
        # blit everything to positions
        ##############################################################################################################

        # ----- left -----

        self.char_detail_back.blit(fit_surf(back=self.char_detail_back, surf=self.detail_back_metall), dest=[0, 0])
        self.char_detail_back.blit(self.char_stat_card, dest=blit_centered_pos(self.char_detail_back,
                                                                               self.char_stat_card))

        # TODO blit back again here
        self.inventory_items_surf.fill((255, 0, 0))
        self.inventory_gear_weapons_surf.fill((0, 34, 98))

        for btn in self.gear_buttons:
            self.inventory_gear_weapons_surf.blit(btn.surf, btn.pos)

        for btn in self.weapon_buttons:
            self.inventory_gear_weapons_surf.blit(btn.surf, btn.pos)

        for btn in self.item_buttons:
            self.inventory_items_surf.blit(btn.surf, btn.pos)

        self.char_inventory_back.blit(fit_surf(back=self.char_inventory_back, surf=self.detail_back_metall), dest=[0, 0])
        self.char_inventory_back.blit(self.inventory_gear_weapons_surf, dest=[0, 0])
        self.char_inventory_back.blit(self.inventory_items_surf, dest=[0,
                                                                       self.inventory_gear_weapons_surf.get_height()])

        self.item_detail_back.blit(fit_surf(back=self.item_detail_back, surf=self.detail_back_metall), dest=[0, 0])
        self.item_detail_back.blit(self.item_stat_card, dest=blit_centered_pos(self.item_detail_back,
                                                                               self.item_stat_card))

        # ----- mid -----

        self.own_team_stats.blit(self.own_team_stats_back_img, dest=[0, 0])

        for btn in self.own_team_stat_buttons:
            self.own_team_stats.blit(btn.surf, btn.pos)

        for bar in self.hp_bars:
            for b in bar:
                self.own_team_stats.blit(b.surf, b.pos)

        if self.zoomed:

            real_mouse_pos = [(self.mouse_pos[0] - (7 / 32) * w), self.mouse_pos[1]]

            self.amount = [int(real_mouse_pos[0] - (self.zoom_factor * real_mouse_pos[0])),
                           int(real_mouse_pos[1] - (self.zoom_factor * real_mouse_pos[1]))]

            self.zoomed = False

        self.game_map.selective_draw_map(team_num=self.own_team.team_num)
        self.map_content = fit_surf(surf=self.game_map.window, size=self.map_surface.get_size())

        if self.zoom_factor >= 1:
            dest = [self.amount[0] + self.con_shift_offset[0] + shift_offset[0],
                    self.amount[1] + self.con_shift_offset[1] + shift_offset[1]]

        else:
            dest = blit_centered_pos(self.map_surface, pg.transform.smoothscale(self.map_content,
                                                      (max(0, int(self.map_content.get_width() * self.zoom_factor)),
                                                       max(0, int(self.map_content.get_height() * self.zoom_factor)))))

        self.map_surface.fill((0, 0, 10))

        var = pg.transform.smoothscale(self.map_content,
                                       (max(0, int(self.map_surface.get_width() * self.zoom_factor)),
                                        max(0, int(self.map_surface.get_height() * self.zoom_factor))))

        self.map_surface.blit(var, dest=dest)  # TODO blit only area that is actually visible for better fps

        # TODO beware of 0.05 as constant
        self.map_surface.blit(self.own_team_stats, dest=[int(0.05 * self.map_surface.get_width()), 0])

        # ----- right -----

        self.player_banners.blit(self.match_stats, dest=[0, int(0.8 * self.player_banners.get_height())])

        self.minimap_surf.blit(fit_surf(back=self.minimap_surf, surf=self.map_content), dest=[0, 0])

        self.done_btn_surf.blit(self.done_btn.surf, self.done_btn.pos)

        # ----- all together -----

        self.screen.blit(self.char_detail_back, dest=[0, 0])
        self.screen.blit(self.char_inventory_back, dest=[0, self.char_detail_back.get_height()])
        self.screen.blit(self.item_detail_back, dest=[0, self.char_detail_back.get_height() +
                                                      self.char_inventory_back.get_height()])

        self.screen.blit(self.map_surface, dest=[self.char_detail_back.get_height(), 0])

        self.screen.blit(self.player_banners, dest=[self.char_detail_back.get_width() + self.map_surface.get_width(), 0])
        self.screen.blit(self.minimap_surf, dest=[self.char_detail_back.get_width() + self.map_surface.get_width(),
                                                  self.player_banners.get_height()])
        self.screen.blit(self.done_btn_surf, dest=[self.char_detail_back.get_width() + self.map_surface.get_width(),
                                                   self.player_banners.get_height() + self.minimap_surf.get_height()])

    def event_handling(self):

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

            if event.type == pg.KEYDOWN:

                if event.key == ord("q"):
                    pg.quit()
                    sys.exit()

            if event.type == pg.MOUSEBUTTONUP:
                p = list(pg.mouse.get_pos())

                if event.button == 2:  # scroll wheel release
                    self.shifting = False
                    self.con_shift_offset = [self.con_shift_offset[0] + p[0] - self.shift_start[0],
                                             self.con_shift_offset[1] + p[1] - self.shift_start[1]]

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()

                if event.button == 1:  # on left click

                    for button in self.gear_buttons:
                        if button.is_focused(p):
                            button.action()

                    for button in self.weapon_buttons:
                        if button.is_focused(p):
                            button.action()

                    for button in self.item_buttons:
                        if button.is_focused(p):
                            button.action()

                    for button in self.own_team_stat_buttons:
                        if button.is_focused(p):
                            button.action()

                    if self.done_btn.is_focused(p):
                        self.done_btn.action()

                    if self.map_surface.get_rect().collidepoint(p[0], p[1]):
                        for button in self.char_map_buttons:
                            if button.is_focused(p):
                                button.action()

                if event.button == 2:  # on mid click
                    self.shift_start = p
                    self.shifting = True

                if event.button == 3:  # on right click
                    pass

                if event.button == 4:  # scroll up

                    self.old_factor = self.zoom_factor
                    self.zoom_factor += 0.1
                    self.mouse_pos = p
                    self.zoomed = True

                if event.button == 5:  # scroll down

                    self.old_factor = self.zoom_factor
                    self.zoom_factor -= 0.1

                    if self.zoom_factor <= 1:
                        self.shift_start = p
                        self.con_shift_offset = [0, 0]

                    self.zoomed = True

    def harakiri(self):
        del self


def resize_surface_height(surf, y_diff=0):

    new = pg.Surface([surf.get_width(), surf.get_height() + y_diff])
    new.blit(surf, dest=[0, 0], area=(0, 0, new.get_width(), new.get_height()))
    return new


def fit_surf(back=None, surf=None, x_back=0, y_back=0, size=None):  # scales second surface to fit in first

    if size:
        background = pg.Surface(size)
    else:
        if x_back > 0 and y_back > 0:
            background = pg.Surface([x_back, y_back])
        else:
            background = back
    surface = surf

    # case 1: back is bigger than surf
    if background.get_height() >= surface.get_height() and background.get_width() >= surface.get_width():
        w_diff = background.get_width()-surface.get_width()
        h_diff = background.get_height()-surface.get_height()
        w_lim = w_diff/surface.get_width()
        h_lim = h_diff/surface.get_height()

        if w_lim <= h_lim:
            # w is scaling limit
            target_size = [background.get_width(),
                           int((background.get_width()*surface.get_height())/surface.get_width())]
        else:
            # h is scaling limit
            target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                           background.get_height()]

        return pg.transform.smoothscale(surf, target_size)

    # case 2: back is smaller than surf
    elif background.get_height() <= surface.get_height() and background.get_width() <= surface.get_width():
        if surface.get_height() <= surface.get_width():
            # wider than high, so height is smallest
            target_size = [int((background.get_height() * surface.get_width()) / surface.get_height()),
                           background.get_height()]
        else:
            # higher than wide
            target_size = [background.get_width(),
                           int((background.get_width() * surface.get_height()) / surface.get_width())]

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

    return [int((back.get_width()-surf.get_width())/2),
            int((back.get_height()-surf.get_height())/2)]


def threaded_timer(period):
    time.sleep(period)
