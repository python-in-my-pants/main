import socket
import pickle
import sys

from requests import get


class Network:

    def __init__(self, host=0):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host   # What's my Ip is gr8 for this get('https://api.ipify.org').text
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()
        self.team = 0
        self.map = b''
        self.g_amount = ""
        self.host_status = ""
        self.client_status = ""
        self.client_got_map = ""
        #self.client.setblocking(False)

    def routine_threaded_listener(self):
        while True:
            try:
                data = self.client.recv(104857645)
                if data[0:3] == b'Map':
                    self.map = data[3:len(data)]
                if data[0:4] == b'Team':
                    self.team = int(data[4:len(data)].decode())
                if data[0:8] == b'G_amount':
                    self.g_amount = data[8:len(data)].decode()
                if data[0:13] == b'Client_status':
                    self.client_status = data[13:len(data)].decode()
                if data[0:11] == b'Host_status':
                    self.host_status = data[11:len(data)].decode()
                if data[0:14] == b'Client_got_map':
                    self.client_got_map = data[14:len(data)].decode()
            except:
                pass
        pass

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
        size = self.size_wrapper(str(len(data)))  # 6 für die Größe der Size in Bytes
        pickletaube += size.encode()
        pickletaube += pickle.dumps(data)
        print(pickletaube.__len__())
        self.client.send(pickletaube)

    def send_control(self, token):
        # Sende Token um Aktionen zu triggern
        strgtaube = token.encode()
        self.client.send(strgtaube)

    def receive_data(self, token):
        self.client.send(token.encode())
        #reply = self.client.recv(1048576)
        #return reply

    @staticmethod
    def size_wrapper(size):
        size_len = 6 - len(size)
        reply = ""
        for i in range(size_len):
            reply += "0"
        reply += size
        return reply

    @staticmethod
    def ip_setup(ip):
        return Network(host=ip)
