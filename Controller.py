import json
from RobotDefine import *
import threading
from WifiInterface import WifiInterface
from Phenomenon import Phenomenon
import math
from OsoyooCar import OsoyooCar


class Controller:
    def __init__(self, view):
        # View
        self.view = view

        # Model
        self.wifiInterface = WifiInterface()
        self.phenomena = []
        self.robot = OsoyooCar(self.view.batch)

        self.async_action = ""
        self.async_flag = 0
        self.async_outcome_string = ""

    def process_outcome(self, text, outcome_string):
        outcome = json.loads(outcome_string)
        # floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

        # Presupposed displacement of the robot relative to the environment
        translation = [0, 0]
        rotation = 0
        if text == "1":
            rotation = 45
        if text == "2":
            translation[0] = -STEP_FORWARD_DISTANCE
        if text == "3":
            rotation = -45
        if text == "8":
            translation[0] = STEP_FORWARD_DISTANCE

        # Actual measured displacement if any
        if 'yaw' in outcome:
            rotation = outcome['yaw']

        # Estimate displacement due to floor change retreat
        if 'floor' in outcome:
            if outcome['floor'] > 0:  # Black line detected
                # Update the translation
                if text == "8":  # TODO Other actions
                    forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted
                # Create a new floor-changed phenomenon
                obstacle = Phenomenon(150 + translation[0], 0, self.view.batch, 1)  # the translation will be reapplied
                self.phenomena.append(obstacle)

        # Translate and rotate all the phenomena
        for p in self.phenomena:
            p.translate(translation)
            p.rotate(rotation)

        # Update head angle
        if 'head_angle' in outcome:
            head_angle = outcome['head_angle']
            self.robot.rotate_head(head_angle)
            if text == "-" or text == "*" or text == "1" or text == "3":
                # Create a new echo phenomenon
                echo_distance = outcome['echo_distance']
                print("Echo distance %i" % echo_distance)
                x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                obstacle = Phenomenon(x, y, self.view.batch)
                self.phenomena.append(obstacle)
        self.view.update_environment_matrix(translation, rotation)

    # Asynchronous interaction with the robot
    def async_action_trigger(self, text):
        def async_action(controller: Controller):
            print("Send " + self.async_action)
            controller.async_outcome_string = controller.wifiInterface.enact(self.async_action)
            print("Receive ", end="")
            print(controller.async_outcome_string)
            controller.async_flag = 2

        self.async_action = text
        self.async_flag = 1
        thread = threading.Thread(target=async_action, args=[self])
        thread.start()

