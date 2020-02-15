import _thread as th
import time
import pickle
import copy
import Data
import socket

'''
Important note:

The server holds a serversocket only to accept incoming connections from clients. Once the connection is established,
he moves on to communicate with the client over the clients socket returned by accept().

The client however uses his own socket for communication and not just for connection establishment. So the name
"target_socket" does not quiet hold for the client, because the socket over which the communication is made is actually
his own socket and NOT the serversocket of the server object.

'''

# TODO reformulate the debug messages with above note in mind


class ConnectionData:

    def __init__(self, rec_buffer=[], send_buffer=[]):

        if send_buffer is None:
            send_buffer = []
        self.rec_buffer = rec_buffer            # holds list of things that were received over this connection
                                                # is emptied every server iteration
        self.rec_log = []
        self.send_buffer = send_buffer
        self.confirmation_search_index = 0


class Connection:

    # TODO: add security by replacing __hash__ with HMAC
    # https://docs.python.org/3/library/pickle.html
    # https://docs.python.org/3/library/hmac.html#module-hmac

    def __init__(self, sock, target_addr, ident, data, role):
        self.target_socket = sock
        self.target_addr = target_addr
        self.ident = ident              # hash from (socket, addr)
        self.data = data
        self.role = role
        self.connection_alive = True

        self.needs_unwrapping = [Data.scc["Turn"],
                                 Data.scc["hosting list"],
                                 Data.scc["char select ready"],
                                 Data.scc["Host"],
                                 Data.scc["game begins"]]

        try:
            th.start_new_thread(self.receive_bytes, ())
            if self.role == "Server":
                print("Connection from {} to {} established successfully!".format(target_addr, self.role))
            else:
                print("Connection from {} to server at {} established successfully!".format(self.role, target_addr))
        except Exception as e:
            print("Starting new thread to receive bytes failed by {}, error:\n{}".format(self.role, e))

    def kill_connection(self):

        self.connection_alive = False
        self.target_socket.shutdown(socket.SHUT_RDWR)
        self.target_socket.close()

    def receive_bytes(self, size=2048):  # first 5 bytes of the msg are control bytes defined in Data.py
        try:
            buf = b''
            while True:
                if self.connection_alive:
                    last_rec = self.target_socket.recv(size)

                    if last_rec[-5:] == b'XXXXX':
                        self.data.rec_buffer.append(buf)
                        self.data.rec_log.append(buf)
                        if len(buf) > 53:  # len of 5 control bytes and "Received message with hash: ..." with 20 digits hash as ...
                            self._send_rec_confirmation(buf)
                        buf = b''
                    else:
                        buf += last_rec

                else:
                    th.exit_thread()
        except Exception as e:
            print("Receiving bytes by the {} failed with exception:".format(self.role))
            print(e)

    def unwrap(self, buf):
        return self.bytes_to_object(buf[5:]) if buf[:5] in self.needs_unwrapping else buf

    @staticmethod
    def get_control_type(msg):
        return msg[0:5]

    def get_last_control_type_and_msg(self):
        return Connection.get_control_type(self.get_last_rec()), \
               self.unwrap(self.get_last_rec()[5:])

    def get_last_rec(self):
        return self.data.rec_buffer[-1] if len(self.data.rec_buffer) > 0 else b'undef'

    # use with caution as this could get long
    def get_rec_log(self):
        return copy.deepcopy(self.data.rec_log)

    def _send_rec_confirmation(self, rec_msg):
        self._send_bytes("Received message with hash: {}".format(rec_msg.__hash__()).encode("UTF-8"))

    # go for this if you want to send something
    def send(self, ctype, msg):  # control type and message to send, msg can be bytes or object
        _msg = ctype + Connection.prep(msg) + b'XXXXX'
        self._send_bytes_conf(_msg)  # should this run in a separated thread as it blocks while waiting for confirm?
                                     # no, as only the "send" part of the connection blocks

    def _send_bytes(self, msg_bytes):
        try:
            self.target_socket.send(msg_bytes)
            self.data.send_buffer.append(msg_bytes)
        except Exception as e:
            print("Sending bytes to {} by {} failed. Data to send: {}\n Error:\n{}".
                  format(self.target_addr, self.role, msg_bytes, e))

    def _send_bytes_conf(self, msg):

        if len(msg) <= 53:  # should not come to use
            self._send_bytes(msg_bytes=msg)
            print("WARNING: message len smaller than 53")
            return

        confirmation_received = False
        msg_hash = -1
        try:
            msg_hash = msg.__hash__()  # TODO see above
        except TypeError:
            print("Message is not hashable, failed to send by {}".format(self.role))

        # listen for confirm
        def _check_for_confirm():
            nonlocal confirmation_received
            if self.data.rec_log[self.data.confirmation_search_index:].\
                    __contains__("Received message with hash: {}".format(msg_hash)):
                confirmation_received = True
                self.data.confirmation_search_index = self.data.rec_log.index("Received msg with hash {}".
                                                                              format(msg_hash)) + 1
        th.start_new_thread(_check_for_confirm, ())

        # send until receiving was confirmed
        while not confirmation_received:
            self.target_socket.send(msg)
            time.sleep(3)

    @staticmethod
    def prep(to_send):
        # TODO check if actual strings get pickled (they should not)

        # TODO make sure things do not get pickled twice!!!
        try:
            if isinstance(to_send, type("a")):
                return to_send.encode("UTF-8")
            else:
                return Connection.object_to_bytes(to_send)
        except Exception as e:
            print("Could not convert the message '{}' to bytes, error:\n{}".format(to_send, e))

    @staticmethod
    def object_to_bytes(obj):
        if len(pickle.dumps(obj)) > 48:
            return pickle.dumps(obj)
        else:
            return pickle.dumps(obj) + (48-len(pickle.dumps(obj)))*b'\x00'

    @staticmethod
    def bytes_to_object(_bytes):
        return pickle.loads(_bytes)

    @staticmethod
    def bytes_to_string(_bytes):
        return _bytes.decode("UTF-8")
