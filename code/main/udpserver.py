# This python script listens on UDP port 3333 
# for messages from the ESP32 board and prints them
import socket
import sys
from live_process import LiveProcess

lp = LiveProcess()

packetSize = 30 # 20 Bytes (Muse packet size)
udpPort = 9999

try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except(socket.error):
    # print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    print('Failed to create socket')
    sys.exit()

try:
    s.bind(('', udpPort)) #'' to bind to all local addresses
except(socket.error):
    # print('Bind failed. Error: ' + str(msg[0]) + ': ' + msg[1])
    print('Bind failed')
    sys.exit()
     
print('Server listening')

while 1:
    d = s.recvfrom(packetSize) #Returns bytes object
    data = d[0]
     
    if not data: 
        break
    
    # print(data.strip())
    lp.addPacket(data.strip())

    
s.close()