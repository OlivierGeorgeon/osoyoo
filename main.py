# This is a sample Python script.
import socket
from time import sleep
import keyboard
from msvcrt import getch, kbhit
import json
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

interactionDict = {"Action": "0", "outcome": "0", "head_angle": 0, "echo_distance": 0, "angle_travelled": 0, "distance_travelled": 0}

# for i in range(10):
#     print(i)
#     sleep(1)
#     if kbhit(): # returns True if the user has pressed a key
#         action = getch()
#         print("test")



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # UDP_IP = "192.168.4.1"  # AP mode
    UDP_IP = "192.168.1.17"  # STA mode
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
        #if len(key) == 1:
        print("Sending action %s" % key)
        sock.sendto(bytes(key, 'utf-8'), (UDP_IP, UDP_PORT))
        try:
            # Wait for outcome
            sock.settimeout(6)
            data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received  outcome %s" % data)
        except:
            print("reception timeout")
        #else:

    # for i in range(100):
    #     message = bytes(input("Action: "), 'utf-8')
    #
    #     # Check whether we received complementary message from the last round
    #     try:
    #         sock.settimeout(0)
    #         data, addresBs = sock.recvfrom(1024)  # buffer size is 1024 bytes
    #         print("received complementary data %s" % data)
    #     except:
    #         pass
    #
    #     print("Sending action %s" % message)
    #     sock.sendto(message, (UDP_IP, UDP_PORT))
    #
    #     try:
    #         sock.settimeout(2)
    #         data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
    #         print("received outcome %s from %s/%s" % (data, address[0], address[1]))
    #     except:
    #         print("no outcome received")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
