import _thread as th
import time
import pickle
import copy
import hashlib
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

magic_number = 5 + len("received message with hash: ") + 40


class ConnectionData:

    def __init__(self, rec_buffer=[], send_buffer=[]):

        if send_buffer is None:
            send_buffer = []
        self.rec_buffer = rec_buffer            # holds list of things that were received over this connection
                                                # TODO is emptied every server iteration
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

        self.old_ctype_msg = {"old_ctype": None, "old_msg": None,
                              "very_old_ctype": None, "very_old_msg": None}

        self.unwrap_as_obj = [Data.scc["Turn"],
                              Data.scc["hosting list"],
                              Data.scc["char select ready"],
                              Data.scc["Host"],
                              Data.scc["game begins"]]
        self.unwrap_as_str = [Data.scc["control"], Data.scc["close connection"]]

        try:
            th.start_new_thread(self.receive_bytes, ())
            if self.role == "Server":
                print("Connection from {} to {} established successfully!".format(target_addr, self.role))
            else:
                print("Connection from {} to server at {} established successfully!".format(self.role, target_addr))
        except Exception as e:
            print("Starting new thread to receive bytes failed by {}, error:\n{}".format(self.role, e))

    def kill_connection(self):

        # tell listening thread to stop
        self.connection_alive = False

        # wait for it to recognize the stop (not necessary anymore), was time.sleep(2)

        # now kill the socket (listening should be dead)
        self.target_socket.shutdown(socket.SHUT_RDWR)
        self.target_socket.close()

    def receive_bytes(self, size=2048):  # first 5 bytes of the msg are control bytes defined in Data.py
        try:
            buf = b''
            while True:
                if self.connection_alive:
                    last_rec = self.target_socket.recv(size)
                    if len(last_rec) < size:  # last piece of msg
                        buf += last_rec
                        self.data.rec_buffer.append(buf)
                        self.data.rec_log.append(buf)
                        if len(buf) > magic_number:  # len of 5 control bytes and "Received message with hash: ..." with 20 digits hash as ...
                            self._send_rec_confirmation(buf)
                        buf = b''
                    elif len(last_rec) == size and last_rec[-5:] == b'XXXXX':
                        # msg is exactly size long
                        self.data.rec_buffer.append(buf)
                        self.data.rec_log.append(buf)
                        if len(buf) > magic_number:  # len of 5 control bytes and "Received message with hash: ..." with 20 digits hash as ...
                            self._send_rec_confirmation(buf)
                        buf = b''
                    elif len(last_rec) == size:  # kleben
                        # if len == 2048 and not end in XXXXX
                        buf += last_rec
                    else:
                        print("Something in receive went wrong")
                    time.sleep(0.5)
                else:
                    # just return, that should kill the thread too
                    return
                    # th.exit_thread()
        except Exception as e:
            print("Connection alive:", self.connection_alive)
            print("Receiving bytes by the {} failed with exception:\n{}".format(self.role, e))

    def unwrap(self, buf):  # gets in put buffer without scc but with XXXXX
        if buf[:5] in self.unwrap_as_obj:
            return self.bytes_to_object(buf[5:-5])
        elif buf[:5] in self.unwrap_as_str:
            return self.bytes_to_string(buf[5:-5])
        else:
            print("Warning! Message unwrapping type is not defined in client! {}".format(buf[:5]))
            return buf

    @staticmethod
    def get_control_type(msg):
        return msg[0:5]

    def get_last_control_type_and_msg(self):
        # overwrite pre last return with last return
        self.old_ctype_msg["very_old_ctype"] = self.old_ctype_msg["old_ctype"]
        self.old_ctype_msg["very_old_msg"] = self.old_ctype_msg["old_msg"]
        self.old_ctype_msg["old_ctype"] = Connection.get_control_type(self._get_last_rec())
        self.old_ctype_msg["old_msg"] = self.unwrap(self._get_last_rec())

        return Connection.get_control_type(self._get_last_rec()), \
               self.unwrap(self._get_last_rec())

    def _get_last_rec(self):
        return self.data.rec_buffer[-1] if len(self.data.rec_buffer) > 0 else b'undef'

    # use with caution as this could get long
    def get_rec_log(self):
        return copy.deepcopy(self.data.rec_log)

    def _send_rec_confirmation(self, rec_msg):
        self._send_bytes("Received message with hash: {}".format(hashlib.sha1(rec_msg).hexdigest()).encode("UTF-8"))

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

        if len(msg) <= magic_number:  # should not come to use
            # send without confirm
            self._send_bytes(msg_bytes=msg)
            if msg[:5] != b'close':
                print("WARNING: message length is smaller than {}, it will not get confirmed by the server!".
                      format(magic_number))
            return

        confirmation_received = False
        msg_hash = -1
        try:
            msg_hash = hashlib.sha1(msg).hexdigest()  # TODO see above
        except TypeError:
            print("Message is not hashable, failed to send by {}".format(self.role))

        # listen for confirm
        def _check_for_confirm():
            while True:
                nonlocal confirmation_received

                if self.data.rec_log[self.data.confirmation_search_index:].\
                        __contains__("Received message with hash: {}".format(msg_hash).encode("UTF-8")):
                    confirmation_received = True
                    self.data.confirmation_search_index = self.data.rec_log.index("Received message with hash: {}".
                                                                                  format(msg_hash).encode("utf-8")) + 1
                    return
                time.sleep(1)

        try:
            self.target_socket.send(msg)
            time.sleep(1)
        except Exception as e:
            print(e)

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
