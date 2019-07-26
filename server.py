import socket
from _thread import *
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = ''
port = 5555
server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

Map = b''


def threaded_client(conn):
    global Map
    reply = ''
    while True:
        try:
            #print("1")
            data = conn.recv(104857645)
            #print("2")
            if data[0:8] == b'Map OwO!':
                print(data)
                Map = data[14:len(data)]
                print(Map)
                print("Saved Successfully!")
            if data[0:13] == b'Map pls UwU !':
                conn.send(Map)
                print("Map Send!")
        except:
            pass
        """try:
            data = conn.recv(1048576)
            print("Recieved BOi!")
            print(data)
            reply = data.decode
            print(reply)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                if len(data) <= 5000:
                    reply = data.decode()
                    print("Recieved: " + reply)
                    if reply == "Map pls UwU !":
                        print("Send it poi!")
                        conn.send(datadude)

                elif len(data) >= 5000:
                    datadude = data
                    print("Data Saved")
                    print(datadude)

        except:
            pass"""

    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
