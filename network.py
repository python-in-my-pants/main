import socket
import pickle
from retrying import retry


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.0.7"   # Schau ipconfig im cmd für die ipv4
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(65536).decode()

    def send(self, data):
        try:
            self.client.send(data)
        except socket.error as e:
            return str(e)

    def send_data(self, stuff):
        data = pickle.dumps(stuff, 2)
        self.send(data)
    @retry
    def receive_data(self):
        self.client.setblocking(False)
        try:
            reply = self.parse_data(self.client.recv(65536))#1048576
            print("PENIS")
            if reply is None:
                raise IOError("Broken af")
            return reply
        except:
            pass

    def parse_data(self, data):
            return pickle.loads(data)
