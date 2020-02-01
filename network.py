import socket
import pickle
import sys
import time

from requests import get


class Network:

    def __init__(self, host=0):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host   # What's my Ip is gr8 for this get('https://api.ipify.org').text
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()
        self.team = 0
        self.o_team = 0
        self.failsafe = False
        self.map = b''
        self.g_amount = ""
        self.host_status = ""
        self.client_status = ""
        self.client_got_map = ""
        self.other_team = b''
        self.confirmation = False
        self.my_turn = True
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
                if data[0:4] == b'Fail':
                    self.failsafe = True
                if data[0:13] == b'Client_status':
                    self.client_status = "Ready"
                if data[0:11] == b'Host_status':
                    self.host_status = "Ready"
                if data[0:14] == b'Client_got_map':
                    self.client_got_map = data[14:len(data)].decode()
                if data[0:10] == b'Other_team':
                    self.other_team = data[10:len(data)]
                if data[0:9] == b'Your_turn':
                    self.my_turn = data[9:].decode()
                if data[0:7] == b'Confirm':
                    self.confirmation = True
            except:
                pass
        pass

    def connect(self):
        try:
            self.client.connect(self.addr)
        except TimeoutError:
            # show that host is not available
            print("Host unavailable!")
            time.sleep(2)
            self.connect()
        except OSError:
            print("OSError, Host is nich da")
            time.sleep(2)
            self.connect()

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
        pickletaube += pickle.dumps(data, 1)
        temp = pickle.dumps(data, 1)
        print(pickle.loads(temp))
        print("____")
        print(pickletaube.__len__())
        self.client.send(pickletaube)

    def send_control(self, token):
        # Sende Token um Aktionen zu triggern
        strgtaube = token.encode()
        try:
            self.client.send(strgtaube)
        except ConnectionResetError:
            print("Host closed the connection")
            time.sleep(2)
            self.send_control(token.encode())

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
