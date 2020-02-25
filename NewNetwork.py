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

# TODO make it so that you have a control type for confirm messages that does not get confirmed itself but all other
#  messages do instead of length as control factor


def current_milli_time():
    return int(round(time.time() * 1000))


class ConnectionData:

    def __init__(self, rec_buffer=[], send_buffer=[]):

        if send_buffer is None:
            send_buffer = []
        self.rec_log = []  # TODO empty every now and then
        self.send_buffer = send_buffer
        self.confirmation_search_index = 0


class Packet:

    def __init__(self, ctype, payload, timestamp=None):
        self.ctype = ctype
        self._payload = payload
        timestamp_padding = 30
        if timestamp:
            if isinstance(timestamp, bytes) and len(timestamp) == timestamp_padding:
                self.timestamp = timestamp
        else:
            t = str(current_milli_time())
            self.timestamp = ("0"*(timestamp_padding-len(t)) + t).encode("UTF-8")  # zero padding to 30 symbols
        # TODO maybe "get_bytes()" to remove redundancy?
        self.bytes = self.ctype + self.timestamp + self._payload + Data.scc["message end"]
        self.bytes_hash = hashlib.sha1(self.bytes).hexdigest().encode("UTF-8")  # this is a string a byte array
        self.confirmed = False

    @classmethod
    def from_buffer(cls, buffer):
        """Construct a packet from a byte array"""
        return cls(buffer[0:5], buffer[35:-5], timestamp=buffer[5:35])

    def get_payload(self):  # TODO look after data types of confirm message!!!
        """returns unwrapped payload, object or string or byte array if no unwrapping type was defined in Data.py"""
        if self.ctype in Data.unwrap_as_str:
            return self._payload.decode("UTF-8")
        if self.ctype in Data.unwrap_as_obj:
            return pickle.loads(self._payload)
        else:
            print("Warning! Unwrapping type for", self.ctype.decode("UTF-8"), "is not defined!")
            return self._payload

    def to_string(self):
        return "Ctype:\t\t{}\nTimestamp:\t{}\nPayload:\t{}...\nHash:\t\t{}".\
            format(self.ctype, self.timestamp, self._payload[-40:], self.bytes_hash)


class Connection:

    # TODO: add security by replacing sha1 with HMAC
    # https://docs.python.org/3/library/pickle.html
    # https://docs.python.org/3/library/hmac.html#module-hmac

    def __init__(self, sock, target_addr, ident, data, role):
        self.target_socket = sock
        self.target_addr = target_addr
        self.ident = ident              # hash from (socket, addr)
        self.data = data
        self.role = role
        self.connection_alive = True
        self.old_rec_len = -1

        self.last_chkd_msg = None

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
        del self

    def receive_bytes(self, size=2048):  # first 5 bytes of the msg are control bytes defined in Data.py
        try:
            buf = b''
            while True:
                if self.connection_alive:
                    # print(self.role, "is receiving bytes ...")
                    # print("buffer input size:", len(buf))
                    last_rec = self.target_socket.recv(size)
                    if len(last_rec) < size or \
                       (len(last_rec) == size and last_rec[-5:] == Data.scc["message end"]):  # last piece of msg

                        if len(last_rec) < size:
                            buf += last_rec

                        pack = Packet.from_buffer(buf)
                        self.data.rec_log.append(pack)

                        # confirms do not get confirmed, everything else does
                        if pack.ctype != Data.scc["confirm"]:
                            th.start_new_thread(self._send_rec_confirmation, tuple([Packet.from_buffer(buf)]))
                        buf = b''

                    elif len(last_rec) == size:  # kleben
                        # if len == 2048 and not end in XXXXX
                        buf += last_rec
                    else:
                        print("Something in receive went wrong")

                    time.sleep(0.005)

                else:
                    # just return, that should kill the thread too
                    return

        except Exception as e:
            print("Receiving bytes by the {} failed with exception:\n{}".format(self.role, e))

    def get_last_control_type_and_msg(self):
        last_rec = self._get_last_rec()
        # print("Last receive:", last_rec.to_string())
        if last_rec:
            return last_rec.ctype, last_rec.get_payload()
        else:
            return Data.scc["undefined"], b''

    def _get_last_rec(self):
        return self.data.rec_log[-1] if len(self.data.rec_log) > 0 else None

    def new_msg_sent(self):  # this now only checks for timestamps
        last_rec = self._get_last_rec()
        if not last_rec:  # no msg was received yet
            return False
        if not self.last_chkd_msg:  # is it the first receive on this connection?
            self.last_chkd_msg = last_rec
            return True
        if self.last_chkd_msg.timestamp == last_rec.timestamp:  # compare timestamps
            return False
        else:
            self.last_chkd_msg = last_rec
            return True

    def get_rec_log_len(self):
        return self.data.rec_log.__len__()

    def get_rec_log(self):
        """use with caution as this could get long and expensive"""
        return copy.deepcopy(self.data.rec_log)

    def _send_rec_confirmation(self, packet):
        self.send(Data.scc["confirm"], packet.bytes_hash)

    def send(self, ctype, msg):

        """Universal send method, just give the ctype and the payload"""

        if ctype == Data.scc["confirm"]:
            self.target_socket.send(Packet(ctype, msg).bytes)
            return

        packet = Packet(ctype, Connection.prep(msg))

        confirmation_received = False
        msg_hash = packet.bytes_hash

        # listen for confirm
        def _check_for_confirm():
            nonlocal confirmation_received
            nonlocal msg_hash

            while not confirmation_received:
                for i, con_msg in enumerate(self.data.rec_log[self.data.confirmation_search_index:]):
                    # if our hash was confirmed by the receiver
                    if con_msg.ctype == Data.scc["confirm"] and con_msg._payload == msg_hash:
                        # print(packet.ctype, "message with timestamp", packet.timestamp, "was confirmed!")
                        confirmation_received = True
                        self.data.confirmation_search_index += i + 1
                        return
                # check for confirm every 3 seconds
                time.sleep(3)

                '''
                if self.data.rec_log[self.data.confirmation_search_index:].__contains__(
                        Data.scc["confirm"] + msg_hash + Data.scc["message end"]):
                    confirmation_received = True
                    self.data.confirmation_search_index = self.data.rec_log.index(msg_hash) + 1
                    return
                time.sleep(1)
                '''

        try:
            # print("Sending -> \nlen:", len(msg), "\nctype:", msg[0:5], "\ntimestamp:", msg[5:45], "\nmsg hash:", msg_hash, "\n")
            self.target_socket.send(packet.bytes)
        except Exception as e:
            print(e)

        th.start_new_thread(_check_for_confirm, ())

        # send until receiving was confirmed
        while not confirmation_received:
            time.sleep(3)
            #print("R E sending -> \nlen:", len(msg), "\nctype:", msg[0:5], "\ntimestamp:", msg[5:45], "\nmsg hash:", msg_hash, "\n")
            self.target_socket.send(packet.bytes)

    @staticmethod
    def prep(to_send):
        # TODO check if actual strings get pickled (they should not)
        # TODO make sure things do not get pickled twice!!!
        try:
            if isinstance(to_send, type("a")):
                # it is a string so just encode it so it becomes a bytes object?
                return to_send.encode("UTF-8")
            else:
                return Connection.object_to_bytes(to_send)
        except Exception as e:
            print("Could not convert the message '{}' to bytes, error:\n{}\n".format(to_send, e))

    @staticmethod
    def object_to_bytes(obj):
        return pickle.dumps(obj)

    @staticmethod
    def bytes_to_object(_bytes):
        # print("unpickling", len(_bytes), "bytes ....")
        return pickle.loads(_bytes)

    @staticmethod
    def bytes_to_string(_bytes):
        return _bytes.decode("UTF-8")
