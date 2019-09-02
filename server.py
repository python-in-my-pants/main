import socket
from _thread import *
from numpy import *
import sys
import os

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
counter = 0
conn1 = None
conn2 = None

karte = b''
client_team_num = 0
host_status = ""
client_status = ""
client_got_map = ""
host_team = None
client_team = None
host_turn = False
client_turn = False
rando = random.randint(0, 2)
if rando == 0:
    host_turn = True
else:
    client_turn = True


def threaded_client(conn):
    global counter
    global karte
    global client_team_num
    global host_status
    global client_status
    global client_got_map
    global host_team
    global client_team
    global host_turn
    global client_turn
    global conn1
    global conn2

    reply = ''
    while True:
        try:
            data = conn.recv(104857645)
            # Team
            if data[0:5] == b'Teams':
                client_team = data[11:len(data)]
                print("Saved Successfully!")
            if data[0:8] == b'Team pls':
                sender(b'Team', str(client_team).encode(), conn)
                print("Team Send!")
            # Map
            if data[0:4] == b'Maps':
                karte = data[4:len(data)]
                print("Saved Successfully!")
            if data[0:7] == b'Map pls':
                print(karte.__len__())
                sender(b'Map', karte, conn)
                print("Map send!")
            # Host_status
            if data[0:12] == b'Host_ready':
                host_status = "Ready"
                #sender(b'Host_status', host_status.encode(), conn2)
                print("Host status: Ready!")
            if data[0:14] == b'Host_not_ready':
                host_status = "Not ready"
                #sender(b'Host_status', host_status.encode(), conn2)
                print("Host status: Not ready!")
            if data[0:13] == b'Host_status':
                sender(b'Host_status', host_status.encode(), conn)
            # Client_status
            if data[0:12] == b'Client_ready':
                client_status = "Ready"
                #sender(b'Client_status', client_status.encode(), conn1)
                print("Client status: Ready!")
            if data[0:16] == b'Client_not_ready':
                client_status = "Not ready"
                #sender(b'Client_status', client_status.encode(), conn1)
                print("Client status: Not ready!")
            if data[0:13] == b'Client_status':
                sender(b'Client_status', client_status.encode(), conn)
            # Teams
            if data[0:4] == b'Team':
                if conn == conn1:
                    host_team = data[10:]
                if conn == conn2:
                    client_team = data[10:]
            if data[0:8] == b'Team_pls':
                if conn == conn1:
                    sender(b'Other_team', client_team, conn)
                if conn == conn2:
                    sender(b'Other_team', host_team, conn)
            # Turns # ToDo on Client Side delete anordern
            if data[0:9] == b'Their_turn':
                if conn == conn1:
                    client_turn = True
                if conn == conn2:
                    host_turn = True
            if data[0:8] == b'Turn_pls':
                if conn == conn1:
                    sender(b'Your_turn', host_turn, conn)
                if conn == conn2:
                    sender(b'Your_turn', client_turn, conn)
            # Delete_Turns
            if data[0:11] == b'Turn_delete':
                client_turn = False
                host_turn = False
            # Status Delete
            if data[0:12] == b'Ready_delete':
                client_status = ""
                host_status = ""
                print("Deleted Status!")
            # Client_got_map
            if data[0:12] == b'Map received':
                client_got_map = "Yes"
                print("_____________")
                sender(b'Client_got_map', client_got_map.encode(), conn1)
            # Connection_amount
            if data[0:8] == b'G_amount':
                sender(b'G_amount', str(counter).encode(), conn1)
            # Close
            if data[0:5] == b'Close':
                os._exit(1)
        except:
            pass

    print("Connection Closed")
    counter -= 1
    conn.close()


def sender(token, data, concon):
    reply = token
    reply += data
    #print(reply)
    concon.send(reply)


while True:
    conn, addr = s.accept()
    counter += 1
    if counter == 1: conn1 = conn
    if counter == 2: conn2 = conn
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
