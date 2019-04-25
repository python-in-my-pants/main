# encoding: UTF-8

import pygame as pg
from pygame.locals import *
from skimage.draw import line_aa
import numpy as np
import sys

from Game_objects import *
from GUI import *
from Data import *
from Map import *
from Characters import Character

elem_size = 25
debug = True





pg.init()
mode = "mainscreen"

# get correct screen size

mon = pg.display.Info()
#screen_h = int((mon.current_h-150) * 0.66)
screen_h = int(mon.current_h)-3*elem_size
screen_w = int(mon.current_w)-3*elem_size

if True:
    fields_x = 30  # width
    fields_y = 30  # height

    elem_size = int(screen_w/fields_x) if int(screen_w/fields_x) < int(screen_h/fields_y) else int(screen_h/fields_y)

    x = elem_size * fields_x  # mult of 10
    y = elem_size * fields_y  # mult of 10

    window = pg.display.set_mode((x, y), )  #flags=pg.FULLSCREEN)
    pg.display.set_caption("Xepa")

    map = Map(fields_x, fields_y, window, elem_size)

    redraw_house = True
    draw_character = False

    counter = 0
    h = 0

while True:

    # display main screen and let user choose mode (atm Play/Credits)

    if mode == "mainscreen":

        # event handling
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # window handling
        mainscreen = pg.display.set_mode((screen_w, screen_h))
        pg.display.set_caption("nAme;Rain - Mainscreen")

        main_background_img = pg.image.load("main_background.jpg")
        main_background_img = pg.transform.scale(main_background_img, (screen_w, screen_h))
        main_background_img = main_background_img.convert()

        mainscreen.blit(main_background_img, (0, 0))

        def button_fkt():
            print("Click me harder!")
            global mode
            mode = "test"
        btn = Button([int(0.2 * screen_w), int(0.069 * screen_h)], name="Button 1", color=(0, 50, 201), \
                     action=button_fkt, text="Play")
        mainscreen.blit(btn.surf, (screen_w/2, screen_h/2))

        pg.display.update()

    elif mode == "test":

        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == ord("n"):
                    redraw_house = True

            if event.type == pg.KEYDOWN:
                if event.key == ord("p"):
                    draw_character = True

            if event.type == pg.KEYDOWN:
                if event.key == ord("c"):
                    map.clear()
                    window.fill((23, 157, 0))
                    map.draw_map()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    x += elem_size
                    window = pg.display.set_mode((x, y))
                    map.draw_map()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    y += elem_size
                    window = pg.display.set_mode((x, y))
                    map.draw_map()

            if event.type == pg.KEYUP:
                if event.key == ord("n"):
                    redraw_house = False

            # apply changes to game state

            # draw changes to screen
            if redraw_house:
                window.fill((23, 157, 0))

                for i in range(5):

                    h = SimpleHouse(name=("Simple house " + str(counter)), obj_type="default", \
                                    pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])

                    # while there is a house (to add) and it does not fit and you did not try 100 times yet generate a new one
                    limit = 0
                    while h != 0 and map.add_object(h, border_size=1) != 1 and limit < 100:
                        h = SimpleHouse(name=("Simple house " + str(counter)), obj_type="default", \
                                        pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])
                        limit += 1

                    if limit >= 100:
                        print("Could not place another object")
                    else:
                        counter += 1

                bush_counter = 0
                limit = 0

                for i in range(5):

                    h = Bush(name=("Simple bush " + str(bush_counter)), obj_type="default", \
                                   pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])

                    # while there is a house (to add) and it doesn't fit and you didn't try 100 times yet generate a new one
                    limit = 0
                    while h != 0 and map.add_object(h, border_size=1) != 1 and limit < 100:
                        h = Bush(name=("Simple bush " + str(bush_counter)), obj_type="default", \
                                        pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)])
                        limit += 1

                    if limit >= 100:
                        print("Could not place another object")
                    else:
                        bush_counter += 1

                map.draw_map()
                redraw_house = False

                if debug:
                    print()

            if draw_character:

                window.fill((23, 157, 0))

                char = Character(pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)], \
                                 orientation=numpy.random.randint(0, 359), team="team_3" if \
                                 numpy.random.randint(0, 2) % 2 == 1 else "team_4", name="Character " + str(map.characters.__len__()))
                map.add_object(char)

                map.draw_map()

                matrix = map.get_vmat(map)

                for i in range(matrix[0].__len__()):
                    print()
                    for j in range(matrix[0].__len__()):
                        sys.stdout.write(str(matrix[i][j]) + " ")

                print("---"*100)

                draw_character = False

            pg.display.update()
