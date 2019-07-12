import socket
import pickle
from retrying import retry


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.0.105"   # What's my Ip is gr8 for this
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)

    def send(self, data):
        try:
            self.client.send(data)
        except socket.error as e:
            return str(e)

    def sendd(self, data):
        self.client.settimeout(3)
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(1048576)
            return reply
        except socket.error as e:
            return str(e)

    def send_data(self, data):
        sendstuff = pickle.dumps(data, 2)
        self.send(sendstuff)

    def receive_data(self):
        token = str(1) + "§" + str("Boi next door")
        data = self.sendd(token)
        if data is None:
            raise IOError("Broken af")

        parsed = pickle.loads(data)
        return parsed

    def parse_data(self, data):
            return pickle.loads(data)
