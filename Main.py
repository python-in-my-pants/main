# encoding: UTF-8

import pygame as pg
from pygame.locals import *
from skimage.draw import line_aa
from threading import Timer
import numpy as np
import sys
import pickle
import time

from network import *
from Game_objects import *
from GUI import *
from Data import *
from Map import *
from Characters import Character

char_amount = 0
elem_size = 25
debug = True

pg.init()
mode = "mainscreen"
changed = True
redraw = True

# client / server stuff
net = Network()
role = "nobody"
teams = []
map_data = []  # holds data of map received from server PLUS the team number you have

select = False
clock = pg.time.Clock()

# get correct screen size

mon = pg.display.Info()
screen_h = int(mon.current_h)#-3*elem_size
screen_w = int(mon.current_w/2)#-3*elem_size

#  --------------------------------------------------------------------------------------------

if True:
    fields_x = 30  # width
    fields_y = 30  # height

    elem_size = int(screen_w/fields_x) if int(screen_w/fields_x) < int(screen_h/fields_y) else int(screen_h/fields_y)

    x = elem_size * fields_x  # mult of 10
    y = elem_size * fields_y  # mult of 10

#  --------------------------------------------------------------------------------------------------
while True:
    # display main screen and let user choose mode (atm Play/Credits)
    if mode == "mainscreen":

        if changed:  # set changed false at the end

            #size = [1650, 928]  # [mon.current_w-100, mon.current_h-100]

            main_background_img = pg.image.load("assets/108.gif")  # "assets/main_background.jpg")

            size = list(main_background_img.get_size())
            size[0] = size[0] * 5
            size[1] = size[1] * 5

            # window handling
            mainscreen = pg.display.set_mode(size)
            pg.display.set_caption("nAme;Rain - Mainscreen")

            main_background_img = pg.transform.scale(main_background_img, (size[0], size[1]))
            main_background_img = main_background_img.convert()

            mainscreen.blit(main_background_img, (0, 0))

            buttons = []

            # set up GUI

            def button_fkt():

                # print("Click me harder!")
                global mode
                global changed

                pg.mixer.music.load("assets/ass.mp3")
                pg.mixer.music.play(0)

                mode = "test"  # if changing mode also change "changed"
                changed = True

            '''btn = Button([int(0.2 * size[0]), int(0.069 * size[1])], \
                         pos=[size[0]/2 - int(0.2 * size[0])/2, size[1]/2 - int(0.069 * size[1])/2], name="Button 1", \
                         color=(0, 50, 201), action=button_fkt, text="Play")'''
            btn = Button([int(0.2 * size[0]), int(0.069 * size[1])],
                         pos=[size[0]/2 - int(0.2 * size[0])/2, size[1]/2 - int(0.069 * size[1])/2 + 200],
                         name="Button 1", img="assets/blue_button_menu.jpg", action=button_fkt, text="Play")

            mainscreen.blit(btn.surf, btn.pos)
            buttons.append(btn)

            surface = mainscreen

            changed = False

        # event handling
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()
                print(p)
                for button in buttons:
                    print(button.pos)
                    if button.is_focused(p):
                        redraw = True
                        button.action()

        if redraw or changed:
            pg.display.update()
            redraw = False

        continue

    # just for testing stuff
    elif mode == "test":

        # "changed" is true, if you are new in this window mode, then change
        # set up all visible stuff and set vars for drawing map contents later on
        if changed:

            buttons.clear()

            fields_x = 30  # width
            fields_y = 30  # height

            elem_size = int(screen_w / fields_x) if int(screen_w / fields_x) < int(screen_h / fields_y) else int(
                screen_h / fields_y)

            x = elem_size * fields_x  # mult of 10
            y = elem_size * fields_y  # mult of 10
            gui_overhead = int((1/3) * (x if x < y else y))

            map_window = pg.Surface((x, y))
            window = pg.display.set_mode((x + 2 * gui_overhead, y))  # flags=pgFULLSCREEN)
            window.fill((0, 0, 0))
            pg.display.set_caption("Xepa")

            map = Map(fields_x, fields_y, map_window, elem_size)

            redraw_house = True
            draw_character = True
            #global select
            select = False

            counter = 0
            h = 0

            def selecter_mode():
                global select
                select = True
                global selected_char
                global selected_button
                selected_char = get_selected_char(pg.mouse.get_pos())
                selected_button = get_selected_button(pg.mouse.get_pos())

            def get_selected_char(mouse_pos):  # TODO: every 10th character or so has its button like 10 field underneath him
                for ch in map.characters:
                    p = pg.mouse.get_pos()
                    if (int(((p[0]) - gui_overhead) / elem_size)) == map.objects[ch].pos[0] and \
                       (int(p[1] / elem_size)) == map.objects[ch].pos[1]:
                        boi = map.objects[ch]
                        for chari in map.characters:
                            map.objects[chari].is_selected = False
                        boi.is_selected = True

                        return boi

            def get_selected_button(mouse_pos):
                for bt in buttons:
                    p = pg.mouse.get_pos()
                    if bt.is_focused(p):
                        return bt

            changed = False

        # --------------------------------------------------------------------------------------------------------------
        # handle input events
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

            if event.type == pg.MOUSEBUTTONDOWN:
                p = pg.mouse.get_pos()
                print(p)
                for button in buttons:
                    print(button.pos)
                    if button.is_focused(p):
                        redraw = True
                        button.action()

            if event.type == pg.KEYDOWN:
                if event.key == ord("c"):
                    map.clear()
                    window.fill((23, 157, 0))
                    changed = True
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

            if event.type == pg.KEYDOWN:
                if event.key == ord("q"):
                    print("Q")
                    net.send_data(map.get_map())

            if event.type == pg.KEYDOWN:
                if event.key == ord("e"):
                    print("E")
                    ret = net.receive_data()
                    print(ret)

            # TODO BOI
            if select:
                if event.type == pg.KEYDOWN:
                    if event.key == ord("w"):
                        print("W")
                        if map.movement_possible(selected_char, [selected_char.pos[0], selected_char.pos[1] - 1]):
                            selected_char.pos[1] -= 1
                            selected_button.pos[1] -= elem_size

                if event.type == pg.KEYDOWN:
                    if event.key == ord("s"):
                        print("S")
                        if map.movement_possible(selected_char, [selected_char.pos[0], selected_char.pos[1]+1]):
                            selected_char.pos[1] += 1
                            selected_button.pos[1] += elem_size

                if event.type == pg.KEYDOWN:
                    if event.key == ord("a"):
                        print("A")
                        if map.movement_possible(selected_char, [selected_char.pos[0] - 1, selected_char.pos[1]]):
                            selected_char.pos[0] -= 1
                            selected_button.pos[0] -= elem_size

                if event.type == pg.KEYDOWN:
                    if event.key == ord("d"):
                        print("D")
                        if map.movement_possible(selected_char, [selected_char.pos[0] + 1, selected_char.pos[1]]):
                            selected_char.pos[0] += 1
                            selected_button.pos[0] += elem_size

                if event.type == pg.MOUSEBUTTONDOWN:
                    p = pg.mouse.get_pos()
                    checkBtn = 0
                    for button in buttons:
                        if button.is_focused(p):
                            checkBtn += 1
                    if checkBtn == 0:
                        select = False
                        for chari in map.characters:
                            map.objects[chari].is_selected = False

                map_window.fill((23, 157, 0))
                map.draw_map()
                window.blit(map_window, (gui_overhead, 0))
                pg.display.update()
            # apply changes to game state

        # --------------------------------------------------------------------------------------------------------------
        # draw changes to screen
        if redraw_house:

            map_window.fill((23, 157, 0))

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

        if draw_character:

            map_window.fill((23, 157, 0))

            char = Character(pos=[numpy.random.randint(0, fields_x), numpy.random.randint(0, fields_y)], \
                             orientation=numpy.random.randint(0, 359), team="team_3",
                             name="Character " + str(map.characters.__len__()))

            map.add_object(char)
            map.draw_map()

            charBtn = Button(dim=[elem_size, elem_size],
                             pos=[(char.get_pos(0))*elem_size + gui_overhead, char.get_pos(1)*elem_size],
                             name="CharB " + str(map.characters.__len__()),
                             img="assets/roter_rand.jpg",
                             action=selecter_mode,
                             text="")

            # some comment to commit

            buttons.append(charBtn)
            window.blit(charBtn.surf, charBtn.pos)

            print("char pos: " + str(char.pos[0]*elem_size + gui_overhead) + " " + str(char.pos[1]*elem_size))
            print("btn pos: " + str(charBtn.pos))

            matrix = map.get_vmat(map)
            '''
            for i in range(matrix[0].__len__()):
                print()
                for j in range(matrix[0].__len__()):
                    sys.stdout.write(str(matrix[i][j]) + " ")
                print("---"*100)
            '''

        if redraw_house or changed:
            redraw_house = False
            window.blit(map_window, (gui_overhead, 0))
            pg.display.update()

        if draw_character or changed:
            draw_character = False
            window.blit(map_window, (gui_overhead, 0))
            pg.display.update()

        if redraw or changed:
            pg.display.update()
            redraw = False

        #if map.characters.__len__() > 1:
          #  map.objects[map.characters[0]].shoot(map.objects[map.characters[1]], 10, 0)
          #  print("shoot me senpai")

    elif mode == "connection_setup":

        if changed:  # set changed false at the end

            # size = [1650, 928]  # [mon.current_w-100, mon.current_h-100]

            main_background_img = pg.image.load("assets/108.gif")  # "main_background.jpg")

            size = list(main_background_img.get_size())
            size[0] = size[0] * 5
            size[1] = size[1] * 5

            # window handling
            connect_screen = pg.display.set_mode(size)
            pg.display.set_caption("nAme;Rain - Verbindungskonfiguration ...")

            main_background_img = pg.transform.scale(main_background_img, (size[0], size[1]))
            main_background_img = main_background_img.convert()

            connect_screen.blit(main_background_img, (0, 0))

            # set up GUI

            surface = connect_screen

            changed = False

        # handle input events
        for event in pg.event.get():

            # handle events
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

        if redraw or changed:
            pg.display.update()
            redraw = False

        continue

    elif mode == "char_select":

        '''
        two cases:
        case 1: you are host
            create map 
            send it to client
        case 2: you are client
            wait for map
            create map from transmission
        
        both parties calculate army size dependent on map size           
        '''

        if changed:

            #role = get_role()  # TODO: what am I?

            if role == "host":

                # global - set only if you are the host, else get it from transm
                fields_x = 50  # width
                fields_y = 50  # height

                # user side
                # ------------------------------------------------------------------------------------------------------
                elem_size = int(screen_w / fields_x) if int(screen_w / fields_x) < int(screen_h / fields_y) else int(
                    screen_h / fields_y)

                # user side for elem_size is user side
                x = elem_size * fields_x  # mult of 10
                y = elem_size * fields_y  # mult of 10

                # user side
                gui_overhead = int((1 / 3) * (x if x < y else y))

                # all user side, for display/window is not transmitted
                map_window = pg.Surface((x, y))
                window = pg.display.set_mode((x + 2 * gui_overhead, y))  # flags=pgFULLSCREEN)
                window.fill((255, 255, 255))
                pg.display.set_caption("Xepa")

                # ------------------------------------------------------------------------------------------------------

                # build map from all data
                # user side
                map = Map(fields_x, fields_y, map_window, elem_size)

                # get global representation of map - without window but with elem size
                # TODO: for client, set clients elem_size after building map from transmitted data
                global_map = map.get_map()

                team_number = np.random.randint(0, 2)
                opp_team_number = -team_number +1

                # TODO: pickle and send to host [global map, opp team number]

                # set vars for drawing contents later on
                # TODO: are they used here at all? maybe delete
                redraw_house = True
                draw_character = True
                select = False
                counter = 0
                h = 0

            elif role == "client":

                # wait for transmission from host
                # TODO: get into wait status and receive transmission from host

                map_data = ...  # TODO: after recieving data, unpickle it into "map_data"

                # user side
                # ------------------------------------------------------------------------------------------------------
                elem_size = int(screen_w / fields_x) if int(screen_w / fields_x) < int(screen_h / fields_y) else \
                            int(screen_h / fields_y)

                # user side for elem_size is user side
                x = elem_size * fields_x  # mult of 10
                y = elem_size * fields_y  # mult of 10

                # user side
                gui_overhead = int((1 / 3) * (x if x < y else y))

                # all user side, for display/window is not transmitted
                map_window = pg.Surface((x, y))
                window = pg.display.set_mode((x + 2 * gui_overhead, y))
                window.fill((255, 255, 255))
                pg.display.set_caption("Xepa")

                # ------------------------------------------------------------------------------------------------------

                # create local map object from map_data
                '''
                lis = [self.unique_pixs,        0
                       self.objects,            1
                       self.characters,         2
                       self.size_x,             3
                       self.size_y,             4
                       team_number]             5
                '''

                map = Map(x_size=map_data[3],
                          y_size=map_data[4],
                          window=map_window,
                          elem_size=elem_size,
                          objects=map_data[1],
                          characters=map_data[2],
                          unique_pixels=map_data[0])

                team_number = map_data[5]

                # set vars for drawing contents later on
                # TODO: are they used here at all? maybe delete
                redraw_house = True
                draw_character = True
                select = False
                counter = 0
                h = 0

            else:
                print("Something went wrong assigning the role 'client/host'!")

            changed = False

        # TODO
        '''if role == "host":
            teams[team_number] = Team( ... )  # TODO: create standard guy somewhere and add him to the team here
        elif role == "client":
            teams[team_number] = Team( ... )  # TODO: as above BUT give him a different name
        else:
            print("Something went wrong assigning the role 'client/host'!")'''

        # gui for character selection goes here

        # TODO if you can select your time sometime ...

    elif mode == "game":

        # "changed" is true, if you are new in this window mode, then change
        if changed:

            buttons.clear()

            # get this from transmission of host
            fields_x = ...  # width
            fields_y = ...  # height

            elem_size = int(screen_w / fields_x) if int(screen_w / fields_x) < int(screen_h / fields_y) else int(
                screen_h / fields_y)

            x = elem_size * fields_x  # mult of 10
            y = elem_size * fields_y  # mult of 10
            gui_overhead = int((1 / 3) * (x if x < y else y))

            map_window = pg.Surface((x, y))
            window = pg.display.set_mode((x + 2 * gui_overhead, y))  # flags=pgFULLSCREEN)
            window.fill((255, 255, 255))
            pg.display.set_caption("Xepa")

            map = Map(fields_x, fields_y, map_window, elem_size)

            redraw_house = True
            draw_character = True
            select = False

            counter = 0
            h = 0

            # functions for character movement
            def selecter_mode():
                global select
                select = True
                global selected_char
                global selected_button
                selected_char = get_selected_char(pg.mouse.get_pos())
                selected_button = get_selected_button(pg.mouse.get_pos())

            def get_selected_char(mouse_pos):
                for ch in map.characters:
                    p = pg.mouse.get_pos()
                    if (int((p[0] - gui_overhead) / elem_size)) == map.objects[ch].pos[0] and \
                            (int(p[1] / elem_size)) == map.objects[ch].pos[1]:
                        boi = map.objects[ch]
                        return boi

            def get_selected_button(mouse_pos):
                for bt in buttons:
                    p = pg.mouse.get_pos()
                    if bt.is_focused(p):
                        return bt

            # don't touch this
            changed = False

        # --------------------------------------------------------------------------------------------------------------
        # win condition stuff starts here: input handling and game state updates

        time_up = False

        def time_is_up():
            global time_up
            time_up = True

        Timer(30, time_is_up).start()

        def win_condition_met():
            global map_data

            my_team_number = -1
            if role == "host":
                my_team_number = team_number
            if role == "client":
                my_team_number = map_data[5]

            for index,team in enumerate(teams):
                if index != my_team_number:
                    if not team.all_dead():
                        return False

            return True

        def lose_condition_met():
            global map_data

            my_team = []
            if role == "host":
                my_team = teams[team_number]
            if role == "client":
                my_team = teams[map_data[5]]

            if my_team.all_dead():
                print("You lose!")
                # TODO send lose to other player(s)
                return True

            return False

        while not win_condition_met() and not lose_condition_met() and not time_up:

            # handle input events
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

                if event.type == pg.MOUSEBUTTONDOWN:
                    p = pg.mouse.get_pos()
                    print(p)
                    for button in buttons:
                        print(button.pos)
                        if button.is_focused(p):
                            redraw = True
                            button.action()

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

                # TODO BOI
                if select:
                    if event.type == pg.KEYDOWN:
                        if event.key == ord("w"):
                            print("W")
                            if map.movement_possible(selected_char, [selected_char.pos[0], selected_char.pos[1] - 1]):
                                selected_char.pos[1] -= 1
                                selected_button.pos[1] -= elem_size

                    if event.type == pg.KEYDOWN:
                        if event.key == ord("s"):
                            print("S")
                            if map.movement_possible(selected_char, [selected_char.pos[0], selected_char.pos[1] + 1]):
                                selected_char.pos[1] += 1
                                selected_button.pos[1] += elem_size

                    if event.type == pg.KEYDOWN:
                        if event.key == ord("a"):
                            print("A")
                            if map.movement_possible(selected_char, [selected_char.pos[0] - 1, selected_char.pos[1]]):
                                selected_char.pos[0] -= 1
                                selected_button.pos[0] -= elem_size

                    if event.type == pg.KEYDOWN:
                        if event.key == ord("d"):
                            print("D")
                            if map.movement_possible(selected_char, [selected_char.pos[0] + 1, selected_char.pos[1]]):
                                selected_char.pos[0] += 1
                                selected_button.pos[0] += elem_size

                    if event.type == pg.MOUSEBUTTONDOWN:
                        p = pg.mouse.get_pos()
                        checkBtn = 0
                        for button in buttons:
                            if button.is_focused(p):
                                checkBtn += 1
                        if checkBtn == 0:
                            select = False
                            for chari in map.characters:
                                map.objects[chari].is_selected = False

                    '''
                    map_window.fill((23, 157, 0))
                    map.draw_map()
                    window.blit(map_window, (gui_overhead, 0))
                    pg.display.update()
                    '''
