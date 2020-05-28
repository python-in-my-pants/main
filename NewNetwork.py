import _thread as th
import time
import pickle
import copy
import hashlib
import Data
import socket
import traceback

pickle.DEFAULT_PROTOCOL = 4

'''
Important note:

The server holds a server socket only to accept incoming connections from clients. Once the connection is established,
he moves on to communicate with the client over the clients socket returned by accept().

The client however uses his own socket for communication and not just for connection establishment. So the name
"target_socket" does not quiet hold for the client, because the socket over which the communication is made is actually
his own socket and NOT the server socket of the server object.

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

    def __init__(self, ctype, payload, timestamp=None, byte_hash=None):
        self.ctype = ctype
        self._payload = payload
        self.timestamp = 1500000000000
        timestamp_padding = 30

        if timestamp:
            if isinstance(timestamp, bytes) and len(timestamp) == timestamp_padding:
                self.timestamp = timestamp
        else:
            t = str(current_milli_time())
            self.timestamp = ("0"*(timestamp_padding-len(t)) + t).encode("UTF-8")  # zero padding to 30 symbols

        self.bytes = self.ctype + self.timestamp + self._payload + Data.scc["message end"]

        self.bytes_hash = hashlib.sha1(self.bytes).hexdigest().encode("UTF-8")  # this is a string a byte array

        self.bytes = self.bytes_hash + self.bytes
        self.confirmed = False

        if byte_hash and byte_hash != self.bytes_hash:
            # packet is trash ALARM
            print("Packet is trash!")
            print(self.to_string())
            print("\tGiven checksum: ", byte_hash)
            print("\tCalculated one: ", self.bytes_hash, "\n")
            while True:
                pass
            raise Exception

    def get_hash(self):
        return self.bytes_hash

    def get_hash_old(self):
        return hashlib.sha1(self.bytes[40:]).hexdigest().encode("UTF-8")

    @classmethod
    def from_buffer(cls, buffer):
        """Construct a packet from a byte array"""

        # was return cls(buffer[40:45], buffer[75:-5], timestamp=buffer[45:75], byte_hash=buffer[0:40])

        try:
            tmp = cls(buffer[40:45], buffer[75:-5], timestamp=buffer[45:75], byte_hash=buffer[0:40])
            return tmp
        except Exception as e:
            print("Error creating packet!", e)
            return None

    def get_payload(self):  # TODO look after data types of confirm message!!!
        """returns unwrapped payload, object or string or byte array if no unwrapping type was defined in Data.py"""
        try:
            if self.ctype in Data.unwrap_as_str:
                return self._payload.decode("UTF-8")
            if self.ctype in Data.unwrap_as_obj:
                return pickle.loads(self._payload)
            else:
                print("Warning! Unwrapping type for", self.ctype.decode("UTF-8"), "is not defined!")
                return self._payload
        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 76!")
            print("Error in get_payload while getting payload of {}-type packet!".format(self.ctype))
            print(e)
            print(self.to_string())
            return self._payload

    def to_string(self, n=0):
        return ("\t" * n + "Ctype:\t\t{}\n" +
                "\t" * n + "Length:\t\t{}\n" +
                "\t" * n + "Timestamp:\t{}\n" +
                "\t" * n + "Payload:\t{} ... {}\n" +
                "\t" * n + "Hash:\t\t{}").\
            format(self.ctype, str(len(self.bytes)), self.timestamp, self._payload[:20], self.bytes[-20:],
                   self.bytes_hash)


class Packet_old:

    def __init__(self, ctype, payload, timestamp=None):
        self.ctype = ctype
        self._payload = payload
        self.timestamp = 1500000000000
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
        try:
            if self.ctype in Data.unwrap_as_str:
                return self._payload.decode("UTF-8")
            if self.ctype in Data.unwrap_as_obj:
                return pickle.loads(self._payload)
            else:
                print("Warning! Unwrapping type for", self.ctype.decode("UTF-8"), "is not defined!")
                return self._payload
        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 76!")
            print("Error in get_payload while getting payload of {}-type packet!".format(self.ctype))
            print(e)
            print(self.to_string())
            return self._payload

    def to_string(self, n=0):
        return ("\t" * n + "Ctype:\t\t{}\n" +
                "\t" * n + "Length:\t\t{}\n" +
                "\t"*n + "Timestamp:\t{}\n" +
                "\t"*n + "Payload:\t{}...\n" +
                "\t"*n + "Hash:\t\t{}").\
            format(self.ctype, str(len(self.bytes)), self.timestamp, self._payload[-40:], self.bytes_hash)


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

        self.fail_counter = 0
        self.old_rec_len = -1
        self.last_chkd_msg = None

        try:
            th.start_new_thread(self.receive_bytes, ())
            if self.role == "Server":
                print("Connection from {} to {} established successfully!".format(target_addr, self.role))
            else:
                print("Connection from {} to server at {} established successfully!".format(self.role, target_addr))
        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 114!")
            print("Starting new thread to receive bytes failed by {}, error:\n{}".format(self.role, e))

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        if self.ident == other.ident:
            return True
        return False

    def kill_connection(self):

        # tell listening thread to stop
        self.connection_alive = False

        # wait for it to recognize the stop (not necessary anymore), was time.sleep(2)
        time.sleep(2)

        # now kill the socket (listening should be dead)
        # self.target_socket.shutdown(socket.SHUT_RDWR)  # TODO gave a gub
        self.target_socket.close()
        del self

    def receive_bytes_old(self, size=4096):
        # first 5 bytes of the msg are control bytes defined in Data.py
        try:
            buf = b''
            while True:
                if self.connection_alive:

                    # print(self.role, "is receiving bytes ...")
                    # print("buffer input size:", len(buf))
                    last_rec = self.target_socket.recv(size)

                    # always glue together
                    buf += last_rec

                    # check if its the last piece of the message
                    if len(last_rec) < size or last_rec[-5:] == Data.scc["message end"]:

                        '''
                        It is the last piece of the message if:
                        3 cases:
                        - ends     in xxxxx and len < size   ... if len < then it's always the last msg
                        - ends     in xxxxx and len = size   ... size and last frame size match
                        - ends not in xxxxx and len < size   ... xxxxx got cut apart, this is the second part of it
                        '''
                        print("+++ Message {} with len {} ended bc of {}".
                              format(buf[40:45], len(buf), "len" if len(last_rec) < size else "XXXXX"))
                        pack = Packet.from_buffer(buf)
                        """
                        if pack.ctype in Data.iscc:

                            # check if payload could be valid
                            proxy_payload = pack.get_payload()

                            
                            if ((pack.ctype in Data.unwrap_as_obj) and len(proxy_payload) == Data.arg_len[pack.ctype]) \
                                or pack.ctype in Data.unwrap_as_str:

                                self.data.rec_log.append(pack)
                                # check if msg needs confirm
                                if Data.needs_confirm[Data.iscc[pack.ctype]]:
                                    th.start_new_thread(self._send_rec_confirmation, tuple([Packet.from_buffer(buf)]))

                            if ((pack.ctype in Data.unwrap_as_obj) and len(proxy_payload) == Data.arg_len[pack.ctype]) \
                                    or pack.ctype in Data.unwrap_as_str:

                                self.data.rec_log.append(pack)
                                # check if msg needs confirm
                                if Data.needs_confirm[Data.iscc[pack.ctype]]:
                                    th.start_new_thread(self._send_rec_confirmation, tuple([Packet.from_buffer(buf)]))
                                    
                        buf = b''
                        """

                        # check if the packet is OK
                        if pack is not None:

                            #print("all good: {}\n{}\n{}\n".format(pack.ctype, pack.bytes[:40], pack.get_hash()))
                            self.data.rec_log.append(pack)

                            if self.role == "Client":
                                print(pack.to_string(), "\n")

                            # check if msg needs confirm
                            if Data.needs_confirm[Data.iscc[pack.ctype]]:
                                th.start_new_thread(self._send_rec_confirmation, tuple([pack]))

                        buf = b''

                    time.sleep(0.005)

                else:
                    # just return, that should kill the thread too
                    return

        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 169!")
            print("Receiving bytes by the {} failed with exception:\n{} ... but I'm fine".format(self.role, e))

    def receive_bytes(self, size=4096):
        # first 5 bytes of the msg are control bytes defined in Data.py
        try:
            buf = b''
            while True:
                if self.connection_alive:

                    last_rec = self.target_socket.recv(size)

                    buf += last_rec

                    # something is in the buffer (already received) and the next rec is empty -> msg ended
                    if (buf and not last_rec) or buf[-5:] == Data.scc["message end"]:

                        print("+++ Message {} with len {} ended bc of {}".
                              format(buf[40:45], len(buf), "empty" if not last_rec else
                                                           ("XXXXX" if buf[-5:]==Data.scc["message end"] else "???")))

                        pack = Packet.from_buffer(buf)

                        # check if the packet is OK
                        if pack is not None:

                            self.data.rec_log.append(pack)

                            if self.role == "Client":
                                print(pack.to_string(), "\n")

                            # check if msg needs confirm
                            if Data.needs_confirm[Data.iscc[pack.ctype]]:
                                th.start_new_thread(self._send_rec_confirmation, tuple([pack]))

                        buf = b''

                    time.sleep(0.005)

                else:
                    # just return, that should kill the thread too
                    return

        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 169!")
            print("Receiving bytes by the {} failed with exception:\n{} ... but I'm fine".format(self.role, e))

    def get_last_control_type_and_msg(self):
        last_rec = self._get_last_rec()
        if last_rec:
            return last_rec.ctype, last_rec.get_payload()
        else:
            return Data.scc["undefined"], b''

    def _get_last_rec(self):
        return self.data.rec_log[-1] if len(self.data.rec_log) > 0 else None

    def new_msg_sent(self):  # this now only checks for timestamps
        # TODO doesn't work bc timestamp of last could be timestamp of third last u know?
        # # new msg in between doesn't get seen
        last_rec = self.get_rec_log_fast(5)
        if not last_rec:  # no msg was received yet
            return False
        if not self.last_chkd_msg:  # is it the first receive on this connection?
            self.last_chkd_msg = last_rec
            return True
        if self.last_chkd_msg == last_rec:  # compare timestamps
            return False
        else:
            self.last_chkd_msg = last_rec
            return True

    def get_rec_log_len(self):
        return self.data.rec_log.__len__()

    def get_rec_log_fast(self, n):
        lol = self.data.rec_log[-n:]
        lol.reverse()
        return lol

    def get_rec_log(self):
        """use with caution as this could get long and expensive"""
        return copy.deepcopy(self.data.rec_log)

    def _send_rec_confirmation(self, packet):
        try:
            self.send(Data.scc["confirm"], packet.bytes_hash)
        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 213!")
            print("Sending confirmation failed! Error: {}".format(e))

    def send(self, ctype, msg):

        """Universal send method, just give the ctype and the payload"""

        if not self.connection_alive:
            print("Connection is dead!")
            return

        # doesn't need to be confirmed
        if not Data.needs_confirm[Data.iscc[ctype]]:
            try:
                if ctype == Data.scc["confirm"]:
                    p = Packet(ctype, msg)
                else:
                    p = Packet(ctype, Connection.prep(msg))

                if self.role == "Server":
                    print(("\t" * 30 + "Sending:\t" + str(self.ident) + "\n{}\n").format(p.to_string(n=30)))
                self.target_socket.send(p.bytes)

            except Exception as e:
                print("")
                traceback.print_exc()
                print("Exception in NewNetwork in line 238!")
                print("Sending confirmation failed! Error: {}".format(e))
                self.fail_counter += 1
                if self.fail_counter >= 3:
                    print("Recipient seems dead!")
                    self.kill_connection()
                    return
            return

        packet = Packet(ctype, Connection.prep(msg))
        # TODO debug only
        print(packet.to_string(n=30), "\n")

        confirmation_received = False
        msg_hash = packet.bytes_hash

        # listen for confirm
        def _check_for_confirm():
            nonlocal confirmation_received
            nonlocal msg_hash

            while not confirmation_received:
                if not self.connection_alive:
                    return
                for i, con_msg in enumerate(self.data.rec_log[self.data.confirmation_search_index:]):
                    # if our hash was confirmed by the receiver
                    if con_msg.ctype == Data.scc["confirm"] and con_msg._payload == msg_hash:
                        if self.role == "Server":
                            print("->"*10, packet.ctype, "message with timestamp", packet.timestamp, "was confirmed!")
                        confirmation_received = True
                        self.data.confirmation_search_index += i + 1
                        return
                # check for confirm
                time.sleep(0.5)

        try:
            # just print if you are server
            if self.role == "Server":
                print("\t" * 30 + "Sending:\t" + str(self.ident) + "\n{}\n".format(packet.to_string(n=30)))

            self.target_socket.send(packet.bytes)
        except Exception as e:
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 280!")
            print(e)

        th.start_new_thread(_check_for_confirm, ())

        counter = 2

        # send until receiving was confirmed
        while not confirmation_received:
            time.sleep(3)
            try:
                counter += 1
                if self.role == "Server":
                    print("\t" * 30 + "... for the", counter-1, ". time:")
                    print("\t" * 30 + "Sending:" + str(self.ident) + "\n{}\n".format(packet.to_string(n=30)))
                self.target_socket.send(packet.bytes)
                counter += 1
            except Exception as e:
                print("")
                traceback.print_exc()
                print("Exception in NewNetwork in line 297!")
                print("Resending message failed! Error: {}".format(e))

            if counter >= 5:
                print("Jz geb ich's auf, resending von {} abgebrochen...".format(packet.ctype))
                return

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
            print("")
            traceback.print_exc()
            print("Exception in NewNetwork in line 311!")
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
