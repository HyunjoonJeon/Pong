import subprocess
import socket
import threading
import os

class ClientConsole():
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addressport = ("52.170.185.55", 2399)
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
    

    
if __name__ == '__main__':
    client = ClientConsole()
    client.UDPthread()

