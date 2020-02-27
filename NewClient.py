import Data
import time
import queue
import sys
from NewNetwork import *

# THE SERVER ONLY ANSWERS; IF THE CLIENT DOES NOT ASK HE WILL GET NOTHING

# ALWAYS ONLY ASK FOR 1 THING AT A TIME


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
            th.start_new_thread(self.empty_send_q, ())
            self.last_opp_turn_time = -1
            self.send_q = queue.Queue()
            self.live_data = {"hosting_list":   [],
                              "map":            None,
                              "in_game":        False,
                              "game_begin":     None,
                              "last_opp_turn":  None}

        except Exception as e:
            print("\nClient failed to connect to server with exception:\n\n\t{}".format(e).upper())
            sys.exit()

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
        # self.connection.send(Data.scc["Host"], (name, game_map, points))

    def join(self, name):
        # client already gets map here in game_data object
        self.send_q.put((Data.scc["Join"], name))
        # self.connection.send(Data.scc["Join"], name)

    def cancel_hosting(self):  # TODO this has to be called from game logic if you are not ready any more
        self.send_q.put((Data.scc["cancel hosting"], ""))
        # th.start_new_thread(self.connection.send, tuple([Data.scc["cancel hosting"], ""]))

    def send_char_select_ready(self, ready, team):
        # this will send until server confirms that he has received it
        self.send_q.put((Data.scc["char select ready"], (ready, team)))
        # self.connection.send(Data.scc["char select ready"], (ready, team))

        # afterwards you we can check for game begin in our inbox
        self._check_for_game_begin()

    def send_turn(self, turn):
        self.send_q.put((Data.scc["turn"], (turn, current_milli_time())))
        # self.connection.send(Data.scc["turn"], (turn, current_milli_time()))

    def send_control(self, msg):
        self.send_q.put((Data.scc["control"], msg))
        # self.connection.send(Data.scc["control"], msg)

    # -------------- gets ------------------------------

    # get hosting list (tell server to start sending)
    def get_hosting_list_from_server(self, b=True):
        """
        Tells server whether to send hosting list every x seconds form now on, should be called once from init
        :param b: should he send it or not?
        :return: most up to date hosting list object
        """

        self.send_q.put((Data.scc["get host list"], str(b)))
        # self.connection.send(Data.scc["get host list"], str(var))

    # get hosting list
    def get_hosting_list(self):
        # update the live data
        th.start_new_thread(self._get_hosting_list, ())
        # no need to tell the server to send, he does so anyway every 2 sec
        # return the current hosting list
        return self.live_data["hosting_list"]

    def _get_hosting_list(self):
        """
        checks incoming messages for host lists and fills live data if any hosting list is there
        :return:
        """
        # TODO guck dass der die hosting list auch echt bekommt, vielleicht verpasst er sie auch weil er immer nur das
        # TODO zuletzt gesendete element bekommt

        while True:
            if self.connection.new_msg_sent():
                ctype, msg = self.connection.get_last_control_type_and_msg()
                if ctype == Data.scc["hosting list"]:
                    self.live_data["hosting_list"] = msg
                    return
            else:
                time.sleep(0.1)  # TODO maybe make this faster?

    # get join stat (in game or not)
    def get_join_stat(self):  # returns true if the server thinks the client is in game, false otherwise
        th.start_new_thread(self._get_join_stat, ())
        return self.live_data["in_game"]

    def _get_join_stat(self):

        self.send_q.put((Data.scc["control"], "get in game stat"))

        while True:
            if self.connection.new_msg_sent():
                ctype, msg = self.connection.get_last_control_type_and_msg()
                if ctype == Data.scc["control"]:
                    self.live_data["in_game"] = True if (msg == "yes") else False
                    return
            else:
                time.sleep(0.1)

    # check for game begin
    def check_for_game_begin(self):  # server sends this automatically
        th.start_new_thread(self._check_for_game_begin, ())
        return self.live_data["game_begin"]

    def _check_for_game_begin(self):
        # TODO this has to be called from game logic while client char select is ready
        # TODO but PLEASE not every frame, else the spam would be real

        while True:
            if self.connection.new_msg_sent():
                ctype, msg = self.connection.get_last_control_type_and_msg()
                if ctype == Data.scc["game begin"]:
                    self.live_data["game_begin"] = msg
                    return
            else:
                time.sleep(0.1)

    # get turn
    def get_turn(self):
        # TODO this has to be called from main loop each frame while you are awaiting an opponent turn
        # TODO maybe call this every 1 or 3 sec from main loop
        th.start_new_thread(self._get_turn, ())
        return self.live_data["last_opp_turn"]

    def _get_turn(self):

        self.send_q.put((Data.scc["send turn"], ""))

        while True:
            if self.connection.new_msg_sent():
                ctype, msg = self.connection.get_last_control_type_and_msg()
                if ctype == Data.scc["Turn"]:
                    turn, turn_time = msg
                    if self.last_opp_turn_time != turn_time:  # turn is new
                        self.last_opp_turn_time = turn_time
                        self.live_data["last_opp_turn"] = turn
                        return
                else:
                    print("Something in _get_turn went wrong, wrong message type was sent by server")
            else:
                time.sleep(0.1)

    # ----------------- empty send queue -----------------------

    def empty_send_q(self):
        while True:
            ctype, msg = self.send_q.get()
            self.connection.send(ctype, msg)
