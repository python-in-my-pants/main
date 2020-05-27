import struct
import queue
from Data import *
from NewNetwork import *
import traceback

"""
You could easily transform this into a generic client/server network framework ...
"""


class Game:  # for actual games

    def __init__(self, host, guest):
        self.host = host
        self.guest = guest
        self.last_host_turn = None
        self.last_host_turn_time = 0
        self.last_guest_turn = None
        self.last_guest_turn_time = 0
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
        self.connections = dict()

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
        self.enqueueing_dict = dict()
        self.loop_funcs = ["_sendHL", "_send_IGS"]
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
            self.connections[addr] = (Connection(c_sock,
                                                 addr,
                                                 addr,  # c_sock.getsockname(),  # TODO
                                                 ConnectionData(),
                                                 "Server"))

    def kill_connection(self, sock):  # TODO fix reconnecting to server
        for con in list(self.connections.values()):
            if con.ident == sock.getsockname():
                list(self.connections.values()).remove(con)

        self.serversocket.close()

    def kill_all_connections(self):  # TODO
        for con in list(self.connections.values()):
            con.kill_connection()
        self.connections = dict()
        self.serversocket.close()

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
    def _hhost(self, con, msg):  # works
        try:
            name, game_map, points = msg
            match_data = MatchData(name, con.ident, game_map, points)
            if match_data not in self.hosting_list.values() and name not in self.hosting_list.keys():
                self.hosting_list[name] = match_data
        except Exception as e:
            print("Exception in ServerNew in line 109!")
            print("Handling hosting message by server failed with error:", e)

    # handle cancel hosting
    def _hchost(self, con, msg):  # works

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

    def _hginst(self, con, msg):

        if msg == "True":
            # start thread for sending host list to this client continuously
            send_in_game_stat = True
            if ("_send_IGS", con.ident) in self.enqueueing_dict and self.enqueueing_dict[("_send_IGS", con.ident)]:
                return
            for elem in list(self.q.queue):
                name, msg, _con = elem
                if name == "_send_IGS" and _con == con:
                    return
        elif msg == "False":
            self.enqueueing_dict[("_send_IGS", con.ident)] = True
            send_in_game_stat = False
            return
        else:
            print("Error! Something in _hginst went wrong!")
            return

        def _send_IGS():
            # send in game stat to client every 2 seconds (unconfirmed)
            if not send_in_game_stat:
                self.enqueueing_dict[("_send_IGS", con.ident)] = True
                return
            con.send(scc["in game stat"], "yes" if con.ident in self.game_players else "no")

        self.q.put([_send_IGS, con, "loop"])

    # handle join
    def _hjoin(self, con, msg):
        # TODO multiple join attempts result in error as player is already in a game then and the hosted game is not
        # in the hosting list anymore
        game_to_join_name = msg  # Connection.bytes_to_string(msg)
        try:
            # remove host from hosting list (2 player scenario)
            match_data = copy.deepcopy(self.hosting_list[game_to_join_name])
            self.hosting_list.pop(game_to_join_name)

            game = Game(match_data.hosting_player, con.ident)
            game.game_map = match_data.game_map

            self.games.append(game)
            self.game_players[match_data.hosting_player] = game
            self.game_players[con.ident] = game
        except Exception as e:
            print("Exception in ServerNew in line 173!")
            print("Error! Something in _hjoin went wrong! (Player might be already in a game or hosting name is wrong)")
            print(e)
            print(traceback.format_exc())

    def _hgetHL(self, con, msg):  # works

        if msg == "True":
            # start thread for sending host list to this client continuously
            send_hosting_list = True
            # if it is currently enqueueing
            if ("_sendHL", con.ident) in self.enqueueing_dict and self.enqueueing_dict[("_sendHL", con.ident)]:
                return
            # or if it is currently in the queue
            for elem in list(self.q.queue):
                name, msg, _con = elem
                if name == "_sendHL" and _con == con:
                    return
        elif msg == "False":
            self.enqueueing_dict[("_sendHL", con.ident)] = True
            send_hosting_list = False
            return
        else:
            print("Error! Something in _hgetHL went wrong!")
            return

        def _sendHL():
            # send host list to client every second (unconfirmed)
            if not send_hosting_list:
                self.enqueueing_dict[("_sendHL", con.ident)] = True
                return
            con.send(scc["hosting list"], self.hosting_list)

        self.q.put([_sendHL, con, "loop"])

    # game

    # handle char select ready
    def _hcsrdy(self, con, msg):
        ready, team = msg
        try:
            # check if player is in a game already (should be the case)
            game = self.game_players[con.ident]
        except KeyError:
            print("Exception in ServerNew in line 217!")
            print("Player is not in a game, sending 'ready' failed!")
            return
        if game.host == con.ident:
            # msg comes from game host
            game.host_ready = ready
            game.host_team = team
        elif game.guest == con.ident:
            # msg comes from game guest
            game.guest_ready = ready
            game.guest_team = team

        if game.host_ready and game.guest_ready:
            # send game begins to both? put all chars on map??
            teams = [game.host_team, game.guest_team]
            # send final map to both players
            self.connections[game.host].send(scc["game begins"], teams)
            self.connections[game.guest].send(scc["game begins"], teams)

    def _hturn(self, con, msg):  # receives turn

        try:
            game = self.game_players[con.ident]
        except KeyError:
            print("Exception in ServerNew in line 241!")
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.ident == game.host:
            # set last turn and keep it until requested
            game.last_host_turn, game.last_host_turn_time = msg
        elif con.ident == game.guest:
            # set last turn and keep it until requested
            game.last_guest_turn, game.last_guest_turn_time = msg
        else:
            print("Error in handling 'Turn' message from {} by server".format(con.ident))

    def _hgturn(self, con, msg):  # sends back turn
        try:
            game = self.game_players[con.ident]
        except KeyError:
            print("Exception in ServerNew in line 257!")
            print("Player is not in a game, receiving turn by server failed!")
            return
        if con.ident == game.host:
            # send last opponent turn
            #print("\nturn time", game.last_guest_turn_time, "\n")
            self.connections[game.host].send(scc["Turn"], (game.last_guest_turn, game.last_guest_turn_time))
        elif con.ident == game.guest:
            #print("\nturn time", game.last_host_turn_time, "\n")
            self.connections[game.guest].send(scc["Turn"], (game.last_host_turn, game.last_host_turn_time))
        else:
            print("Error in handling 'Get turn' request from {} by server".format(con.ident))

    # handle game end
    def _hendg(self, con, msg):
        print("Error! Not implemented yet!")
        ...  # TODO

    # misc
    def _hundef(self, con, msg):
        pass

    # handle sending text
    def _hcon(self, con, msg):  # works
        if msg == "Close connection":
            print("Server is closing connection ...")
            self.connections.pop(con)
            con.kill_connection()
            del con
            return

        print("Client@{} says: \n\n\t{}\n".format(con.target_addr, msg))

    def _hclose(self, con, msg):
        print("Server is closing connection ...")
        self.connections.pop(con)
        con.kill_connection()
        del con
        return
    # </editor-fold>

    def requeue(self, t, func, params):
        self.enqueueing_dict[(params[0].__name__, params[1].ident)] = True
        time.sleep(t)
        func(params)
        self.enqueueing_dict[(params[0].__name__, params[1].ident)] = False

    def empty_q(self):  # tODO stop this asshole from sending hosting list after connection dies
        while True:

            try:  # TODO change keyword "loop" to sth more distinct

                params = self.q.get()
                if not params[1].connection_alive:
                    continue

                # first element is a function, all succeeding elements are parameters for the function call
                if params[2] == "loop":  # if the first param is "loop" enqueue the function again after calling it
                    params[0]()
                    # if this function is not queueing right now
                    if (((params[0].__name__, params[1].ident) not in self.enqueueing_dict) or
                            not self.enqueueing_dict[(params[0].__name__, params[1].ident)]) and \
                            params[1].ident not in self.game_players:
                        th.start_new_thread(self.requeue,
                                            (1, self.q.put, params))
                else:
                    # unpack the rest of the list to use them as parameters
                    params[0](params[1], *params[2:])
            except Exception as e:
                print("Exception in ServerNew in line 326!")
                print("Error in emptying server queue!")
                print(e)
                print(traceback.format_exc())


def main_routine():

    """
    This does 3 things:
    - start a separate thread to listen to incoming connections and put them in server.connections
    - start a separate thread that empties the queue
    - put incoming messages of connections in a server.queue
    :return: nothing
    """

    def del_connection(con):

        # remove from connections
        if con.ident not in server.connections:
            return
        del server.connections[con.ident]

        # remove from hosting list
        for key, val in server.hosting_list.items():
            if server.hosting_list[key].hosting_player == con.ident:
                server.hosting_list.pop(key)

        # remove from game players
        for key, val in server.game_players.items():
            if server.game_players[key].hosting_player == con.ident:
                server.game_players.pop(key)

        for elem in list(server.q.queue):
            if elem[1] == con.ident:
                server.q.queue.remove(elem)

        for elem in [(name, con.ident) for name in server.loop_funcs]:
            if elem in server.enqueueing_dict:
                server.enqueueing_dict.pop(elem)

    server = None
    try:
        server = Server()
        th.start_new_thread(server.start_listening, ())
        th.start_new_thread(server.empty_q, ())

        while True:

            # check rec buffer of all connections and handle accordingly
            for con in list(server.connections.values()):
                try:

                    # if client is gone remove his stuff
                    if not con.connection_alive:
                        del_connection(con)

                    # handle incoming messages
                    if con.new_msg_sent():

                        print(str(con.ident))
                        print("-"*30 + "Rec log len:", con.get_rec_log_len())
                        for elem in con.get_rec_log_fast(5):
                            print("\n", elem.to_string())
                        print()
                        print("+++++++++++++++++++++++", server.hosting_list.keys(), "\n")

                        ctype, msg = con.get_last_control_type_and_msg()
                        server.q.put([server.ctype_dict[ctype], con, msg])

                except KeyError as e:
                    print("Exception in ServerNew in line 388!")
                    print("KeyError! {}\n".format(e))
                except RuntimeError:
                    continue
                except Exception as e:
                    print("Exception in ServerNew in line 353!")
                    print("Exception in server main loop over connections:")
                    print(e)
                    traceback.print_exc()
                    print("Killing connection ...")
                    del_connection(con)
                    con.kill_connection()
                    print("Connection killed!\n")

            time.sleep(0.005)
    except KeyboardInterrupt:
        if server:
            server.kill_all_connections()
    except Exception as e:
        print("Exception in ServerNew in line 402!")
        print("Exception in server outer main loop:")
        print(e)


if __name__ == "__main__":
    main_routine()
