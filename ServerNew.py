import socket
import struct
from NewNetwork import *

'''
    TODO
        - unterscheide welches objekt ankommt
        - entscheide, was du an wen weiter schicken musst und mach das
        - bau n client der senden kann und so
'''


class MatchData:  # for hosting games

    def __init__(self, name, hosting_player, game_map, points):
        self.name = name
        self.hosting_player = hosting_player
        self.game_map = game_map
        self.points = points


class Game:  # for actual games

    def __init__(self, host, guest):
        self.host = host
        self.guest = guest
        self.last_host_turn = None
        self.last_guest_turn = None
        self.over = False
        self.host_ready = False
        self.guest_ready = False
        self.host_team = None
        self.guest_team = None
        self.game_map = None


class Server:

    def __init__(self, port=5556, max_connections=5):

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(("0.0.0.0", port))
        self.serversocket.listen(max_connections)
        self.connections = []

        self.hosting_list = dict()
        self.games = []

        self.ctype_dict = {
            Data.scc["Host"]:              self._hhost,
            Data.scc["cancel hosting"]:    self._hchost,
            Data.scc["get host list"]:     self._hgetHL,
            Data.scc["Join"]:              self._hjoin,
            Data.scc["char select ready"]: self._hcsrdy,
            Data.scc["Turn"]:              self._hturn,
            Data.scc["control"]:           self._hcon,
            Data.scc["end game"]:          self._hendg,
            Data.scc["game begins"]:       self._hgbegi,
            Data.scc["undefined"]:         self._hundef,
        }

        self.game_players = dict()

    # connection handling

    def start_listening(self):
        while True:
            c_sock, addr = self.serversocket.accept()
            self.connections.append(Connection(c_sock,
                                               addr,
                                               c_sock.getsockname(),
                                               ConnectionData(),
                                               "Server"))

    def kill_connection(self, sock):
        for con in self.connections:
            if con.identifier == sock.getsockname():
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

    ###############
    # matchmaking #
    ###############

    # handle hosting
    def _hhost(self, msg, con):
        name, game_map, points = Connection.bytes_to_object(msg)
        match_data = MatchData(name, con.target_socket, game_map, points)
        if not self.hosting_list.values().__contains__(match_data) and not self.hosting_list.keys().__contains__(name):
            self.hosting_list[name] = match_data

    # handle cancel hosting
    def _hchost(self, msg, con):  # TODO unclean, untested
        for host_elem in self.hosting_list.values():
            if host_elem.hosting_player is con.target_socket:
                del host_elem

    # handle join
    def _hjoin(self, msg, con):
        host = Connection.bytes_to_string(msg)
        # remove host from hosting list (2 player scenario)
        match_data = copy.deepcopy(self.hosting_list[host])
        del self.hosting_list[host]

        game = Game(host, con.target_socket)
        game.game_map = match_data.game_map
        self.games.append(game)
        self.game_players[host.getsockname()] = game
        self.game_players[con.getsockname()] = game

    # handle get hosting list
    def _hgetHL(self, msg, con):
        con.target_socket.send(ctype="hosting list", msg=self.hosting_list)

    # game

    # handle char select ready
    def _hcsrdy(self, msg, con):
        ready, team = Connection.bytes_to_object(msg)
        try:
            # check if player is in a game already (should be the case)
            game = self.game_players[con.target_socket.getsockname()]
        except KeyError:
            print("Player is not in a game, sending 'ready' failed!")
            return
        if game.host.getsockname() == con.target_socket.getsockname():
            # msg comes from game host
            game.host_ready = ready
            game.host_team = team
        elif game.guest.getsocketname() == con.target_socket.getsockname():
            # msg comes from game guest
            game.guest_ready = ready
            game.guest_team = team

        if game.host_ready and game.guest_ready:
            # send game begins to both? put all chars on map??
            final_map = self.combine_map(game.game_map, game.host_team, game.guest_team)
            # send final map to both players
            game.host.send(ctype=Data.scc["game begin"], msg=final_map)

    # handle game begin
    # TODO both players wait for the game begin msg of the server when they are ready
    # msg contains the final map for game start
    def _hgbegi(self, msg, con):
        pass

    # DEPRECATED
    '''
    # handle sending turn
    def _hturn_old(self, msg, con):
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
    '''

    def _hturn(self, msg, con):

        try:
            game = self.game_players[con.target_socket.getsockname()]
        except KeyError:
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.target_socket.getsockname() == game.host.getsockname():
            # set last turn and keep it until requested
            game.last_host_turn = msg
        elif con.target_socket.getsockname() == game.guest.getsockname():
            # set last turn and keep it until requested
            game.last_guest_turn = msg
        else:
            print("Error in handling 'Turn' message from client by server")

    def _hgturn(self, msg, con):
        try:
            game = self.game_players[con.target_socket.getsockname()]
        except KeyError:
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.target_socket.getsockname() == game.host.getsockname():
            # send last opponent turn
            game.host.send(ctype=Data.scc["turn"], msg=game.last_guest_turn)
        elif con.target_socket.getsockname() == game.guest.getsockname():
            game.host.send(ctype=Data.scc["turn"], msg=game.last_host_turn)
        else:
            print("Error in handling 'Get turn' request by server")

    # handle game end
    def _hendg(self, msg, con):
        print("Error! Not implemented yet!")
        ...  # TODO

    # misc

    def _hundef(self, msg, con):
        pass

    # handle sending text
    def _hcon(self, msg, con):
        if msg == "Close connection":
            print("Server is closing connection ...")
            self.connections.remove(con)
            return
        print("{} says: {}".format("Some random client", msg))

    @staticmethod
    def combine_map(_map, team1, team2):
        for char in team1:
            _map.objects[0].add_char(char)
        for char in team2:
            _map.objects[1].add_char(char)
        return _map


def main_routine():

    server = Server()
    th.start_new_thread(server.start_listening, ())
    old_ctype = old_msg = None

    while True:

        # check rec buffer of all connections and handle accordingly
        for con in server.connections:
            # TODO prevent server from handling the last msg over and over again
            # TODO so check if new msg was received on this connection after last loop
            ctype, msg = con.get_last_control_type_and_msg()
            # handle incoming messages
            if not (old_ctype == ctype and old_msg == msg):
                server.ctype_dict[ctype](msg, con)  # was con.target_socket
                old_ctype, old_msg = ctype, msg

        time.sleep(1)
        print(len(server.connections))


if __name__ == "__main__":
    main_routine()
