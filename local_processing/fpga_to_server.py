import subprocess
import socket

def send_on_jtag(cmd):
    # Taken from IP lab 4
    assert len(cmd)==1, "Make the cmd a single character"

    inputCmd = "nios2-terminal.exe <<< {}".format(cmd)

    # subprocess allows python to run a bash command
    output = subprocess.run(inputCmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE)

    vals = output.stdout
    vals = vals.decode("utf-8")
    vals = vals.split('<-->')

    return vals[1].strip()



def main():
   
    #Server connection setup
    serverAddressPort   = ("52.170.185.55", 2399)
    bufferSize          = 1024
    UDPClientSocket     = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    n = 1
    msgFromClient = send_on_jtag('r')
    bytesToSend   = str.encode(msgFromClient)
    
    while n > 0:
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        msgFromClient = send_on_jtag('r')
        bytesToSend   = str.encode(msgFromClient)


    ''' Reserved for later use with the server side
    
    msg = "Message from Server {}".format(msgFromServer[0])
    print(msg) 
    
    '''
    

    #res = send_on_jtag('t') # example of how to use send_on_jtag function
    #print(x, res)
    
if __name__ == '__main__':
    main()

