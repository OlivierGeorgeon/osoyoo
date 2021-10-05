import socket

class RobotController():
    def __init__(self, IP, port):
        # IP du robot (192.168.4.1 par default)
        self.IP = IP
        self.port = port
        self.upperCaseOnly = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    '''Permet d'envoyer des données par le wifi et d'en recevoir en retour'''
    def start(self):
        while True:
            data = input("Données à envoyer >> ")
            data = data.upper() if self.upperCaseOnly is True else data
            self.socket.sendto(data.encode(), (self.IP, self.port))
            try:
                self.socket.settimeout(5)
                data, address = self.socket.recvfrom(255)
                print("Données reçu >> ", data.decode())
            except:
                print("Timeout")

robot = RobotController("192.168.4.1", 8888)
robot.start()