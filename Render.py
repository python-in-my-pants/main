'''

Gives general classes and fuctions for rendering on screen

'''

import Map
import pygame as pg
from GUI import *
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
        # use convert for better redering performance
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

        main_background_img = pg.image.load("assets/108.gif")  # "main_background.jpg")

        size = list(main_background_img.get_size())
        size[0] = size[0] * 5  # change to sth dependent on screen size instead of 5
        size[1] = size[1] * 5

        # create window
        self.connect_screen = pg.display.set_mode(size)
        # set title
        pg.display.set_caption("nAme;Rain - Verbindungskonfiguration ...")

        # scale image
        main_background_img = pg.transform.scale(main_background_img, (size[0], size[1]))
        main_background_img = main_background_img.convert()

        # draw background to screen
        self.connect_screen.blit(main_background_img, (0, 0))

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

        self.connect_screen.blit(left_surf, (0, 0))
        self.connect_screen.blit(right_surf, (surfs_size[0], 0))

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



