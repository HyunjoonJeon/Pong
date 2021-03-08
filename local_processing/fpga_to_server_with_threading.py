import subprocess
import socket
import threading


class ClientConsole():
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addressport = ("52.170.185.55", 2399)
        self.buffersize = 1024
        self.command = 'r'
        
    def send_on_jtag(self, cmd):
        # Taken from IP lab 4
        assert len(cmd)==1, "Make the cmd a single character"

        inputCmd = "nios2-terminal <<< {}".format(cmd)

        # subprocess allows python to run a bash command
        output = subprocess.run(inputCmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE)

        vals = output.stdout
        vals = vals.decode("utf-8")
        vals = vals.split('<-->')

        return vals[1].strip()

    def UDPsend(self):
        while True:
            self.sock.sendto(str.encode(self.send_on_jtag(self.command)), self.addressport)
            t = threading.Thread(target=self.UDPreceive)
            t.start()

    def UDPreceive(self):
        msgfromserver = self.sock.recvfrom(self.buffersize)
        msg = "Message from Server {}".format(msgfromserver[0])
        print(msg)
        self.command = msgfromserver.decode("utf-8")
    

    
if __name__ == '__main__':
    client = ClientConsole()
    client.UDPreceive()

