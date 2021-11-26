import socket
import keyboard

# UDP_IP = "192.168.4.1"  # AP mode
# UDP_IP = "192.168.1.19"  # STA mode sur Olivier's wifi
# UDP_IP = "10.40.22.251" # STA sur RobotBSN Olivier's Robot en A301
# UDP_IP = "10.40.22.254" # STA sur RobotBSN
UDP_IP = "10.44.53.11"  # STA sur RobotBSN Olivier's Robot en A485
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
        _outcome = '{"outcome":"0"}'
        self.socket.sendto(bytes(_action, 'utf-8'), (self.IP, self.port))
        try:
            _outcome, address = self.socket.recvfrom(255)
        except:
            print("Reception Timeout")
        return _outcome


if __name__ == '__main__':
    wifiInterface = WifiInterface()
    action = ""
    while True:
        print("Action key: ", end="")
        action = keyboard.read_key().upper()
        print()
        outcome = wifiInterface.enact(action)
        print(outcome)
