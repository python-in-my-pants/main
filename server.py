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

currentId = "0"
datadude = "Oh my shoulder!"
def this_stupid(conn):
    conn.send(datadude)

def threaded_client(conn):
    global datadude
    #conn.send(str.encode("POI"))
    reply = ''
    while True:
        try:
            data = conn.recv(1048576)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                if len(data) <= 5000:
                    print("Recieved: " + reply)
                    print("Send it boi!")
                    conn.send(datadude)

                elif len(data) >= 5000:
                    datadude = data
                    print("Data Saved")
                    print(datadude)

        except:
            pass

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
