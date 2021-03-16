import socket

UDP_IP = "52.170.185.55"
UDP_PORT = 2399
MESSAGE = b"Zion's second attempt !"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

print("Connection established and message sent")
