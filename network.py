import socket
import pickle


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.0.7"   # Schau ipconfig im cmd für die ipv4
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(1048576).decode()

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(1048576).decode()
            return reply
        except socket.error as e:
            return str(e)

    def send_data(self, stuff):
        """
        Send position to server
        :return: None
        """
        data = str(self.id) + ":" + str(pickle.dumps(stuff, 2))
        reply = self.send(data)
        return reply

    def receive_data(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1]
            return pickle.loads(d[1])
        except:
            pass
