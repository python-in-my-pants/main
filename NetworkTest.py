from NewClient import *

client = NetworkClient()
client.send_control("ERschieß DEICH")
client.kill_connection()
