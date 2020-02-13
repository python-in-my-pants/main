import socket
import Data
from NewNetwork import *

# THE SERVER ONLY ANSWERS; IF THE CLIENT DOES NOT ASK HE WILL GET NOTHING

# ALWAYS ONLY ASK FOR 1 THING AT A TIME


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
        self.ctype_dict = {
            Data.scc["host"]:              self._hhost,
            Data.scc["cancel hosting"]:    self._hchost,
            Data.scc["get host list"]:     self._hgetHL,
            Data.scc["hosting list"]:      self._hhlist,
            Data.scc["join"]:              self._hjoin,
            Data.scc["char select ready"]: self._hcsrdy,
            Data.scc["turn"]:              self._hturn,
            Data.scc["control"]:           self._hcon,
            Data.scc["end game"]:          self._hendg,
            Data.scc["game begins"]:       self._hgbegi
        }

    ''' DEPRECATED
    def client_receive_loop(self):   # TODO

        while self.connection:  # as long as the connection exists
            last_control_type, last_msg = self.connection.get_last_control_type_and_msg()
            self.ctype_dict[last_control_type](last_msg)
            time.sleep(1)
    '''

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

    def cancel_hosting(self):
        self.connection.send(ctype=Data.scc["cancel hosting"], msg="")
        # TODO stop waiting for begin msg from server

    def send_char_select_ready(self, ready, team):
        # this will send until server confirms that he has received it
        self.connection.send(ctype=Data.scc["char select ready"], msg=(ready, team))
        # afterwards you we can check for game begin in our inbox
        self._check_for_game_begin()

    def _check_for_game_begin(self):
        ctype, msg = self.connection.get_last_control_type_and_msg()
        if ctype == "game begin":
            return msg  # TODO

    def send_turn(self, turn):
        pass

    def send_control(self, msg):
        pass

    def get_turn(self):
        pass
