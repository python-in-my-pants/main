from NewClient import *

client = NetworkClient()
client.send_control("8" + "="*71 + "D")
client.kill_connection()
