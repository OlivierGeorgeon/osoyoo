import socket
import keyboard
import time
from Python import RobotDefine





UDP_TIMEOUT = 5  # Seconds
if RobotDefine.ROBOT_ID == 0:
    UDP_TIMEOUT = 0



class WifiInterface:
    def __init__(self, ip="10.40.22.254", port=8888, udpTimeout=4):
        self.IP = ip
        self.port = port
        self.udpTimeout = udpTimeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.udpTimeout)
        # self.socket.connect((UDP_IP, UDP_PORT))  # Not necessary

    '''Send the action. Return the outcome'''
    def enact(self, action):
        """ Sending the action string, waiting for the outcome, and returning the outcome bytes """
        outcome = b'{"status":"T"}'  # Default status T if timeout
        print("sending " + str(action))
        self.socket.sendto(bytes(str({"action" : action}).replace("'", '"'), 'utf-8'), (self.IP, self.port))
        try:
            outcome, address = self.socket.recvfrom(512)
        except socket.error as error:  # Time out error when robot is not connected
            print(error)
        return outcome

def onkeypress(event):
    print("Send:", event.name)
    outcome = wifiInterface.enact({"action":event.name})
    print(outcome)
    
# Test the wifi interface by controlling the robot from the console
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
            






