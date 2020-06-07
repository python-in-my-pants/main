"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer                                                                                         #
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

import queue
import sys
from NewNetwork import *
import traceback


def current_milli_time():
    return int(round(time.time() * 1000))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NetworkClient(metaclass=Singleton):

    """
    The client should not use a receive loop. It should check for information by querying the server for it when needed.
    """

    def __init__(self, port=5556):
        try:
            self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientsocket.connect((Data.serverIP, port))
            self.connection = Connection(self.clientsocket,
                                         Data.serverIP,
                                         (self.clientsocket, Data.serverIP).__hash__(),
                                         ConnectionData(),
                                         "Client")
            self.send_q = queue.Queue()
            th.start_new_thread(self.empty_send_q, ())
            self.last_opp_turn_time = -1
            self.live_data = None
            self.set_live_data()

        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewClient in line 44!")
            print("\nClient failed to connect to server with exception:\n\n\t{}".format(e).upper())
            sys.exit()

    def set_live_data(self):

        self.live_data = {"hosting_list":   {},
                          "map":            None,
                          "in_game":        False,
                          "game_begin":     None,
                          "last_opp_turn":  (None, -1)}

    def kill_connection(self):
        # (this is so that all pending sends go through) it seems we can just skip this???
        # time.sleep(3)
        # this prevents *[WinError 10038] Ein Vorgang bezog sich auf ein Objekt, das kein Socket ist*
        time.sleep(1)
        # blocks until confirm
        self.connection.send(Data.scc["close connection"], "")
        # this prevents *[WinError 10038] Ein Vorgang bezog sich auf ein Objekt, das kein Socket ist*
        time.sleep(2)
        # this kills the socket and tells the listening thread to stop
        self.connection.kill_connection()

    # matchmaking, sends

    def host_game(self, name, game_map, points):
        # send relevant data to the server
        self.send_q.put((Data.scc["Host"], (name, game_map, points)))

    def join(self, name):
        # client already gets map here in game_data object
        self.send_q.put((Data.scc["Join"], name))

    def cancel_hosting(self):  # TODO this has to be called from game logic if you are not ready any more
        self.send_q.put((Data.scc["cancel hosting"], ""))

    def send_char_select_ready(self, ready, team):  # after calling this you have to check for game begin ready
        # this will send until server confirms that he has received it
        self.send_q.put((Data.scc["char select ready"], (ready, team)))

    def send_turn(self, turn, timestamp):
        self.send_q.put((Data.scc["Turn"], (turn, timestamp)))  # current_milli_time()

    def send_endgame(self):
        self.send_q.put((Data.scc["end game"], ""))
        self.set_live_data()

    def send_control(self, msg):
        self.send_q.put((Data.scc["control"], msg))

    # -------------- gets ------------------------------

    # get hosting list (tell server to start sending)
    def get_hosting_list_from_server(self, b=True):
        """
        Tells server whether to send hosting list every x seconds form now on, should be called once from init
        :param b: should he send it or not?
        :return: most up to date hosting list object (or nothing apparently?)
        """
        self.send_q.put((Data.scc["get host list"], str(b)))

    # get hosting list
    def get_hosting_list(self):
        # get last 10 items of receive log, newest first
        log = self.connection.get_rec_log_fast(10)
        for pack in log:
            if pack.ctype == Data.scc["hosting list"]:
                p = pack.get_payload()
                self.live_data["hosting_list"] = p
                return self.live_data["hosting_list"]

    def get_in_game_stat_from_server(self, b=True):
        self.send_q.put((Data.scc["get in game stat"], str(b)))

    # get in-game-stat (in game or not)
    def get_in_game_stat(self):  # returns true if the server thinks the client is in game, false otherwise
        log = self.connection.get_rec_log_fast(10)
        for pack in log:
            try:
                if pack.ctype == Data.scc["in game stat"]:
                    self.live_data["in_game"] = True if (pack.get_payload() == "yes") else False
                    return self.live_data["in_game"]
            except Exception as e:
                print("")
                traceback.print_exc()
                print("Exception in NewClient in line 115!")
                print("Something in NetworkClients get_in_game_stat went wrong!")
                print(e)

        return self.live_data["in_game"]

    # check for game begin
    def check_for_game_begin(self):  # server sends this automatically
        log = self.connection.get_rec_log_fast(10)
        for pack in log:
            if pack.ctype == Data.scc["game begins"]:
                self.live_data["game_begin"] = pack.get_payload()
                return self.live_data["game_begin"]
        return self.live_data["game_begin"]

    def get_turn_from_server(self, bolle=True):  # does not make sense
        self.send_q.put((Data.scc["get turn"], str(bolle)))

    # get turn
    def get_turn(self):  # returns either old turn or new turn

        log = self.connection.get_rec_log_fast(10)
        for pack in log:
            if pack.ctype == Data.scc["Turn"]:
                p = pack.get_payload()
                if len(p) != 2:
                    return self.live_data["last_opp_turn"]
                turn, turn_time = p
                if self.last_opp_turn_time < turn_time:  # turn is new
                    self.last_opp_turn_time = turn_time
                    self.live_data["last_opp_turn"] = (turn, self.last_opp_turn_time)
                    return self.live_data["last_opp_turn"]

        return self.live_data["last_opp_turn"]

    # ----------------- empty send queue -----------------------

    def empty_send_q(self):
        while True:
            ctype, msg = self.send_q.get()
            self.connection.send(ctype, msg)
            time.sleep(0.2)
