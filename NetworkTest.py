from NewClient import *

client = NetworkClient()
client.send_control("8" + "="*50 + "D")
client.kill_connection()
