import socket
import Data
from NewNetwork import *


class NetworkClient:

    def __init__(self, port=5556):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((Data.serverIP, port))
        self.connection = Connection(self.clientsocket,
                                     Data.serverIP,
                                     (self.clientsocket, Data.serverIP).__hash__(),
                                     ConnectionData(),
                                     "Client")

    # matchmaking

    def host_game(self, name, game_map, points):

        # send relevant data to the server
        self.connection.send(ctype=Data.scc["host"], msg=(name, game_map, points))

    def get_hosting_list(self):
        self.connection.send(ctype=Data.scc["get hosting list"], msg="")

    def join(self, name):
        self.connection.send(ctype=Data.scc["join"], msg=name)

    def cancel_hosting(self):
        self.connection.send(ctype=Data.scc["cancel hosting"], msg="")

    def char_select_ready(self, ready, team):
        self.connection.send(ctype=Data.scc["char select ready"], msg=(ready, team))