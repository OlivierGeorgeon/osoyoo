import socket
import keyboard

# UDP_IP = "192.168.4.1"  # AP mode
UDP_IP = "192.168.1.19"  # STA mode sur Olivier's wifi
# UDP_IP = "10.40.22.251" # STA sur RobotBSN Olivier's Robot en A301
# UDP_IP = "10.40.22.254" # STA sur RobotBSN
# UDP_IP = "10.44.53.11"  # STA sur RobotBSN Olivier's Robot en A485
UDP_TIMEOUT = 3  # Seconds


class WifiInterface:
    def __init__(self, ip=UDP_IP, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(UDP_TIMEOUT)
        # self.socket.connect((UDP_IP, UDP_PORT))  # Not necessary

    '''Send the action string. Return the outcome string'''
    def enact(self, action):
        outcome = '{"outcome":"0"}'
        self.socket.sendto(bytes(action, 'utf-8'), (self.IP, self.port))
        try:
            outcome, address = self.socket.recvfrom(255)
        except socket.error as error:  # Expect possible time out error
            print(error)
        return outcome


if __name__ == '__main__':
    wifiInterface = WifiInterface()
    _action = ""
    while True:
        print("Action key: ", end="")
        _action = keyboard.read_key().upper()
        print()
        _outcome = wifiInterface.enact('{"action":"' + _action + '"}')
        # _outcome = wifiInterface.enact(_action)
        print(_outcome)
