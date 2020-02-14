import socket
import Data
import time
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
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((Data.serverIP, port))
        self.connection = Connection(self.clientsocket,
                                     Data.serverIP,
                                     (self.clientsocket, Data.serverIP).__hash__(),
                                     ConnectionData(),
                                     "Client")
        self.last_opp_turn_time = -1
        self.ctype_dict = {
            Data.scc["Host"]:              self._hhost,
            Data.scc["cancel hosting"]:    self._hchost,
            Data.scc["get host list"]:     self._hgetHL,
            Data.scc["hosting list"]:      self._hhlist,
            Data.scc["Join"]:              self._hjoin,
            Data.scc["char select ready"]: self._hcsrdy,
            Data.scc["Turn"]:              self._hturn,
            Data.scc["control"]:           self._hcon,
            Data.scc["end game"]:          self._hendg,
            Data.scc["game begins"]:       self._hgbegi
        }

    def kill_connection(self):
        self.connection.kill_connection()

    # ----------------------------------------------------------------------------------------

    # TODO Do we actually need this if we have no receive loop???

    def _hhost(self):
        print("Warning! Client received 'HOST' message!")

    def _hchost(self):
        print("Warning! Client received 'CANCEL HOST' message!")

    def _hgetHL(self):
        print("Warning! Client received 'GET HOST LIST' message! He is not the one holding it though ...")

    def _hjoin(self):
        print("Warning! Client received 'JOIN' message! You cannot directly join a client game.")

    def _hcsrdy(self):
        print("Warning! Client received 'CHAR SELECT READY' message!")

    def _hturn(self):
        # handle and apply turn to local game state
        # but only if the client asked for the turn to be sent, else something went wrong
        # TODO
        pass

    def _hcon(self, msg):
        pass

    def _hendg(self):
        # TODO handle game end
        pass

    def _hgbegi(self):
        # TODO handle game begin
        pass

    def _hhlist(self):
        # handle incoming hosting list
        pass
        # TODO

    # ----------------------------------------------------------------------------------------

    # matchmaking

    def host_game(self, name, game_map, points):

        # send relevant data to the server
        self.connection.send(ctype=Data.scc["host"], msg=(name, game_map, points))

    def get_hosting_list(self):
        self.connection.send(ctype=Data.scc["get host list"], msg="")

    def join(self, name):
        self.connection.send(ctype=Data.scc["join"], msg=name)

    def cancel_hosting(self):  # TODO this has to be called from game logic if you are not ready any more
        self.connection.send(ctype=Data.scc["cancel hosting"], msg="")

    def send_char_select_ready(self, ready, team):
        # this will send until server confirms that he has received it
        self.connection.send(ctype=Data.scc["char select ready"], msg=(ready, team))
        # afterwards you we can check for game begin in our inbox
        self._check_for_game_begin()

    def _check_for_game_begin(self):  # TODO this has to be called each frame from game logic while client char select is ready
        ctype, msg = self.connection.get_last_control_type_and_msg()
        if ctype == "game begin":
            return msg
        else:
            return None

    def send_turn(self, turn):
        self.connection.send(ctype=Data.scc["turn"], msg=(turn, current_milli_time()))

    def send_control(self, msg):
        self.connection.send(ctype=Data.scc["control"], msg=msg)

    def get_turn(self):  # TODO this has to be called from main loop each frame while you are awaiting an opponent turn
        self.connection.send(ctype=Data.scc["send turn"], msg="")
        # now wait for turn msg in inbox
        ctype, msg = self.connection.get_last_control_type_and_msg()
        if ctype == Data.scc["turn"]:
            turn, turn_time = msg
            if self.last_opp_turn_time != turn_time:  # turn is new
                self.last_opp_turn_time = turn_time
                return turn
            else:
                return None
        else:
            return None


