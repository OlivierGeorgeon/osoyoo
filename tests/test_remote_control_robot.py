#!/usr/bin/env python
# Olivier Georgeon, 2023.
# This code is used to to test the PetitCat robot.

import socket
import sys
import json
# import keyboard  # Uncomment to use instead of input()

UDP_IP = "192.168.4.1"
UDP_TIMEOUT = 5  # Seconds


class PetitCatTester:
    def __init__(self, ip, time_out, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(time_out)
        self.clock = 0
        self.focus_x = None
        self.focus_y = None
        self.color = None
        self.duration = None
        self.angle = None
        self.span = None

    def enact(self, _action_string):
        """ Sending the action string, waiting for the outcome, and returning the outcome bytes """
        _outcome = None  # Default if timeout
        # print("sending " + action)
        self.socket.sendto(bytes(_action_string, 'utf-8'), (self.IP, self.port))
        try:
            _outcome, address = self.socket.recvfrom(512)
        except socket.error as error:  # Time out error when robot is not connected
            print(error)
        return _outcome

    def send(self, _action):
        """Format the action string for the notebook"""
        command_dict = {'clock': self.clock, 'action': _action}
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
        if self.focus_y is not None:
            command_dict['focus_y'] = self.focus_y
        if self.color is not None:
            command_dict['color'] = self.color
        if self.duration is not None:
            command_dict['duration'] = self.duration
        if self.angle is not None:
            command_dict['angle'] = self.angle
        _action_string = json.dumps(command_dict)
        print("Sending packet:", _action_string)
        _outcome = self.enact(_action_string)
        print("Received packet:", _outcome)
        if _outcome is not None:
            self.clock += 1
        print("Next clock:", self.clock)
        return _outcome


# Test the wifi interface by controlling the robot from the console
# Provide the Robot's IP address as a launch argument
# py test_remote_control_robot.py 192.168.8.242
if __name__ == '__main__':
    robot_ip = UDP_IP
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    else:
        input_ip = input(f"Please provide your robot's IP address or press ENTER for default {UDP_IP} : ")
        if input_ip == "":
            robot_ip = UDP_IP

    print("Connecting to robot: " + robot_ip)
    print("Action keys: 1: Turn left, 2: Backward, 3: Turn right, 4: Swipe left, 6: Swipe right, 8: Forward, -: Scan")
    print("Ctrl+C and ENTER to abort")
    petitcat_tester = PetitCatTester(robot_ip, UDP_TIMEOUT)
    clock = 0
    action = ""
    while True:
        # print("Press action key:")
        # action = keyboard.read_key().upper()
        action = input("Enter action key:")
        action_string = '{"clock":' + str(clock) + ', "action":"' + action + '"}'
        print("Sending packet:", action_string)
        outcome = petitcat_tester.enact(action_string)
        print("Received packet:", outcome)
        if outcome is not None:
            clock += 1
