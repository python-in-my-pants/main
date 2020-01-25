import _thread as th
import time
import pickle


class ConnectionData:

    def __init__(self, rec_buffer=[], send_buffer=[]):

        if send_buffer is None:
            send_buffer = []
        self.rec_buffer = rec_buffer            # holds list of things that were received over this connection
        self.send_buffer = send_buffer
        self.confirmation_search_index = 0


class Connection:

    # TODO: add security by replacing __hash__ with HMAC
    # https://docs.python.org/3/library/pickle.html
    # https://docs.python.org/3/library/hmac.html#module-hmac

    def __init__(self, sock, target_addr, ident, data):
        self.target_socket = sock
        self.target_addr = target_addr
        self.ident = ident
        self.data = data

        try:
            th.start_new_thread(self.receive_bytes(), ())
            print("Connection from {} to server established successfully!".format(target_addr))
        except Exception as e:
            print("Starting new thread to receive bytes failed by server, error:\n".format(e))

    def receive_bytes(self, size=2048):
        try:
            buf = ""
            while True:
                last_rec = self.target_socket.recv(size)

                if len(last_rec) == 0:
                    self.data.rec_buffer.append(buf)
                    if len(buf) > 48:  # this is the len of "Received message with hash: ..." with 20 digits hash as ...
                        self.send_rec_confirmation(buf)  # TODO super small objects do not get confirmed
                    return buf
                else:
                    buf += last_rec
        except Exception as e:
            print("Receiving bytes by the server failed with exception:\n{}".format(e))

    def send_rec_confirmation(self, rec_msg):
        self.send_bytes("Received message with hash: {}".format(rec_msg.__hash__()).encode("UTF-8"))

    # go for this if you want to send something
    def send(self, msg):
        _msg = Connection.prep(msg)
        self.send_bytes_conf(_msg)

    def send_bytes(self, msg_bytes):
        try:
            self.target_socket.send(msg_bytes)
            self.data.send_buffer.append(msg_bytes)
        except Exception as e:
            print("Sending bytes to {} by server failed. Data to send: {}\n Error:\n{}".
                  format(self.target_addr, msg_bytes, e))

    def send_bytes_conf(self, msg):

        # super short objects do not get confirmed just as small pps do not get puss
        if len(msg) <= 48:
            self.send_bytes(msg_bytes=msg)
            return

        confirmation_received = False
        msg_hash = -1
        try:
            msg_hash = msg.__hash__()  # TODO see above
        except TypeError:
            print("Message is not hashable, failed to send")

        # listen for confirm
        def check_for_confirm():
            nonlocal confirmation_received
            if self.data.rec_buffer[self.data.confirmation_search_index:].\
                    contains("Received message with hash: {}".format(msg_hash)):
                confirmation_received = True
                self.data.confirmation_search_index = self.data.rec_buffer.index("Received msg with hash {}".
                                                                                 format(msg_hash)) + 1
        th.start_new_thread(check_for_confirm(), ())

        # send until receiving was confirmed
        while not confirmation_received:
            self.target_socket.send(msg)
            time.sleep(3)

    @staticmethod
    def prep(to_send):
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
