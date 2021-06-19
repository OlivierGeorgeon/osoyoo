# This is a sample Python script.
import time
import socket
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


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
    sock.settimeout(20)

    for i in range(100):
        message = bytes(input("Action: "), 'utf-8')
        # message = b"A"
        print("Sending action %s" % message)
        sock.sendto(message, (UDP_IP, UDP_PORT))

        try:
            data, address = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received outcome %s from %s/%s" % (data, address[0], address[1]))
        except:
            print("no outcome received")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
