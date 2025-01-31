import sys
import socket
from resources import IP, PORT

class client():
    def __init__(self):
        self.addr = (IP,PORT)

    def send(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode(), self.addr)

    def getInput(self):
        print(f"Listening:")
        command = input()
        if command == "exit":
            sys.exit(0)
        self.send(command)


if __name__ == "__main__":
    cln = client()
    while True:
        cln.getInput()

