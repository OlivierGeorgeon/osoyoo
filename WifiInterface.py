import socket
import keyboard
import time

#UDP_IP = "192.168.4.1"  # AP mode
# UDP_IP = "192.168.1.19"  # STA mode sur Olivier's wifi
# UDP_IP = "10.40.22.251" # STA sur RobotBSN Olivier's Robot
#UDP_IP = "10.40.22.251" #IP du robot 2 STA sur RobotBSN
# UDP_IP = "10.40.22.254" #IP du robot 1 STA sur RobotBSN


UDP_TIMEOUT = 3  # Seconds

class WifiInterface:
    def __init__(self, ip=UDP_IP, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(UDP_TIMEOUT)
        # self.socket.connect((UDP_IP, UDP_PORT))  # Not necessary

    '''Send the action. Return the outcome'''
    def enact(self, _action):
        _outcome = "{}"
        self.socket.sendto(bytes(_action, 'utf-8'), (self.IP, self.port))
        try:
            _outcome, address = self.socket.recvfrom(255)
        except:
            print("Reception Timeout for command:", _action)
        return _outcome


def onkeypress(event):
    print("Send:", event.name)
    outcome = wifiInterface.enact(event.name)
    print(outcome)

if __name__ == '__main__':
    wifiInterface = WifiInterface()
    # Bind event key press
    keyboard.on_press(onkeypress)
    # Every 15 seconds, requests bot data
    cooldown = time.time()
    while True:
        if cooldown + 15 <= time.time():
            cooldown = time.time()
            print("Data requests")
            outcome = wifiInterface.enact('$')
            





