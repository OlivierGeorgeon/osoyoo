import sys
import json
import threading
import keyboard
from pyrr import matrix44, Quaternion
import math
from .. Misc.RobotDefine import *
from .. Misc.WifiInterface import WifiInterface
from .. Views.PointOfInterest import *
from .. Views.EgocentricView import EgocentricView
from .. Model.Memories.MemoryV1 import MemoryV1


class RobotController:
    def __init__(self, robot_ip):
        # Model
        self.wifiInterface = WifiInterface(robot_ip)
        self.points_of_interest = []

        self.action = ""
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

    def enact(self, text):
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            # print("Send " + self.action)
            self.outcome_bytes = self.wifiInterface.enact(self.action)
            print("Receive ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2
            # self.watch_outcome()

        self.action = text
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()

    def watch_outcome(self, dt):
        """ Watching for the reception of the outcome """
        if self.enact_step == 2:
            self.update_model()
            self.enact_step = 0

    def update_model(self):
        """ Updating the model from the latest received outcome """
        outcome = json.loads(self.outcome_bytes)

        # If timeout then no ego memory update
        if outcome['status'] == "T":
            print("No ego memory update")
            return

        floor = 0
        if 'floor' in outcome:
            floor = int(outcome['floor'])
        shock = 0
        if 'shock' in outcome:
            shock = outcome['shock']
        blocked = False
        if 'blocked' in outcome:
            blocked = outcome['blocked']

        # Presupposed displacement of the robot relative to the environment
        translation = [0, 0]
        rotation = 0
        if self.action == "1":
            rotation = 45
        if self.action == "2":
            translation[0] = -STEP_FORWARD_DISTANCE
        if self.action == "3":
            rotation = -45
        if self.action == "4":
            translation[1] = SHIFT_DISTANCE
        if self.action == "6":
            translation[1] = -SHIFT_DISTANCE
        if self.action == "8":
            if not blocked:
                # translation[0] = STEP_FORWARD_DISTANCE * outcome['duration'] / 1000
                translation[0] = STEP_FORWARD_DISTANCE

        # Actual measured displacement if any
        if 'yaw' in outcome:
            rotation = outcome['yaw']

        # Estimate displacement due to floor change retreat
        if floor > 0:  # Black line detected
            # Update the translation
            if self.action == "8":  # TODO Other actions
                forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted

        # The displacement matrix of this interaction
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(-math.radians(-rotation))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

        # Translate and rotate all the points of interest
        self.view.displace(displacement_matrix)

        # Marker the new position
        self.view.add_point_of_interest(0, 0, POINT_PLACE)

        # Check if line detected
        if floor > 0:
            # Mark a new trespassing interaction
            self.view.add_point_of_interest(LINE_X, 0, POINT_TRESPASS)

        # Check for collision when moving forward
        if self.action == "8" and floor == 0:
            if blocked:
                # Create a new push interaction
                self.view.add_point_of_interest(110, 0, POINT_PUSH)
            else:
                # Create a new shock interaction
                if shock == 0b01:
                    self.view.add_point_of_interest(110, -80, POINT_SHOCK)
                if shock == 0b11:
                    self.view.add_point_of_interest(110, 0, POINT_SHOCK)
                if shock == 0b10:
                    self.view.add_point_of_interest(110, 80, POINT_SHOCK)

        # Update head angle
        if 'head_angle' in outcome:
            head_angle = int(outcome['head_angle'])
            self.robot.rotate_head(head_angle)
            if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3":
                # Create a new echo phenomenon
                echo_distance = float(outcome['echo_distance'])
                if echo_distance > 0:  # echo measure 0 is false measure
                    x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                    y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                    self.view.add_point_of_interest(x, y, POINT_ECHO)

        # Update the azimuth
        if 'azimuth' in outcome:
            self.view.azimuth = outcome['azimuth']


# Testing the controller by remote controlling the robot from the egocentric memory window
# Set the IP address. Run:
# py -m stage_titouan.Controllers.RobotControllerOlivier "192.168.8.189"
if __name__ == "__main__":
    ip = "192.168.4.1"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)
    ev = EgocentricView()
    controller = RobotController(ip)

    _action = ""
    while True:
        print("Action key: ", end="")
        a = keyboard.read_key().upper()
        print()
        controller.enact('{"action":"' + a + '"}')
