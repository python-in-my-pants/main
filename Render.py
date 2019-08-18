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


def update():  # not really needed here but implemented for consistency
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

            pg.mixer.music.load("assets/ass.mp3") # TODO replace with omae wa mou and play on window open in loop
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

        host_btn = Button(dim=[int(surfs_size[0]/3), int(surfs_size[1] * 0.07)],
                          pos=[int((left_surf.get_size()[0]-int(surfs_size[0]/3)/2)),
                               int(surfs_size[1]/6)],
                          name="host_btn", color=(135, 206, 235), action=host_btn_fkt, text="Host")

        self.buttons.append(host_btn)

        host_stat_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],  # TODO mach, dass der den status anzeigt
                               pos=[int((left_surf.get_size()[0]-int(surfs_size[0]/3)/2)),
                                    int(surfs_size[1] * 0.43)],
                               name="host_stat", color=(135, 206, 235), action=(lambda: None), text="Status goes here")

        self.buttons.append(host_stat_btn)

        host_cancel_btn = Button(dim=[int(surfs_size[0]/3), int(surfs_size[1] * 0.07)],
                                 pos=[int((left_surf.get_size()[0]-int(surfs_size[0]/3)/2)),
                                      int(surfs_size[1] * 0.7)],
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

        join_btn = Button(dim=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                          pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2),
                               int(surfs_size[1] / 6)],
                          real_pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2) +
                                    left_surf.get_size()[0],
                                    int(surfs_size[1] / 6)],
                          name="join_btn", color=(135, 206, 235), action=join_btn_fkt, text="Join")

        self.buttons.append(join_btn)

        join_stat_btn = Button(dim=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                               # TODO mach, dass der den status anzeigt
                               pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2),
                                    int(surfs_size[1] * 0.43)],
                               real_pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2) +
                                         left_surf.get_size()[0], int(surfs_size[1] * 0.43)],
                               name="join_stat", color=(135, 206, 235), action=(lambda: None), text="Status goes here")

        self.buttons.append(join_stat_btn)

        ip_to_join_btn = Button([int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                                pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2),
                                     int(surfs_size[1] * 0.7)],
                                real_pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2) +
                                          left_surf.get_size()[0], int(surfs_size[1] * 0.7)],
                                name="ip_to_join_btn", color=(0, 0, 0), action=ip_field_fkt, text="Enter the Host-IP")

        self.buttons.append(ip_to_join_btn)

        join_cancel_btn = Button(dim=[int(surfs_size[0] / 3), int(surfs_size[1] * 0.07)],
                                 pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2),
                                      int(surfs_size[1] * 0.84)],
                                 real_pos=[int((right_surf.get_size[0]-(surfs_size[0]/3))/2) +
                                           left_surf.get_size()[0], int(surfs_size[1] * 0.84)],
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

    def __init__(self, points_to_spend):

        self.new_window_target = InGame

        self.spent_points = 0

        size = [pg.display.Info().current_w(), pg.display.Info().current_h()]

        self.screen = pg.display.set_mode(size, flags=pg.FULLSCREEN)

        self.ownTeam = Team()  # holds actual object of own team
        self.selectedChar = None
        self.ready = False

        self.cc_num = ...  # TODO number of character cards
        self.wc_num = ...  # number of weapon cards
        self.ic_num = ...  # number of item cards

        self.render_char_ban = True
        self.render_weap_ban = True
        self.render_item_ban = True

        self.scroll_offset = 0

        # set up surfaces for screen
        # -------------------------------------------------------------------------------------------------------------

        #############
        # left side #
        #############

        # character cards go here as buttons
        troop_overview = pg.Surface([int(0.7 * size[0]), size[1]*10])  # make very long for scroll stuff

        # some vars and constants
        self.character_cards = []  # TODO: buttons
        self.weapon_cards = []
        self.item_cards = []
        self.banners = []  # TODO: buttons
        self.team_char_btns = []  # TODO: buttons
        # room between cards should be 1/8 of their width, 5 cards per line makes 6 spaces, so 5* 8/8 + 6 * 1/8
        # = 46/8, so the width has to be split in 46 equal parts where 1/46 makes the space between 2 cards
        # 46 = line_len * 9 + 1
        line_len = 5
        gap_size = int(troop_overview.get_size()[0]/(line_len*9+1))
        card_w = int(troop_overview.get_size()[0]*8/(line_len*9+1))
        card_h = int(card_w * 1.457)  # dimensions of 59/86 like Yu-gi-oh cards

        # to blit button on
        rem_point_back = pg.Surface([troop_overview.get_size()[0], int(size[1]*0.1)])

        # to blit character_banner and character_content on
        character_back = pg.Surface([troop_overview.get_size()[0],
                                     int(2*gap_size + int(card_h*self.cc_num/line_len) +
                                    (int(self.cc_num/line_len)-1)*gap_size + int(card_h*0.5))])  # add place for banner
        character_content = pg.Surface([character_back.get_size()[0], character_back.get_size()[1]-int(card_h/2)])

        weapon_back = pg.Surface([troop_overview.get_size()[0],
                                  int(2*gap_size + int(card_h*self.wc_num/line_len) +
                                  (int(self.wc_num/line_len)-1)*gap_size + int(card_h*0.5))])  # add place for banner
        weapon_content = pg.Surface([weapon_back.get_size()[0], weapon_back.get_size()[1]-int(card_h/2)])

        item_back = pg.Surface([troop_overview.get_size()[0],
                                int(2 * gap_size + int(card_h * self.ic_num / line_len) +
                               (int(self.ic_num / line_len) - 1) * gap_size + int(card_h * 0.5))])  # add place for banner
        item_content = pg.Surface([item_back.get_size()[0], item_back.get_size()[1]-int(card_h/2)])

        ##############
        # right side #
        ##############

        player_overview = pg.Surface([int(0.3 * size[0]), size[1]])

        player_banner_back = pg.Surface([int(0.3 * size[0]), int(0.3 * size[0])])
        player_banner_img = pg.image.load("assets/default_player_banner.png")  # TODO: add custom player banners

        selected_units_back = pg.Surface([int(0.3 * size[0]), int(size[1] - player_banner_back.get_height()*2)])
        selected_units_box = pg.Surface([selected_units_back.get_size()[0] - 10, selected_units_back.get_size()[1] - 10])

        selected_weapons_back = pg.Surface([int(0.3 * size[0]), int(size[1] - player_banner_back.get_height()*2)])
        selected_weapons_box = pg.Surface([selected_weapons_back.get_size()[0]-10, selected_weapons_back.get_size()[1]-10])
        # TODO: show items of selected char here

        # constants
        small_line_len = 3
        small_gap_size = int(selected_units_box.get_size()[0]/(small_line_len*9+1))
        w_small_card = int(selected_units_box.get_size()[0]*8/(small_line_len*9+1))
        h_small_card = int(w_small_card*1.457)

        # -------------------------------------------------------------------------------------------------------------
        # set up buttons
        # -------------------------------------------------------------------------------------------------------------

        ########
        # left #
        ########

        # points to spend
        def get_rem_points():
            return points_to_spend-self.spent_points

        self.points_btn = Button(img="assets/remaining_points.png", use_dim=True, \
                                 dim=[int(troop_overview.get_size()[0]*0.21), int(size[1]*0.1)], \
                                 pos=[int(troop_overview.get_size()[0]*0.305), 0],
                                 action=(lambda: None),
                                 text=get_rem_points())

        # banners
        def char_ban_func():
            if self.render_char_ban:
                character_back.get_size()[1] -= character_content.get_size()[1]
            else:
                character_back.get_size()[1] -= character_content.get_size()[1]

            self.render_char_ban = not self.render_char_ban

        def weap_ban_func():
            if self.render_weap_ban:
                weapon_back.get_size()[1] -= weapon_content.get_size()[1]
            else:
                weapon_back.get_size()[1] -= weapon_content.get_size()[1]

            self.render_weap_ban = not self.render_weap_ban

        def item_ban_func():
            if self.render_item_ban:
                item_back.get_size()[1] -= item_content.get_size()[1]
            else:
                item_back.get_size()[1] -= item_content.get_size()[1]

            self.render_item_ban = not self.render_item_ban

        # TODO: Button
        # hide of show character_content on click, height must be card_h/2 and y padding card_h/4
        character_banner = Button(dim=[int(troop_overview.get_size()[0]*0.9), int(card_h/2)],
                                  pos=[int(troop_overview.get_size()[0]*0.05), int(card_h/4)],
                                  real_pos=[int(troop_overview.get_size()[0]*0.05),
                                            int(card_h/4)+
                                            self.points_btn.dim[1]
                                            ],
                                  text="Characters", color=(50, 30, 230),
                                  action=char_ban_func)
        self.banners.append(character_banner)

        weapons_banner = Button(dim=[int(troop_overview.get_size()[0]*0.9), int(card_h/2)],
                                pos=[int(troop_overview.get_size()[0]*0.05), int(card_h/4)],
                                real_pos=[int(troop_overview.get_size()[0]*0.05),
                                          int(card_h/4)] +
                                          self.points_btn.dim[1] +
                                          character_back.get_size()[1],
                                text="Weapons", color=(230, 50, 30),
                                action=weap_ban_func)
        self.banners.append(weapons_banner)

        item_banner = Button(dim=[int(troop_overview.get_size()[0]*0.9), int(card_h/2)],
                             pos=[int(troop_overview.get_size()[0]*0.05), int(card_h/4)],
                             real_pos=[int(troop_overview.get_size()[0]*0.05),
                                       int(card_h/4) +
                                       self.points_btn.dim[1]+
                                       character_back.get_size()[1]+
                                       weapon_back.get_size()[1]],
                             text="Items", color=(30, 230, 50),
                             action=item_ban_func)
        self.banners.append(item_banner)

        # character cards
        def function_binder(name, card_num):

            def butn_fkt(card_num):

                char = ...  # TODO: add function call to get instance of corresponding class
                if self.spent_points + char.cost <= points_to_spend:
                    self.ownTeam.add_char(char)
                    self.spent_points -= char.cost
                else:
                    # TODO: take out
                    print("Too expensive, cannot buy")

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.cc_num):

            w_pos = gap_size + (i % (line_len-1)) * (card_w+gap_size)

            #               height of point counter + line_len_factor         *  card height plus gap
            h_pos = self.points_btn.get_size()[1] + 5 + i * int((i + 1) / line_len) * (gap_size + card_h)

            card_btn = Button(pos=[w_pos, h_pos],
                              real_pos=[w_pos,
                                        h_pos +
                                        self.points_btn.dim[1] +
                                        character_banner.dim[1]],
                              img=("assets/cc/cc_" + str(i) + ".png"), dim=[card_w, card_h], \
                              use_dim=True, action=function_binder("cc_btn_function_" + str(i), i))

            self.character_cards.append(card_btn)

        # weapon cards
        def weapon_function_binder(name, card_num):

            def butn_fkt(card_num):

                weap = ...  # TODO: add function call to get instance of corresponding class
                if self.spent_points + weap.cost <= points_to_spend:
                    self.selectedChar.weapons.append(weap)
                    self.spent_points -= weap.cost
                else:
                    # TODO: take out
                    print("Too expensive, cannot buy")

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.wc_num):

            w_pos = gap_size + (i % (line_len-1)) * (card_w+gap_size)

            #               height of point counter + line_len_factor         *  card height plus gap
            h_pos = self.points_btn.get_size()[1] + 5 + i * int((i + 1) / line_len) * (gap_size + card_h)

            card_btn = Button(pos=[w_pos, h_pos],
                              real_pos=[w_pos,
                                        h_pos +
                                        self.points_btn.dim[1]] +
                                        character_back.get_size()[1] +
                                        weapons_banner.dim[1],
                              img=("assets/wc/wc_" + str(i) + ".png"), dim=[card_w, card_h], \
                              use_dim=True, action=weapon_function_binder("wc_btn_function_" + str(i), i))

            self.weapon_cards.append(card_btn)

        # item cards
        def item_function_binder(name, card_num):

            def butn_fkt(card_num):

                item = ...  # TODO: add function call to get instance of corresponding class
                if self.spent_points + item.cost <= points_to_spend:
                    self.ownTeam.add_char(item)
                    self.spent_points -= item.cost
                else:
                    # TODO: take out
                    print("Too expensive, cannot buy")

            butn_fkt.__name__ = name
            return butn_fkt

        for i in range(self.ic_num):

            w_pos = gap_size + (i % (line_len-1)) * (card_w+gap_size)

            #               height of point counter + line_len_factor         *  card height plus gap
            h_pos = self.points_btn.get_size()[1] + 5 + i * int((i + 1) / line_len) * (gap_size + card_h)

            card_btn = Button(pos=[w_pos, h_pos],
                              real_pos=[w_pos,
                                        h_pos +
                                        self.points_btn.dim[1] +
                                        character_back.dim[1] +
                                        weapon_back.dim[1] +
                                        item_banner.dim[1]],
                              img=("assets/ic/ic_" + str(i) + ".png"), dim=[card_w, card_h], \
                              use_dim=True, action=item_function_binder("ic_btn_function_" + str(i), i))

            self.item_cards.append(card_btn)

        #########
        # right #
        #########

        # --------------------------------------------------------------------
        # buttons for own team members
        # if you click them, the weapons and item of this character are show and bought items are equipped to this char
        # --------------------------------------------------------------------

        # blit to selected_units_box
        def cc_function_binder(name, _char_id):

            def btn_fkt(_char_id, button=1):
                if button == 1:
                    # show characters items in selected_weapons_box and set him as selected char
                    self.selectedChar = self.ownTeam.get_char_by_id(_char_id)
                if button == 3:
                    # sell this character
                    char = self.ownTeam.get_char_by_id(_char_id)
                    self.ownTeam.remove_char_by_obj(char)
                    self.selectedChar = self.ownTeam.characters[0]

                    self.spent_points -= char.cost
                    nonlocal points_to_spend
                    points_to_spend += char.cost

            btn_fkt.__name__ = name
            return btn_fkt

        for i in range(self.ownTeam.characters.__len__()):

            pos_w = small_gap_size + (i % (small_line_len-1)) * (w_small_card+small_gap_size)
            pos_h = small_gap_size + i * int((i+1) / small_line_len) * (small_gap_size + h_small_card)

            class_num = character_classes[self.ownTeam.characters[i].unit_class]

            btn = Button(dim=[w_small_card, h_small_card], pos=[pos_w, pos_h],
                         real_pos=[pos_w +
                                   int((selected_units_back.get_size()[0]-selected_units_box.get_size()[0])/2) +
                                   troop_overview.get_size()[0],
                                   pos_h +
                                   int((selected_units_back.get_size()[1] - selected_units_box.get_size()[1]) / 2) +
                                   player_banner_back.get_size()[1]],
                         img=("assets/cc/cc_" + str(class_num) + ".png"),
                         use_dim=True, action=cc_function_binder("assets/cc/cc_small_btn_func" + str(i), \
                                                                 self.ownTeam.characters[i].id))

            self.team_char_btns.append(btn)

        # ----------------------------------------------------------
        # equipped items and shit
        # ----------------------------------------------------------

        if self.selectedChar is not None:
            gear = self.selectedChar.gear
            weapons = self.selectedChar.weapons
            items = self.selectedChar.items
        else:
            gear = []
            weapons = []
            items = []

        def ic_function_binder(name, _category, _id):

            def btn_fkt(_category, _id, button=1):
                if button == 3:

                    # sell this item
                    thing_to_sell = None

                    if _category == "gear":
                        for g in gear:
                            if g.id == _id:
                                thing_to_sell = g

                                self.spent_points -= thing_to_sell.cost
                                nonlocal points_to_spend
                                points_to_spend += thing_to_sell.cost

                                gear.remove(g)

                    if _category == "weapon":
                        for w in weapons:
                            if w.id == _id:
                                thing_to_sell = w

                                self.spent_points -= thing_to_sell.cost
                                nonlocal points_to_spend
                                points_to_spend += thing_to_sell.cost

                                weapons.remove(w)

                    if _category == "item":
                        for item in items:
                            if item.id == _id:
                                thing_to_sell = item

                                self.spent_points -= thing_to_sell.cost
                                nonlocal points_to_spend
                                points_to_spend += thing_to_sell.cost

                                item.remove(item)

            btn_fkt.__name__ = name
            return btn_fkt

        for i in range(gear.__len__() + weapons.__len__() + items.__len__()):

            pos_w = small_gap_size + (i % (small_line_len-1)) * (w_small_card+small_gap_size)
            pos_h = small_gap_size + i * int((i+1) / small_line_len) * (small_gap_size + h_small_card)

            image_uri = ""
            cat = None
            id = 0

            # TODO check for errors
            if i < gear.__len__():
                image_uri = "assets/gc/small/gc_" + str(i) + ".png"
                cat = "gear"
                id = i

            if gear.__len__() <= i < weapons.__len__() + gear.__len__():
                image_uri = "assets/wc/small/wc_" + str(i-gear.__len__()) + ".png"
                cat = "weapon"
                id = i - gear.__len__()

            if i >= gear.__len__() + weapons.__len__():
                image_uri = "assets/ic/small/ic_" + str(i-gear.__len__()-weapons.__len__()) + ".png"
                cat = "item"
                id = i - gear.__len__() - weapons.__len__()

            btn = Button(dim=[w_small_card, h_small_card], pos=[pos_w, pos_h],
                         real_pos=[pos_w +
                                   troop_overview.get_size()[0] +
                                   int((selected_weapons_back.get_size()[0]-selected_units_box.get_size()[0])/2),
                                   pos_h +
                                   player_banner_back.get_size()[1] +
                                   selected_units_box.get_size()[0] +
                                   int((selected_weapons_back.get_size()[1]-selected_units_box.get_size()[1])/2)],
                         img=image_uri, use_dim=True, action=ic_function_binder("ci_small_btn_func" + str(i),
                                                                                _category=cat, _id=id))

            self.team_char_btns.append(btn)

        # to blit to player_banner_back
        # ready button
        def ready_up():

            self.ready = not self.ready
            # TODO: CHRISTIAN <3 when ready, sync wait for other player to be

        def get_text():
            return "Unready" if self.ready else "Ready!"

        #TODO: button
        self.ready_btn = Button(dim=[int(player_banner_back.get_size()[0]*0.8), int(player_banner_back.get_size()[1]*0.25)],
                                text=get_text(), \
                                pos=[int(player_banner_back.get_size()[0]*0.1), player_banner_img.get_size()[1]],
                                real_pos=[int(player_banner_back.get_size()[0]*0.1) +
                                          troop_overview.get_size()[0],
                                          player_banner_img.get_size()[1]],
                                action=ready_up)

        # -------------------------------------------------------------------------------------------------------------
        # now blit everything to the desired position
        # -------------------------------------------------------------------------------------------------------------

        ########
        # left #
        ########

        # TODO: maybe add big image of selected char and selected weap at left side ... or maybe not 'cause you'd have to rework button positions again

        # cards and banners
        character_back.blit(character_banner, character_banner.pos)
        if self.render_char_ban:
            for char_btn in self.character_cards:
                character_content.blit(char_btn.surf, char_btn.pos)
            character_back.blit(character_content, [0, character_banner.dim[1]])

        weapon_back.blit(weapons_banner, weapons_banner.pos)
        if self.render_weap_ban:
            for weapon_btn in self.weapon_cards:
                weapon_content.blit(weapon_btn.surf, weapon_btn.pos)
            weapon_back.blit(weapon_content, [0, weapons_banner.dim[1]])

        item_back.blit(item_banner, item_banner.pos)
        if self.render_item_ban:
            for item_btn in self.item_cards:
                item_content.blit(item_btn.surf, item_btn.pos)
            item_back.blit(item_content, [0, item_banner.dim[1]])

        # TODO: blit background image
        # points btn to left side
        troop_overview.blit(self.points_btn.surf, dest=self.points_btn.pos)

        troop_overview.blit(character_back, dest=[0, self.points_btn.dim[1]])
        troop_overview.blit(weapon_back, dest=[0, self.points_btn.dim[1]+character_back.get_size()[1]])
        troop_overview.blit(item_back, dest=[0, self.points_btn.dim[1]+character_back.get_size()[1]+weapon_back.get_size()[1]])

        #########
        # right #
        #########

        # player banner
        player_banner_back.blit(player_banner_img, dest=[0, 0])
        player_banner_back.blit(self.ready_btn.surf, self.ready_btn.pos)

        player_overview.blit(player_banner_back, [0, 0])

        # selected units
        for sm_char_btn in self.team_char_btns:
            selected_units_box.blit(sm_char_btn.surf, sm_char_btn.pos)

        selected_units_back.blit(selected_units_box, dest=
                                 [int((selected_units_back.get_size()[0]-selected_units_box.get_size()[0])/2),
                                  int((selected_units_back.get_size()[1]-selected_units_box.get_size()[1])/2)])

        player_overview.blit(selected_units_back, dest=[0, player_banner_back.get_size()[1]])

        # selected weapons

        selected_weapons_back.blit(selected_weapons_box, dest=
                                   [int((selected_weapons_back.get_size()[0]-selected_weapons_box.get_size()[0])/2),
                                    int((selected_weapons_back.get_size()[0]-selected_weapons_box.get_size()[0])/2)])

        player_overview.blit(selected_weapons_back, dest=
                             [0, player_banner_back.get_size()[1] + selected_weapons_back.get_size()[1]])

        ###########################
        # right and left together #
        ###########################

        self.screen.blit(troop_overview, [0, self.scroll_offset])
        self.screen.blit(player_overview, [troop_overview.get_size()[0], 0])

    def event_handling(self):

        # event handling
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()

                if event.button == 1:  # on left click
                    for button in self.character_cards:
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
                            button.action()

                    if self.ready_btn.is_focused(p):
                        self.ready_btn.action()

                    for banner_btn in self.banners:
                        if banner_btn.is_focused(p):
                            banner_btn.action()

                if event.button == 3:  # on right click

                    for button in self.team_char_btns:
                        if button.is_focused(p):
                            button.action(button=3)

                if event.button == 4:  # scroll up

                    self.scroll_offset -= 10

                if event.button == 5:  # scroll down

                    self.scroll_offset += 10


class InGame:

    def __init__(self, own_team, game_map):

        self.next_window_target = MainWindow  # TODO

        self.char_prev_selected = False  # holds if own team character is already selected

        size = [pg.display.Info().current_w(), pg.display.Info().current_h()]
        w = size[0]
        h = size[1]
        self.element_size = int(w*9/(16*30)) # default is 30 elem width
        self.screen = pg.display.set_mode(size, flags=pg.FULLSCREEN)

        self.selected_own_char = own_team[0] # TODO
        self.selected_item = own_team[0].items[0]
        self.selected_weapon = own_team[0].weapons[0]

        self.selected_char = self.selected_own_char

        # set up surfaces
        # -------------------------------------------------------------------------------------------------------------

        char_stat_back = pg.Surface([int(7*w/32), int(7*h/18)])
        char_stat_card = pg.image.load(...) # TODO enter URI for sel character card square, empty stub for begin

        char_inventory = pg.Surface([int(7*w/32), int(4*h/18)])
        inventory_gear_weapons = pg.Surface([int(7*w/32), int(0.34*4*h/18)]) # 2 first are gear, last 3 are weapons
        inventory_items = pg.Surface([int(7*w/32), int(0.66*4*h/18)])  # 2 rows high

        item_stat_back = pg.Surface([int(7*w/32), int(7*h/18)])
        # TODO make so that actual stats are shown in character card instead of just standard stats
        item_stat_card = pg.image.load(...)


        map_surface = game_map.window #(int(9*w/16), h)
        #                   gap size up and down        factor                                    gap size                btn_h * 1.6 for hp bar
        own_team_height = 2*int((1/32) * 7*w/32) + (int(own_team.characters.__len__() / 10)+1) * (int((1/32) * 7*w/32) + int(1.6 * (5/32) * 7*w/32))
        own_team_stats = pg.Surface([int(map_surface.get_size()[0]*0.9), own_team_height]) #int(0.2*7*h/18)])
        own_team_stats_back_img = pg.image.load(...) # TODO size from own team stats


        player_banners = pg.Surface([int(7*w/32), int(7*h/18)])
        match_stats = pg.Surface([player_banners.get_size()[0], int(player_banners.get_size()[1]*0.2)])

        minimap_surf = pg.Surface([int(7*w/32), int(7*h/18)]) # TODO
        done_btn_surf = pg.Surface([int(7*w/32), int(4*h/18)])

        # set up buttons
        # TODO characters on map must have buttons to select them as sel char
        # -------------------------------------------------------------------------------------------------------------

        # button functions

        def weap_func_binder(name, _id, type):

            def func(_id):

                if type == "weap":
                    for weap in self.selected_own_char.weapons:
                        if weap.idi == _id:
                            self.selected_own_char.active_weapon = weap
                            return

                if type == "item":
                    for item in self.selected_own_char.items:
                        if weap.idi == _id:
                            self.selected_own_char.active_item = item
                            return

            func.__name__ = name
            return func

        def sel_own_char_binder(name, _id):

            def func(_id):
                self.selected_own_char = own_team.get_char_by_id(_id)

            func.__name__ = name
            return func

        def sel_char_binder(name, _id):

            def func(_id):
                for _index in game_map.characters:
                    _char = game_map.objects[_index]
                    if _char.idi == _id:
                        if own_team.get_char_by_id(_id):
                            self.selected_own_char = char
                        else:
                            # own sel char wants to attack char
                            ...  # TODO attack routine
                        return

            func.__name__ = name
            return func

        def done_button_action(): # TODO
            pass

        # -------------------------------------------------------------------------------------------------------------
        # buttons and bars

        gear_buttons = []  # TODO buttons
        weapon_buttons = []
        item_buttons = []

        own_team_stat_buttons= []
        hp_bars = []

        char_map_buttons = []

        # constants
        inventory_gap_size = int((1/32) * 7*w/32)
        btn_w = int((5/32) * 7*w/32)
        btn_h = btn_w

        # gear buttons
        for i in range(self.selected_own_char.gear.__len__()):

            pos_w = (i+1) * inventory_gap_size + i*btn_w
            pos_h = inventory_gap_size

            btn = Button(dim=[btn_w, btn_h],
                         pos=[pos_w, pos_h],
                         real_pos=[pos_w,
                                   pos_h +
                                   char_stat_back.get_size()[1]],
                         img="assets/ic/small/ic_" + str(self.selected_own_char.gear.class_num) + ".png",
                         text="", name=("gear " + str(self.selected_own_char.gear.class_num) + " button"),
                         action=(lambda: None))

            gear_buttons.append(btn)

        # weapon buttons
        for i in range(self.selected_own_char.weapons.__len__()):

            pos_w = 2*btn_w + 4*inventory_gap_size + i*(inventory_gap_size+btn_w)
            pos_h = inventory_gap_size

            btn = Button(dim=[btn_w, btn_h],
                         pos=[pos_w, pos_h],
                         real_pos=[pos_w,
                                   pos_h +
                                   char_stat_back.get_size()[1]],
                         img="assets/wc/small/wc_" + str(self.selected_own_char.weapons.class_num) + ".png",
                         text="", name=("weapon " + str(self.selected_own_char.weapons.class_num) + ".png"),
                         action=weap_func_binder("weapon " + str(self.selected_own_char.weapons.class_num),
                                                 self.selected_own_char.weapons[i].idi, type="weapon"))

            weapon_buttons.append(btn)

        # item buttons
        for i in range(self.selected_own_char.items.__len__()):

            pos_w = inventory_gap_size + (i % 5)*(btn_w + inventory_gap_size)
            pos_h = inventory_gap_size + (i % 5)*(btn_h + inventory_gap_size)

            btn = Button(dim=[btn_w, btn_h],
                         pos=[pos_w, pos_h],
                         real_pos=[pos_w,
                                   pos_h +
                                   char_stat_back.get_size()[1] +
                                   inventory_gear_weapons.get_size()[1]],
                         img="assets/ic/small/ic_" + str(self.selected_own_char.items.class_num) + ".png",
                         text="", name=("item " + str(self.selected_own_char.items.class_num) + ".png"),
                         action=weap_func_binder("item " + str(self.selected_own_char.items.class_num),
                                                 self.selected_own_char.items[i].idi, type="item"))

            item_buttons.append(btn)

        # hp bars, blit to own team stats
        # TODO update hp bars each tick
        for i in range(own_team.characters.__len__()):

            pos_w = btn_w + (i % 10) * (btn_w + inventory_gap_size)
            pos_h = inventory_gap_size + btn_h + int(i / 10) * (btn_h + inventory_gap_size + btn_h * 0.6)

            bars = []

            for j in range(5):

                hp_bar = HPBar(dim=[btn_w, int(0.1 * btn_h)],
                               pos=[pos_w, pos_h + 0.1*j*btn_h],
                               curr=own_team.characters[i].health[j],
                               end=100)
                bars.append(hp_bar)

            hp_bars.append(bars)

        # team buttons
        for i in range(own_team.characters.__len__()):

            pos_w = btn_w + (i%10)*(btn_w+inventory_gap_size)
            pos_h = inventory_gap_size + int(i / 10)*(btn_h + inventory_gap_size + btn_h*0.6)

            btn = Button(dim=[btn_w, btn_h],
                         pos=[pos_w, pos_h],
                         real_pos=[pos_w +
                                   char_stat_back.get_size()[0] +
                                   int(minimap_surf.get_size()[0]*0.05),
                                   pos_h],
                         img=("assets/cc/small/cc_" + str(own_team.characters[i].unit_class) + ".png"),
                         text="", name="char btn " + str(own_team.characters[i].unit_class),
                         action=sel_own_char_binder("chat_btn_" + str(own_team.characters.idi), own_team.characters[i].idi))

            own_team_stat_buttons.append(btn)

        for index in game_map.characters:
            char = game_map.objects[index]

            btn = Button(dim=[self.element_size, self.element_size],
                         pos=[char.get_pos(0) * self.element_size, char.get_pos(1) * self.element_size],
                         real_pos=[char.get_pos(0) * self.element_size +
                                   char_stat_back.get_size()[0],
                                   char.get_pos(1) * self.element_size],
                         img="assets/char/" + str(char.unit_class) + ".png",
                         action=sel_char_binder("map_char_btn_" + str(char.idi), char.idi))

            char_map_buttons.append(btn)

        # done button
        done_btn = Button(dim=[int(7*w/32), int(4*h/18)], # TODO button
                          pos=[0,0],
                          real_pos=[char_stat_back.get_size()[0] +
                                    map_surface.get_size()[0],
                                    player_banners.get_size()[1] +
                                    minimap_surf.get_size()[1]],
                          img="assets/done_button.png",
                          name="Done Button", action=done_button_action)

        # blit everything to positions
        # ------------------------------------------------------------------------------------------------------------

        char_stat_back.blit(char_stat_card, dest=[int(char_stat_back.get_size()[0]*0.05),
                                                  int(char_stat_back.get_size()[0]*0.05)])

        for btn in gear_buttons:
            inventory_gear_weapons.blit(btn.surf, btn.pos)

        for btn in weapon_buttons:
            inventory_gear_weapons.blit(btn.surf, btn.pos)

        for btn in item_buttons:
            inventory_items.blit(btn.surf, btn.pos)

        char_inventory.blit(inventory_gear_weapons, dest=[0, 0])
        char_inventory.blit(inventory_items, dest=[0, inventory_gear_weapons.get_size()[1]])

        item_stat_back.blit(item_stat_card, dest=[int(item_stat_back.get_size()[0]*0.05),
                                                  int(item_stat_back.get_size()[0]*0.05)])

        own_team_stats.blit(own_team_stats_back_img, dest=[0, 0])

        for bar in hp_bars:
            own_team_stats.blit(bar.surf, bar.pos)

        for btn in own_team_stat_buttons:
            own_team_stats.blit(btn.surf, btn.pos)

        map_surface.blit(own_team_stats, dest=[int(0.05*map_surface.get_size()[0]), 0]) # TODO beware of 0.05 as constant

        player_banners.blit(match_stats, dest=[0, int(0.8*player_banners.get_size()[1])])

        done_btn_surf.blit(done_btn.surf, done_btn.pos)


        self.screen.blit(char_stat_back, dest=[0, 0])
        self.screen.blit(char_inventory, dest=[0, char_stat_back.get_size()[1]])
        self.screen.blit(item_stat_back, dest=[0, char_stat_back.get_size()[1]+char_inventory.get_size()[1]])

        self.screen.blit(map_surface, dest=[char_stat_back.get_size()[1], 0])

        self.screen.blit(player_banners, dest=[char_stat_back.get_size()[0]+map_surface.get_size()[0], 0])
        self.screen.blit(minimap_surf, dest=[char_stat_back.get_size()[0]+map_surface.get_size()[0],
                                             player_banners.get_size()[1]])
        self.screen.blit(done_btn_surf, dest=[char_stat_back.get_size()[0]+map_surface.get_size()[0],
                                              player_banners.get_size()[1]+minimap_surf.get_size()[1]])

    def event_handling(self):
        pass
