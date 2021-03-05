import socket
import sys

HOST, PORT = "52.170.185.55", 2399
data = " Runnning the third program".join(sys.argv[1:])

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while(1):
	Text = input("")
# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
	sock.sendto(bytes( Text + "\n", "utf-8"), (HOST, PORT))
	received = str(sock.recv(1024), "utf-8")

	print("Sent:     {}".format(data))
	print("Received: {}".format(received))
