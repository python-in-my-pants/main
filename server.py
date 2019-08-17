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

karte = b''
client_team = ""


def threaded_client(conn):
    global karte
    global client_team
    reply = ''
    while True:
        try:
            data = conn.recv(104857645)
            # Map
            if data[0:5] == b'Teams':
                client_team = data[11:len(data)]
                print("Saved Successfully!")
            if data[0:8] == b'Team pls':
                sender(b'Team', client_team, conn)
                print("Team Send!")
            # Team
            if data[0:4] == b'Maps':
                karte = data[10:len(data)]
                print("Saved Successfully!")
            if data[0:7] == b'Map pls':
                sender(b'Map', karte, conn)
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


def sender(token, data, concon):
    reply = token
    reply += data
    concon.send(reply)


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
