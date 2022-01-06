import socket
import keyboard
import time

class WifiInterface:
    def __init__(self, ip="192.168.4.1", port=8888, udpTimeout=4):
        self.IP = ip
        self.port = port
        self.udpTimeout = udpTimeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.udpTimeout)
        # self.socket.connect((UDP_IP, UDP_PORT))  # Not necessary

    '''Send the action. Return the outcome'''
    def enact(self, jsonAction):
        _outcome = "{}"

        if jsonAction["action"] != '$':
            self.socket.settimeout(0.2)
            try:
                Routcome, address = self.socket.recvfrom(255)
                print("Outcome en retard", Routcome)
            except:
                pass
            self.socket.settimeout(self.udpTimeout)
            
        self.socket.sendto(bytes(str(jsonAction).replace("\'", "\""), 'utf-8'), (self.IP, self.port))
        try:
            _outcome, address = self.socket.recvfrom(255)
        except:
            print("Reception Timeout for command:", jsonAction["action"])
        return _outcome


def onkeypress(event):
    print("Send:", event.name)
    outcome = wifiInterface.enact({"action":event.name})
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
            outcome = wifiInterface.enact({"action": "$"})
            





