'''

Gives general classes and fuctions for rendering on screen

'''

import Map
import pygame as pg
from GUI import *
from Team import *
from Data import *
import time


'''
elem size,
fields
'''


def update(self):  # not really needed here but implemented for consistency
    pg.display.update()


class MainWindow:

    def __init__(self):  # creates main window with contents -> "mainscreen"

        # holds new window target if you want to leave this screen because the user clicked a button or sth
        self.new_window_target = "None"

        main_background_img = pg.image.load("assets/108.gif")  # "assets/main_background.jpg")

        size = list(main_background_img.get_size())
        size[0] = size[0] * 5  # make depended on screen size
        size[1] = size[1] * 5

        # build surface in the size of "size"
        self.screen = pg.display.set_mode(size)
        # set window name
        pg.display.set_caption("nAme;Rain - Mainscreen")

        # scale image to desired size ("size")
        main_background_img = pg.transform.scale(main_background_img, (size[0], size[1]))
        # use convert for better rendering performance
        main_background_img = main_background_img.convert()

        # draw background image on screen
        self.screen.blit(main_background_img, (0, 0))

        # ------------------------------------------------------
        # set up GUI

        self.buttons = []

        def button_fkt():

            pg.mixer.music.load("assets/ass.mp3")
            pg.mixer.music.play(0)
            time.sleep(2.5)

            # go to different window and kill this one
            self.new_window_target = ConnectionSetup
            # delete this from Main!

        btn = Button([int(0.2 * size[0]), int(0.069 * size[1])],
                     pos=[size[0] / 2 - int(0.2 * size[0]) / 2, size[1] / 2 - int(0.069 * size[1]) / 2 + 200],
                     name="Button 1", img="assets/blue_button_menu.jpg", action=button_fkt, text="Play")

        # render Button to screen
        self.screen.blit(btn.surf, btn.pos)
        # add button to button list
        self.buttons.append(btn)

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


class ConnectionSetup:

    def __init__(self):

        # TODO overthink if this works
        self.new_window_target = CharacterSelection

        main_background_img = pg.image.load("assets/108.gif")  # "main_background.jpg")

        size = list(main_background_img.get_size())
        size[0] = size[0] * 5  # change to sth dependent on screen size instead of 5
        size[1] = size[1] * 5

        # create window
        self.screen = pg.display.set_mode(size)
        # set title
        pg.display.set_caption("nAme;Rain - Verbindungskonfiguration ...")

        # scale image
        main_background_img = pg.transform.scale(main_background_img, (size[0], size[1]))
        main_background_img = main_background_img.convert()

        # draw background to screen
        self.screen.blit(main_background_img, (0, 0))

        # set up GUI ---------------------------------------------------------------------------------------------------

        # we need 2 surfaces that are transparent

        left_surf = pg.Surface([int(size[0]/2), size[1]])  # TODO: is it working?
        left_surf.set_colorkey((255, 255, 255))

        right_surf = pg.Surface([int(size[0]/2), size[1]])
        right_surf.set_colorkey((255, 255, 255))

        surfs_size = list(left_surf.get_size())  # only 1 because they are equally big

        # define list of buttons

        self.buttons = []

        # button functions need to be defined before buttons

        def host_btn_fkt():
            pass  # TODO für Dich, Christian <3

        def cancel_host_fkt():
            pass  # TODO für Dich, Christian <3

        def back_fkt():
            pass  # TODO mach ich

        # define buttons and put them on their surface

        host_btn = Button([int(surfs_size[0]/3), int(surfs_size[1] * 0.07)],
                          pos=[int(surfs_size[0]/3), int(surfs_size[1]/6)],
                          name="host_btn", color=(135, 206, 235), action=host_btn_fkt, text="Host")

        self.buttons.append(host_btn)

        host_stat_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],  # TODO mach, dass der den stat anzeigt
                               pos=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.43)],
                               name="host_stat", color=(135, 206, 235), action=(lambda: None), text="Status goes here")

        self.buttons.append(host_stat_btn)

        host_cancel_btn = Button([int(surfs_size[0]/3), int(surfs_size[1] * 0.07)],
                                 pos=[int(surfs_size[0]/3), int(surfs_size[1] * 0.7)],
                                 name="cancel_host", color=(250, 128, 114), action=cancel_host_fkt, text="Cancel")

        self.buttons.append(host_cancel_btn)

        back_btn = Button(pos=[0, 0], use_dim=False, name="back_btn", img="geiler_button.png", action=back_fkt, text="")

        self.buttons.append(back_btn)

        left_surf.blit(host_btn.surf, host_btn.pos)
        left_surf.blit(host_stat_btn.surf, host_stat_btn.pos)
        left_surf.blit(host_cancel_btn.surf, host_cancel_btn.pos)
        left_surf.blit(back_btn.surf, back_btn.pos)

        # -------------------------------------------------------------------------------------------------------------

        def join_btn_fkt():
            pass  # TODO für Dich, Christian <3, kannst von ausgehen, dass die ip im text von ip_to_join_btn steht

        def cancel_join_fkt():
            pass  # TODO für Dich, Christian <3

        first_click = True

        def ip_field_fkt():
            # on first click erase content, else do nothing
            nonlocal first_click
            if first_click:
                ip_to_join_btn.text = ""
                first_click = False

        join_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                          pos=[int(surfs_size[0] / 3), int(surfs_size[1] / 6)],
                          name="join_btn", color=(135, 206, 235), action=join_btn_fkt, text="Join")

        self.buttons.append(join_btn)

        join_stat_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                               # TODO mach, dass der den stat anzeigt
                               pos=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.43)],
                               name="join_stat", color=(135, 206, 235), action=(lambda: None), text="Status goes here")

        self.buttons.append(join_stat_btn)

        ip_to_join_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                                pos=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.7)],
                                name="ip_to_join_btn", color=(0, 0, 0), action=ip_field_fkt, text="Enter the Host-IP")

        self.buttons.append(ip_to_join_btn)

        join_cancel_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                                 pos=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.84)],
                                 name="cancel_join", color=(250, 128, 114), action=cancel_join_fkt, text="Cancel")

        self.buttons.append(join_cancel_btn)

        right_surf.blit(join_btn.surf, join_btn.pos)
        right_surf.blit(join_stat_btn.surf, join_stat_btn.pos)
        right_surf.blit(join_cancel_btn.surf, join_cancel_btn.pos)
        right_surf.blit(ip_to_join_btn.surf, ip_to_join_btn.pos)

        # put right and left surface to screen

        self.screen.blit(left_surf, (0, 0))
        self.screen.blit(right_surf, (surfs_size[0], 0))

    def event_handling(self):

        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_KP0:
                    self.buttons[6].text.append("0")
                if event.key == pg.K_KP1:
                    self.buttons[6].text.append("1")
                if event.key == pg.K_KP2:
                    self.buttons[6].text.append("2")
                if event.key == pg.K_KP3:
                    self.buttons[6].text.append("3")
                if event.key == pg.K_KP4:
                    self.buttons[6].text.append("4")
                if event.key == pg.K_KP5:
                    self.buttons[6].text.append("5")
                if event.key == pg.K_KP6:
                    self.buttons[6].text.append("6")
                if event.key == pg.K_KP7:
                    self.buttons[6].text.append("7")
                if event.key == pg.K_KP8:
                    self.buttons[6].text.append("8")
                if event.key == pg.K_KP9:
                    self.buttons[6].text.append("9")

                if event.key == pg.K_0:
                    self.buttons[6].text.append("0")
                if event.key == pg.K_1:
                    self.buttons[6].text.append("1")
                if event.key == pg.K_2:
                    self.buttons[6].text.append("2")
                if event.key == pg.K_3:
                    self.buttons[6].text.append("3")
                if event.key == pg.K_4:
                    self.buttons[6].text.append("4")
                if event.key == pg.K_5:
                    self.buttons[6].text.append("5")
                if event.key == pg.K_6:
                    self.buttons[6].text.append("6")
                if event.key == pg.K_7:
                    self.buttons[6].text.append("7")
                if event.key == pg.K_8:
                    self.buttons[6].text.append("8")
                if event.key == pg.K_9:
                    self.buttons[6].text.append("9")

                for char in "abcdefghijklmnopqrstuvwxyz":
                    if event.key == ord(char):
                        self.buttons[6].text.append(char)

                if event.key == pg.K_PERIOD:
                    self.buttons[6].text.append(".")
                if event.key == pg.K_KP_PERIOD:
                    self.buttons[6].text.append(".")
                if event.key == pg.K_COLON:
                    self.buttons[6].text.append(":")

                if event.key == pg.K_BACKSPACE:
                    del self.buttons[6].text[-1]

            if event.type == pg.MOUSEBUTTONDOWN:
                if pg.mouse.get_pressed()[0]:
                    for b in self.buttons:
                        if b.is_focused(pg.mouse.get_pos()):
                            b.action()


class CharacterSelection:

    def __init__(self):

        self.new_window_target = InGame

        size = [pg.display.Info().current_w(), pg.display.Info().current_h()]

        self.screen = pg.display.set_mode(size, flags=pg.FULLSCREEN)

        self.ownTeam = Team()  # holds actual object of own team

        self.ready = False

        # set up surfaces for screen
        # -------------------------------------------------------------------------------------------------------------

        #############
        # left side #
        #############
        troop_overview = pg.Surface([int(0.7 * size[0]), size[1]])

        # TODO: add in some kind of scrollable surface here later

        # background image for points to spend
        points = pg.image.load("remaining_points.png").convert()

        # character cards go here as buttons

        ##############
        # right side #
        ##############
        player_overview = pg.Surface([int(0.3 * size[0]), size[1]])

        player_banner_back = pg.Surface([int(0.3 * size[0]), int(0.3 * size[0])])
        player_banner_img = pg.image.load("default_player_banner.png")  # TODO: add custom player banners

        selected_units_back = pg.Surface([int(0.3 * size[0]), int(size[1] - player_banner_back.get_height()*2)])
        selected_units_box = pg.Surface([selected_units_back.get_size()[0] - 10, selected_units_back.get_size()[1] - 10])

        selected_weapons_back = pg.Surface([int(0.3 * size[0]), int(size[1] - player_banner_back.get_height()*2)])
        selected_units_box = pg.Surface([selected_weapons_back.get_size()[0]-10, selected_weapons_back.get_size()[1]-10])

        # set up buttons
        # -------------------------------------------------------------------------------------------------------------

        ########
        # left #
        ########

        character_cards = []  #TODO: buttons
        number_of_character_cards = 0
        line_len = 5

        # room between cards should be 1/8 of their width, 5 cards per line makes 6 spaces, so 5* 8/8 + 6 * 1/8
        # = 46/8, so the width has to be split in 46 equal parts where 1/46 makes the space between 2 cards
        # 46 = line_len * 9 + 1
        gap_size = int(troop_overview.get_size()[0]/(line_len*9+1))
        card_w = int(troop_overview.get_size()[0]*8/(line_len*9+1))
        card_h = int(card_w * 1.457)  # dimensions of 59/86 like Yu-gi-oh cards

        def function_binder(name, card_num):

            def butn_fkt(card_num):

                char = ... # TODO: add function call to get instance of corresponding class
                self.ownTeam.add_char(char)

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(number_of_character_cards):

            w_pos = gap_size + (i % (line_len-1)) * (card_w+gap_size)

            #               height of point counter + line_len_factor         *  card height plus gap
            h_pos = points.get_size()[1] + 5 + i*int((i+1) / line_len) * (gap_size + card_h)

            card_btn = Button(pos=[w_pos, h_pos], img=("cc_" + str(i) + ".png"), dim=[card_w, card_h], use_dim=True, \
                              action=function_binder("cc_btn_function_" + str(i), i))

            character_cards.append(card_btn)

        # TODO: Add this later, see plan for this screen for details
        # category_banner_weapons_btn = Button()

        #########
        # right #
        #########

        # buttons for own team members
        # if you click them, the weapons and item of this character are show and bought items are equipped to this char

        # blit to selected_units_box
        team_char_btns = []  #TODO: buttons
        small_line_len = 3

        small_gap_size = int(selected_units_box.get_size()[0]/(small_line_len*9+1))
        w_small_card = int(selected_units_box.get_size()[0]*8/(small_line_len*9+1))
        h_small_card = int(w_small_card*1.457)

        def cc_function_binder(name, id):

            def btn_fkt(id):
                pass

            btn_fkt.__name__ = name
            return btn_fkt

        for i in range(self.ownTeam.characters.__len__()):

            pos_w = small_gap_size + (i % (small_line_len-1)) * (w_small_card+small_gap_size)
            pos_h = small_gap_size + i * int( (i+1) / small_line_len) * (small_gap_size + h_small_card)

            class_num = character_classes[self.ownTeam.characters[i].unit_class]

            btn = Button(dim=[w_small_card, h_small_card], pos=[pos_w, pos_h], \
                         img=("cc_" + str(class_num) + ".png"),
                         use_dim=True, action=cc_function_binder("cc_small_btn_func" + str(i), \
                                                                 self.ownTeam.characters[i].id))

            team_char_btns.append(btn)

        # blit to player_banner_back
        # ready button
        def ready_up():

            self.ready = not self.ready

        def get_text():
            return "Unready" if self.ready else "Ready!"

        ready_btn = Button(dim=[player_banner_back.get_size()[0]*0.8, player_banner_back.get_size()[1]*0.25],
                           text=get_text(), \
                           pos=[player_banner_back.get_size()[0]*0.1, \
                                player_banner_back.get_size()[1], player_banner_img.get_size()[1]],
                           action=ready_up)
        #TODO: button

        # -------------------------------------------------------------------------------------------------------------
        # now blit everything to the desired position

        #TODO

    def event_handling(self):




class InGame:

    def __init__(self):
        pass