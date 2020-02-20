from NewClient import *

client = NetworkClient()
client.send_control("-"*63)
client.kill_connection()
