import subprocess
import socket
import threading
import os
import sys
import signal
import time

class ClientConsole():
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addressport = ("51.145.12.252", 2399)
        self.buffersize = 1024
        self.command = 'x'
        
    def UDPthread(self):
        t1 = threading.Thread(target=self.UDPreceive)
        t2 = threading.Thread(target=self.UDPsend)
        t1.start()
        t2.start()
        
    def UDPsend(self):
        process = subprocess.Popen("nios2-terminal", shell=True, 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        while True:
            time.sleep(1/120)
            #print ("UDPsend loop <-> " , self.command)
            process.stdin.write(str.encode(self.command))
            process.stdin.flush()
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output = output.decode("utf-8")
                if "exiting due to ^D on remote" in output:
                    print("Exiting!")
                    os._exit(1)
                output = output.split('<-->')
            try:
                self.sock.sendto(str.encode(output[1].strip()),self.addressport)
            except Exception:
                print(output[0])

    def UDPreceive(self):
        while True:
            #print ("UDPreceive loop")
            msgfromserver = self.sock.recvfrom(self.buffersize)
            msg = "Message from Server {}".format(msgfromserver[0])
            print(msg)
            self.command = msgfromserver[0].decode("utf-8")

    def UDPconnect(self):
        connectmsg = "Connect"
        self.sock.sendto(str.encode(connectmsg), self.addressport)
        newaddressport = self.sock.recvfrom(self.buffersize)
        self.addressport = ("51.145.12.252", int(newaddressport[0].decode("utf-8")))
        self.UDPthread()

    def UDPdisconnect(self, signal, frame):
        self.sock.sendto(str.encode("d"), self.addressport)
        exit(0)
        
    

    
if __name__ == '__main__':
    client = ClientConsole()
    client.UDPconnect()
    signal.signal(signal.SIGINT, client.UDPdisconnect)

