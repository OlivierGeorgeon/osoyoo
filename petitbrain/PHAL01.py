#!/usr/bin/env python
#Python-Hardware Abstraction Layer


 Olivier Georgeon, 2024.
# This code is used to demonstrates the reliable wifi protocol between the PC and the robot.

# After sending the command string, the PC expects to receive the outcome string within a timeout.
# If not, two things may have happened:
# 1) the robot did not receive the command string,
# 2) the robot did receive the command string, executed the command, sent the outcome string, but the PC did not
#    receive the outcome string.
# In both cases, when the timeout is triggered, the PC sends the command string again.
# In case 1), the robot detects that it received a new command string (new clock value), executes the command as if
#    the string was sent for the first time, and then sends the outcome string back to the PC.
# In case 2), the robot detects that it received the same command string again (same clock), so it does not execute the
#    command again but resents the outcome string.
# The PC keeps resending the command string until it receives the outcome string.

import socket
import sys
import json
import time
import keyboard


UDP_IP = "192.168.8.242"
UDP_TIMEOUT = 5  # Seconds

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_ENACTING = 2

running = True


class RobotController:
    """The RobotController class handles the communication between the PC and the robot"""

    def __init__(self, ip, time_out, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0)  # The socket's time out is 0. Not to be mistaken with the timeout used by code

        self.clock = 0
        self.time_out = time_out
        self.send_time = 0.
        self.interaction_step = INTERACTION_STEP_IDLE
        self.command_string = None
        self.outcome_string = None

        # The additional fields of the command string (not used in this script)
        self.focus_x = None
        self.focus_y = None
        self.color = None
        self.duration = None
        self.angle = None
        self.span = None

    def main(self):
        """Execute this method in the main loop"""
        # If the robot is not enacting an interaction
        if self.interaction_step == INTERACTION_STEP_IDLE:
            # If there is a command string then send it
            if self.command_string is not None:
                print("Sending command", self.command_string)
                self.socket.sendto(bytes(self.command_string, 'utf-8'), (self.IP, self.port))
                self.send_time = time.time()
                self.interaction_step = INTERACTION_STEP_ENACTING

        # If the robot is enacting an interaction
        else:
            # If the time out is not elapsed
            if time.time() < self.send_time + self.time_out:
                # Watch for the outcome
                try:
                    self.outcome_string, _ = self.socket.recvfrom(512)
                    # If no error then the outcome string was received
                    print("\nOutcome:", self.outcome_string)
                    self.clock += 1
                    self.command_string = None
                    self.interaction_step = INTERACTION_STEP_IDLE
                # If error then the outcome is not yet received. Print "." and keep waiting
                except socket.timeout:  # The socket timeout was set to 0
                    print(".", end='')
                except OSError as e:  # Other reception error codes tested on PC and Mac
                    if e.args[0] in [35, 10035]:
                        print(".", end='')
                    else:
                        print(e)

            # The timeout is elapsed. Resend the command string
            else:
                print(f". Timeout {self.time_out:.3f}s")
                # Resetting the interaction_step will resend the command string on the next cycle if not None
                self.interaction_step = INTERACTION_STEP_IDLE

    def generate_command_string(self, event):
        """Handle keypress: generate the next command string"""
        global running
        action = event.name.upper()
        if action == "R":
            # Stop sending again the command string
            self.command_string = None
        elif action == "Q":
            # Exit the program
            running = False
            sys.exit()  # Does not work for some reason
        elif self.interaction_step == INTERACTION_STEP_IDLE:
            # If a key was pressed then generate the command string
            command_dict = {'clock': self.clock, 'action': action}
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
            self.command_string = json.dumps(command_dict)
            self.outcome_string = None


# To run this demonstration, provide the Robot's IP address as a launch argument. For example:
# py reliable_teleop.py 1

if __name__ == '__main__':
    # Check the robot's IP address
    robot_ip = UDP_IP
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    else:
        input_ip = input(f"Please provide your robot's IP address or press ENTER for default {UDP_IP} : ")
        if input_ip == "":
            robot_ip = UDP_IP

    print("Connecting to robot: " + robot_ip)
    print("Action keys: 1: Turn left, 2: Backward, 3: Turn right, 4: Swipe left, 6: Swipe right, 8: Forward, -: Scan")
    print("Reset: R. Quit: Q")

    robot_controller = RobotController(robot_ip, UDP_TIMEOUT)
    # Setup the keyboard listener
    keyboard.on_press(robot_controller.generate_command_string)

    # The main loop
    while running:
        robot_controller.main()
        time.sleep(0.1)  # Loop every 100ms