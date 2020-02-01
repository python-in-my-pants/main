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

    def __init__(self, name, hosting_player, game_map, points):
        self.name = name
        self.hosting_player = hosting_player
        self.game_map = game_map
        self.points = points


class Game:

    def __init__(self, host, guest):
        self.host = host
        self.guest = guest
        self.last_host_turn = None
        self.last_guest_turn = None
        self.over = False


class Server:

    def __init__(self, port=5556, max_connections=5):

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(("0.0.0.0", port))
        self.serversocket.listen(max_connections)
        self.connections = []

        self.hosting_list = dict()
        self.games = []

        self.ctype_dict = {
            Data.iscc["host"]:              self._hhost,
            Data.iscc["cancel hosting"]:    self._hchost,
            Data.iscc["get host list"]:     self._hgetHL,
            Data.iscc["join"]:              self._hjoin,
            Data.iscc["char select ready"]: self._hcsrdy,
            Data.iscc["turn"]:              self._hturn,
            Data.iscc["control"]:           self._hcon
        }
        self.game_players = dict()

    # connection handling

    def start_listening(self):
        c_sock, addr = self.serversocket.accept()
        self.connections.append(Connection(c_sock,
                                           addr,
                                           c_sock.getsockname(), #c_sock.__hash__(),
                                           ConnectionData(),
                                           "Server"))

    def kill_connection(self, sock):
        for con in self.connections:
            if con.identifier == sock.getsockname():#(sock, addr).__hash__():
                del con

    def kill_all_connections(self):
        del self.connections
        self.connections = []

    @staticmethod
    def ip2long(ip):
        """
        Convert an IP string to long
        """
        packed_ip = socket.inet_aton(ip)
        return struct.unpack("!L", packed_ip)[0]

    # matchmaking

    # handle hosting
    def _hhost(self, msg, con):
        name, game_map, points = Connection.bytes_to_object(msg)
        match_data = MatchData(name, con, game_map, points)
        if not self.hosting_list.values().__contains__(match_data) and not self.hosting_list.keys().__contains__(name):
            self.hosting_list[name] = match_data

    # handle cancel hosting
    def _hchost(self, msg, con):  # TODO unclean, untested
        for host_elem in self.hosting_list.values():
            if host_elem.hosting_player is con:
                del host_elem

    # handle join
    def _hjoin(self, msg, con):
        host = Connection.bytes_to_string(msg)
        game = Game(host, con)
        self.games.append(game)
        self.game_players[host.getsockname()] = game
        self.game_players[con.getsockname()] = game

    # handle get hosting list
    def _hgetHL(self, msg, con):
        con.send(ctype="hosting list", msg=self.hosting_list)

    # handle char select ready
    def _hcsrdy(self, msg, con):
        try:
            game = self.game_players[con.getsockname()]
        except KeyError:
            print("Player is not in a game, sending 'ready' failed!")
            return
        if con.getsockname() == game.host.getsockname():
            # send to client
            game.guest.send(ctype=Data.scc["turn"], msg=msg)
        else:
            # send to host
            game.host.send(ctype=Data.scc["turn"], msg=msg)

    # game

    # handle sending turn
    def _hturn(self, msg, con):
        try:
            game = self.game_players[con.getsockname()]
        except KeyError:
            print("Player is not in a game, sending turn failed!")
            return
        if con.getsockname() == game.host.getsockname():
            # send to client
            game.guest.send(ctype=Data.scc["turn"], msg=msg)
        else:
            # send to host
            game.host.send(ctype=Data.scc["turn"], msg=msg)

    # misc

    # handle sending text
    @staticmethod
    def _hcon(msg, con):
        print("{} says: {}".format(con.target_addr, Connection.bytes_to_string(msg)))


def main_routine():

    server = Server()
    server.start_listening()

    while True:

        # check rec buffer of all connections and handle accordingly
        for con in server.connections:
            ctype, msg = con.get_last_control_type_and_msg()
            server.ctype_dict[ctype](msg, con.target_socket)

        time.sleep(1)
