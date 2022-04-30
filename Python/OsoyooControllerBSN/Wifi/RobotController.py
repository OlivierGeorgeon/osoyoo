import sys
import threading
import json
import time
import keyboard
import math
from pyrr import matrix44
from . WifiInterface import WifiInterface
from . RobotDefine import *


class RobotController:
    def __init__(self, robot_ip):
        self.wifiInterface = WifiInterface(robot_ip)

        self.action = ""
        self.action_angle = 0
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout
        self.azimuth = 0

    def command_robot(self, action):
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        self.outcome_bytes = "Waiting"

        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            action_string = json.dumps({'action': self.action, 'angle': self.action_angle})
            print("Sending: " + action_string)
            self.outcome_bytes = self.wifiInterface.enact(action_string)
            print("Receive ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2

        self.action = action
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()

        # Cas d'actions particulières :
        if action == "r":
            self.action_reset()

    def translate_robot_data(self):
        """ Computes the enacted interaction from the robot's outcome data """
        outcome = json.loads(self.outcome_bytes)
        enacted_interaction = {'action': self.action, 'status': outcome['status']}

        # If timeout then no ego memory update
        if enacted_interaction['status'] == "T":
            return enacted_interaction

        # Head angle
        head_angle = 90
        if 'head_angle' in outcome:
            head_angle = outcome['head_angle']
        enacted_interaction['head_angle'] = head_angle

        # Azimuth
        if 'azimuth' in outcome:
            self.azimuth = outcome['azimuth']
        else:
            self.azimuth -= enacted_interaction['yaw']
        enacted_interaction['azimuth'] = self.azimuth

        # Presupposed displacement of the robot relative to the environment
        translation, yaw = [0, 0], 0
        if self.action == "1":
            yaw = 45
        if self.action == "2":
            translation[0] = -STEP_FORWARD_DISTANCE
        if self.action == "3":
            yaw = -45
        if self.action == "4":
            translation[1] = SHIFT_DISTANCE
        if self.action == "6":
            translation[1] = -SHIFT_DISTANCE
        if self.action == "8":
            translation[0] = STEP_FORWARD_DISTANCE # * outcome['duration'] / 1000

        # Actual measured yaw if any
        if 'yaw' in outcome:
            yaw = outcome['yaw']

        # interacting with phenomena
        obstacle, floor, shock, blocked, x, y = 0, 0, 0, 0, 0, 0
        echo_distance = 0

        if 'floor' in outcome:
            floor = outcome['floor']
        if 'shock' in outcome and self.action == '8' and floor == 0:
            shock = outcome['shock']
        if 'blocked' in outcome and self.action == '8' and floor == 0:
            blocked = outcome['blocked']
        if 'echo_distance' in outcome and self.action == "-" or self.action == "*" or self.action == "+":
            echo_distance = outcome['echo_distance']
            if echo_distance > 0:
                obstacle = 1

        # Interaction trespassing
        if floor > 0:
            # The position of the interaction trespassing
            x, y = LINE_X, 0
            # The resulting translation
            forward_duration = outcome['duration'] - 300  # Subtract retreat duration
            if self.action == "8":  # TODO Other actions
                translation[0] = STEP_FORWARD_DISTANCE * forward_duration / 1000 - RETREAT_DISTANCE
                if translation[0] < 0:
                    print("translation negative")
                if floor == 0b01:  # Black line on the right
                    translation[0] -= 0
                    translation[1] = RETREAT_DISTANCE_Y
                if floor == 0b10:  # Black line on the left
                    translation[0] -= 0
                    translation[1] = -RETREAT_DISTANCE_Y
            if self.action == "4":
                translation[0] = -RETREAT_DISTANCE
                translation[1] = SHIFT_DISTANCE * forward_duration / 1000
            if self.action == "6":
                translation[0] = -RETREAT_DISTANCE
                translation[1] = -SHIFT_DISTANCE * forward_duration / 1000

        # Interaction blocked
        if blocked:
            x, y = 110, 0

        # Interaction shock
        if shock == 0b01:
            x, y = 110, -80
        if shock == 0b11:
            x, y = 110, 0
        if shock == 0b10:
            x, y = 110, 80

        # Interaction ECHO
        if obstacle:
            x = int(ROBOT_HEAD_X + math.cos(math.radians(head_angle)) * echo_distance)
            y = int(math.sin(math.radians(head_angle)) * echo_distance)

        enacted_interaction['phenom_info'] = (floor, shock, blocked, obstacle, x, y)
        enacted_interaction['echo_distance'] = echo_distance

        # The displacement caused by this interaction
        enacted_interaction['translation'] = translation
        enacted_interaction['yaw'] = yaw
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(-math.radians(-enacted_interaction['yaw']))
        enacted_interaction['displacement_matrix'] = matrix44.multiply(rotation_matrix, translation_matrix)

        # Returning the enacted interaction
        print(enacted_interaction)
        return enacted_interaction


# Test the wifi interface by controlling the robot from the console
# Replace the IP address with your robot's IP address. Run :
# py -m Python.OsoyooControllerBSN.Wifi.RobotController <Robot's IP>
if __name__ == "__main__":
    ip = "192.168.1.11"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide our robot's IP address")
    print("Sending to robot at: " + ip)
    print("Select the terminal window and press command key. Press Q to exit.")

    controller = RobotController(ip)

    a = ""
    while True:
        print("Command key: ")
        a = keyboard.read_key().upper()
        if a == "Q":
            break
        controller.command_robot(a)
        while controller.enact_step < 2:
            time.sleep(0.1)
        controller.translate_robot_data()
