import socket
import sys


class RobotController:
    def __init__(self, ip, port):
        self.IP = ip
        self.port = port
        self.upperCaseOnly = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        """Permet d'envoyer des données par le wifi et d'en recevoir en retour"""
        while True:
            data = input("Données à envoyer >> ")
            data = data.upper() if self.upperCaseOnly is True else data
            self.socket.sendto(data.encode(), (self.IP, self.port))
            try:
                self.socket.settimeout(5)
                data, address = self.socket.recvfrom(255)
                print("Données reçu >> ", data.decode())
            except socket.error as error:
                print(error)


# Test the wifi interface by controlling the robot from the console
# Replace the IP address with your robot's IP address. Run :
# > python -m Python.OsoyooControllerBSN.Wifi.RobotController <Robot's IP>
if __name__ == '__main__':
    ip = "192.168.4.1"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)
    robot = RobotController(ip, 8888)
    robot.start()
