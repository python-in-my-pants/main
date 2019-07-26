import socket
import pickle
import sys

from requests import get


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = get('https://api.ipify.org').text   # What's my Ip is gr8 for this
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()
        #self.client.setblocking(False)

    def connect(self):
        self.client.connect(self.addr)

    def send_data(self, token, data):
        # Sendformat: Token, Size, Data
        taube = token.encode()
        size = self.size_wrapper(str(len(data)+len(token)+6))  # 6 für die Größe der Size in Bytes
        taube += size.encode()
        taube += data.encode()
        self.client.send(taube)

    def send_data_pickle(self, token, data):
        # Sendformat: Token, Size, Data
        pickletaube = token.encode()
        size = self.size_wrapper(str(len(data)+len(token)+6))  # 6 für die Größe der Size in Bytes
        pickletaube += size.encode()
        pickletaube += pickle.dumps(data)
        print(pickle.dumps(data))
        self.client.send(pickletaube)

    def receive_data(self, token):
        self.client.send(token.encode())
        reply = self.client.recv(1048576)
        return reply

    def receive_data_pickle(self, token):
        self.client.send(token.encode())
        reply = pickle.loads(self.client.recv(1048576))
        return reply

    @staticmethod
    def size_wrapper(size):
        size_len = 6 - len(size)
        reply = ""
        for i in range(size_len):
            reply += "0"
        reply += size
        return reply
