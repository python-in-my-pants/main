import socket
import Data
import time
import sys
from NewNetwork import *

# THE SERVER ONLY ANSWERS; IF THE CLIENT DOES NOT ASK HE WILL GET NOTHING

# ALWAYS ONLY ASK FOR 1 THING AT A TIME


def current_milli_time():
    return int(round(time.time() * 1000))


class NetworkClient:

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
            self.last_opp_turn_time = -1
            self.live_data = {"hosting_list": [],
                              "map": None,
                              "in_game": False,
                              "game_begin": None,
                              "last_opp_turn": None}

        except Exception as e:
            print("\nClient failed to connect to server with exception:\n\n\t{}".format(e).upper())
            sys.exit()

    def kill_connection(self):
        # (this is so that all pending sends go through) it seems we can just skip this???
        # time.sleep(3)

        # this prevents *[WinError 10038] Ein Vorgang bezog sich auf ein Objekt, das kein Socket ist*
        time.sleep(1)

        # blocks until confirm
        self.connection.send(ctype=Data.scc["close connection"], msg="")

        # this prevents *[WinError 10038] Ein Vorgang bezog sich auf ein Objekt, das kein Socket ist*
        time.sleep(2)

        # this kills the socket and tells the listening thread to stop
        self.connection.kill_connection()

    # matchmaking

    def host_game(self, name, game_map, points):

        # send relevant data to the server
        self.connection.send(Data.scc["Host"], (name, game_map, points))

    def join(self, name):
        # client already gets map here in game_data object
        self.connection.send(Data.scc["Join"], name)

    def cancel_hosting(self):  # TODO this has to be called from game logic if you are not ready any more
        self.connection.send(Data.scc["cancel hosting"], "")

    # get hosting list
    def get_hosting_list(self):
        th.start_new_thread(self._get_hosting_list, ())
        return self.live_data["hosting_list"]

    def _get_hosting_list(self):

        # check len of rec log to and tell server to send host list
        l1 = self.connection.get_rec_log_len()
        self.connection.send(Data.scc["get host list"], "")

        # wait until new message was received (hopefully the answer to get host list is not yet sent)
        while l1 == self.connection.get_rec_log_len():
            time.sleep(0.5)

        # now a new msg was sent
        ctype, msg = self.connection.get_last_control_type_and_msg()
        # as long as the data type is not a hosting list
        while ctype != Data.scc["hosting list"]:
            # wait a sec
            time.sleep(1)
            # and try again
            ctype, msg = self.connection.get_last_control_type_and_msg()

        self.live_data["hosting_list"] = msg
        return

    def get_join_stat(self):
        self._get_join_stat()
        return self.live_data["in_game"]

    def _get_join_stat(self):
        # check len of rec log and tell server to tell in game status
        l1 = self.connection.get_rec_log_len()
        self.connection.send(Data.scc["control"], "get in game stat")

        # wait until new message was received
        while l1 == self.connection.get_rec_log_len():
            time.sleep(0.5)

        # now a new msg was sent
        ctype, msg = self.connection.get_last_control_type_and_msg()
        # as long as the data type is not a hosting list
        while ctype != Data.scc["control"]:
            # wait a sec
            time.sleep(1)
            # and try again
            ctype, msg = self.connection.get_last_control_type_and_msg()

        self.live_data["in_game"] = True if (msg == "yes") else False
        return

    # check for game begin
    def check_for_game_begin(self):
        th.start_new_thread(self._check_for_game_begin, ())
        return self.live_data["game_begin"]

    def _check_for_game_begin(self):
        # TODO this has to be called from game logic while client char select is ready
        # TODO but PLEASE not every frame, else the spam would be real

        ctype, msg = self.connection.get_last_control_type_and_msg()
        while ctype != Data.scc["game begin"]:
            time.sleep(1)
        return msg

    # get turn
    def get_turn(self):
        # TODO this has to be called from main loop each frame while you are awaiting an opponent turn
        # TODO maybe call this every 1 or 3 sec from main loop
        th.start_new_thread(self._get_turn, ())
        return self.live_data["last_opp_turn"]

    def _get_turn(self):
        l1 = self.connection.get_rec_log_len()
        self.connection.send(Data.scc["send turn"], "")

        # assure that a new msg came in meanwhile
        while l1 == self.connection.get_rec_log_len():
            time.sleep(0.5)

        # now wait for turn msg in inbox
        ctype, msg = self.connection.get_last_control_type_and_msg()
        if ctype == Data.scc["Turn"]:
            turn, turn_time = msg
            if self.last_opp_turn_time != turn_time:  # turn is new
                self.last_opp_turn_time = turn_time
                self.live_data["last_opp_turn"] = turn
            else:
                print("Something in _get_turn went wrong")
                return None
        else:
            print("Something in _get_turn went wrong, wrong message type was sent by server")
            return None

    # sends
    def send_turn(self, turn):
        self.connection.send(Data.scc["turn"], (turn, current_milli_time()))

    def send_control(self, msg):
        self.connection.send(Data.scc["control"], msg)

    def send_char_select_ready(self, ready, team):
        # this will send until server confirms that he has received it
        self.connection.send(Data.scc["char select ready"], (ready, team))
        # afterwards you we can check for game begin in our inbox
        self._check_for_game_begin()
