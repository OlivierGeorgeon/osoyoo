# This is a sample Python script.
import socket
from time import sleep
import keyboard
from msvcrt import getch, kbhit
import json
#import egocentric_memory

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

interactionDict = {"Action": "0", "outcome": "0", "head_angle": 0, "echo_distance": 0, "angle_travelled": 0, "distance_travelled": 0}



if __name__ == '__main__':
    UDP_IP = "192.168.4.1"  # AP mode
    UDP_IP = "192.168.1.19"  # STA mode sur Olivier's wifi
    # UDP_IP = "10.40.22.251" # STA sur RobotBSN Olivier's Robot
    # UDP_IP = "10.40.22.254" # STA sur RobotBSN

    UDP_PORT = 8888
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    # Connect to the osoyoo car server
    sock.connect((UDP_IP, UDP_PORT))

    key = ""
    while key != "0":
        key = keyboard.read_key().upper()
        try:
            # Catch complementary incoming data
            sock.settimeout(0)
            data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received complementary data %s" % data)
        except:
            pass
        print("Sending action %s" % key)
        sock.sendto(bytes(key, 'utf-8'), (UDP_IP, UDP_PORT))
        try:
            # Wait for outcome
            sock.settimeout(6)
            data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received  outcome %s" % data)
        except:
            print("reception timeout")


