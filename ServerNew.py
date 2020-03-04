import struct
import queue
from Data import *
from NewNetwork import *


"""
You could easily transform this into a generic client/server network framework ...
"""


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
        self.send_free = True

        self.hosting_list = dict()
        self.games = []
        self.ctype_dict = {
            scc["Host"]:              self._hhost,
            scc["cancel hosting"]:    self._hchost,
            scc["get host list"]:     self._hgetHL,
            scc["Join"]:              self._hjoin,
            scc["char select ready"]: self._hcsrdy,
            scc["get turn"]:          self._hgturn,
            scc["Turn"]:              self._hturn,
            scc["control"]:           self._hcon,
            scc["end game"]:          self._hendg,
            scc["game begins"]:       lambda x: None,
            scc["undefined"]:         self._hundef,
            scc["confirm"]:           self._hundef,
            scc["get in game stat"]:  self._hginst,
            scc["close connection"]:  self._hclose
        }
        self.needs_send_resource = [scc["get host list"],
                                    scc["char select ready"]]
        self.q = queue.Queue()

        # dictionary that maps players (sockets) to their games
        self.game_players = dict()

    # <editor-fold desc="Connection handling">
    # connection handling

    def start_listening(self):
        while True:
            c_sock, addr = self.serversocket.accept()
            self.connections.append(Connection(c_sock,
                                               addr,
                                               c_sock.getsockname(),
                                               ConnectionData(),
                                               "Server"))

    def kill_connection(self, sock):  # TODO fix reconnecting to server
        for con in self.connections:
            if con.identifier == sock.getsockname():
                self.connections.remove(con)

    def kill_all_connections(self):  # TODO works?
        for con in self.connections:
            con.kill_connection()
        self.connections = []

    @staticmethod
    def ip2long(ip):
        """
        Convert an IP string to long
        """
        packed_ip = socket.inet_aton(ip)
        return struct.unpack("!L", packed_ip)[0]
    # </editor-fold>

    # <editor-fold desc="Handle incoming msgs">
    # handle hosting
    def _hhost(self, msg, con):  # works
        name, game_map, points = msg
        match_data = MatchData(name, con.ident, game_map, points)
        if match_data not in self.hosting_list.values() and name not in self.hosting_list.keys():
            self.hosting_list[name] = match_data

    # handle cancel hosting
    def _hchost(self, msg, con):  # works

        '''
        for x in self.hosting_list:
            print(x)
            print("\t", self.hosting_list[x].name)
            print("\t", self.hosting_list[x].points)
            print("\t", self.hosting_list[x].hosting_player)
        '''

        for key, value in self.hosting_list.items():
            if value.hosting_player is con.ident:
                del self.hosting_list[key]
                break

    def _hginst(self, msg, con):

        if msg == "True":
            # start thread for sending host list to this client continuously
            send_in_game_stat = True
        elif msg == "False":
            send_in_game_stat = False
        else:
            print("Error! Something in _hginst went wrong!")
            return

        def _send_IGS():
            # send in game stat to client every 2 seconds (unconfirmed)
            if not send_in_game_stat:
                return
            con.send(scc["in game stat"], "yes" if con.ident in self.game_players else "no")
            time.sleep(2)

        self.q.put([_send_IGS, "loop"])

    # handle join
    def _hjoin(self, msg, con):
        # TODO multiple join attempts result in error as player is already in a game then and the hosted game is not
        # in the hosting list anymore
        print(self.hosting_list)
        host = Connection.bytes_to_string(msg)
        try:
            # remove host from hosting list (2 player scenario)
            match_data = self.hosting_list[host]
            del self.hosting_list[host]

            game = Game(host, con.ident)
            game.game_map = match_data.game_map
            self.games.append(game)
            self.game_players[match_data.hosting_player] = game
            self.game_players[con.ident] = game
        except Exception as e:
            print("Error! Something in _hjoin went wrong! (Player might be already in a game or hosting name is wrong)")
            print(e)

        # TODO notify host so that he can transition to next screen

    def _hgetHL(self, msg, con):  # works

        if msg == "True":
            # start thread for sending host list to this client continuously
            send_hosting_list = True
        elif msg == "False":
            send_hosting_list = False
        else:
            print("Error! Something in _hgetHL went wrong!")
            return

        def _sendHL():
            # send host list to client every 2 seconds (unconfirmed)
            if not send_hosting_list:
                return
            con.send(scc["hosting list"], self.hosting_list)
            time.sleep(2)

        self.q.put([_sendHL, "loop"])

    # game

    # handle char select ready
    def _hcsrdy(self, msg, con):
        ready, team = msg
        try:
            # check if player is in a game already (should be the case)
            game = self.game_players[con.ident]
        except KeyError:
            print("Player is not in a game, sending 'ready' failed!")
            return
        if game.host.ident == con.ident:
            # msg comes from game host
            game.host_ready = ready
            game.host_team = team
        elif game.guest.ident == con.ident:
            # msg comes from game guest
            game.guest_ready = ready
            game.guest_team = team

        if game.host_ready and game.guest_ready:
            # send game begins to both? put all chars on map??
            teams = [game.host_team, game.guest_team]
            # send final map to both players
            self.send_free = False
            game.host.send(scc["game begin"], teams)
            game.guest.send(scc["game begin"], teams)
            self.send_free = True

    def _hturn(self, msg, con):

        try:
            game = self.game_players[con.ident]
        except KeyError:
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.ident == game.host.ident:
            # set last turn and keep it until requested
            game.last_host_turn = msg
        elif con.ident == game.guest.ident:
            # set last turn and keep it until requested
            game.last_guest_turn = msg
        else:
            print("Error in handling 'Turn' message from client by server")

    def _hgturn(self, msg, con):
        try:
            game = self.game_players[con.ident]
        except KeyError:
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.ident == game.host.ident:
            # send last opponent turn
            game.host.send(scc["turn"], game.last_guest_turn)
        elif con.ident == game.guest.ident:
            game.host.send(scc["turn"], game.last_host_turn)
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
    def _hcon(self, msg, con):  # works
        if msg == "Close connection":
            print("Server is closing connection ...")
            self.connections.remove(con)
            con.kill_connection()
            del con
            return

        print("Client@{} says: \n\n\t{}\n".format(con.target_addr, msg))

    def _hclose(self, msg, con):
        print("Server is closing connection ...")
        self.connections.remove(con)
        con.kill_connection()
        del con
        return
    # </editor-fold>

    def empty_q(self):
        while True:
            try:
                # put all elements in a list
                params = self.q.get()

                # first element is a function, all succeeding elements are parameters for the function call
                if params[1] == "loop":  # if the first param is "loop" enqueue the function again after calling it
                    params[0]()
                    self.q.put([params[0], "loop"])
                else:
                    # unpack the rest of the list to use them as parameters
                    params[0](*params[1:])
            except Exception as e:
                print("Error in emptying server queue!")
                print(e)


def main_routine():

    """
    This does 3 things:
    - start a separate thread to listen to incoming connections and put them in server.connections
    - start a separate thread that empties the queue
    - put incoming messages of connections in a server.queue
    :return: nothing
    """

    server = Server()
    th.start_new_thread(server.start_listening, ())
    th.start_new_thread(server.empty_q, ())

    while True:

        # check rec buffer of all connections and handle accordingly
        for con in server.connections:
            try:

                # handle incoming messages
                if con.new_msg_sent():

                    print("-" * 30 + "\nRec log len:", con.get_rec_log_len())
                    for elem in con.get_rec_log_fast(5):
                        print("\n", elem.to_string())
                    print()

                    ctype, msg = con.get_last_control_type_and_msg()
                    server.q.put([server.ctype_dict[ctype], msg, con])

            except KeyError as e:
                print("KeyError! {}".format(e))

        time.sleep(0.005)


if __name__ == "__main__":
    main_routine()
