import socket
import keyboard
import sys
from autocat.Robot.RobotDefine import ROBOT_ID

UDP_IP = "192.168.8.189"  # AP mode routeur margit
UDP_TIMEOUT = 5  # Seconds
if ROBOT_ID == 0:
    UDP_TIMEOUT = 0


class WifiInterface:
    def __init__(self, ip=UDP_IP, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(UDP_TIMEOUT)
        # self.socket.connect((UDP_IP, UDP_PORT))  # Not necessary

    def enact(self, action):
        """ Sending the action string, waiting for the outcome, and returning the outcome bytes """
        outcome = b'{"status":"T"}'  # Default status T if timeout
        #print("sending " + action)
        self.socket.sendto(bytes(action, 'utf-8'), (self.IP, self.port))
        try:
            outcome, address = self.socket.recvfrom(512)
        except socket.error as error:  # Time out error when robot is not connected
            print(error)
        return outcome


def onkeypress(event):
    """ Suggested by Célien """
    print("Send:", event.name)
    outcome = wifiInterface.enact(event.name)
    print(outcome)


# Test the wifi interface by controlling the robot from the console
#
if __name__ == '__main__':
    ip = UDP_IP
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)
    wifiInterface = WifiInterface(ip)
    # keyboard.on_press(onkeypress) Suggested by Celien
    _action = ""
    while True:
        print("Action key: ", end="")
        _action = keyboard.read_key().upper()
        print()
        _outcome = wifiInterface.enact('{"action":"' + _action + '"}')
        # _outcome = wifiInterface.enact(_action)
        print(_outcome)
