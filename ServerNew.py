import socket
import struct
from NewNetwork import *

'''
    TODO
        - unterscheide welches objekt ankommt
        - entscheide, was du an wen weiter schicken musst und mach das
        - bau n client der senden kann und so
'''


class MatchData:

    def __init__(self, hosting_player, board_size, game_map, points):
        self.hosting_player = hosting_player
        self.board_size = board_size
        self.game_map = game_map
        self.points = points
        

class Server:

    def __init__(self, port=5556, max_connections=5):

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(("0.0.0.0", port))
        self.serversocket.listen(max_connections)
        self.connections = []

        self.hosting_list = []
#ooooo
    def start_listening(self):
        c_sock, addr = self.serversocket.accept()
        self.connections.append(Connection(c_sock,
                                           addr,
                                           (c_sock, addr).__hash__(),
                                           ConnectionData()))

    def kill_connection(self, sock, addr):
        for con in self.connections:
            if con.identifier == (sock, addr).__hash__():
                del con

    def kill_all_connections(self):
        del self.connections
        self.connections = []

    @staticmethod
    def ip2long(ip):
        """
        Convert an IP string to long
        """
        packedip = socket.inet_aton(ip)
        return struct.unpack("!L", packedip)[0]



