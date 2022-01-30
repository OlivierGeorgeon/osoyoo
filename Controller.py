import json
from RobotDefine import *
import threading
from WifiInterface import WifiInterface
from Phenomenon import Phenomenon
import math
from OsoyooCar import OsoyooCar
from EgoMemoryWindow import EgoMemoryWindow
import pyglet
from pyrr import matrix44


class Controller:
    def __init__(self, view):
        # View
        self.view = view

        # Model
        self.wifiInterface = WifiInterface()
        self.phenomena = []
        self.robot = OsoyooCar(self.view.batch)

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
        blocked = False
        shock = 0
        # floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

        if outcome['status'] == "T":  # If timeout no ego memory update
            print("No ego memory update")
        else:
            if 'blocked' in outcome:
                blocked = outcome['blocked']
            if 'shock' in outcome:
                shock = outcome['shock']

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
                    translation[0] = STEP_FORWARD_DISTANCE * outcome['duration'] / 1000

            # Actual measured displacement if any
            if 'yaw' in outcome:
                rotation = outcome['yaw']

            # Estimate displacement due to floor change retreat
            if 'floor' in outcome:
                if outcome['floor'] > 0:  # Black line detected
                    # Update the translation
                    if self.action == "8":  # TODO Other actions
                        forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                        translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted

            # The displacement matrix of this interaction
            translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
            rotation_matrix = matrix44.create_from_z_rotation(-math.radians(-rotation))
            displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

            # Translate and rotate all the phenomena
            for p in self.phenomena:
                p.translate(translation)
                p.rotate(rotation)
                # p.displace(displacement_matrix) # not working yet

            # The phenomenon line
            if 'floor' in outcome:
                if outcome['floor'] > 0:  # Black line detected
                    # Create a new floor-changed phenomenon
                    line = Phenomenon(150, 0, self.view.batch, 1)  # the translation will be reapplied
                    self.phenomena.append(line)

            # The phenomenon wall
            if self.action == "8":
                if blocked:
                    wall = Phenomenon(110, 0, self.view.batch, 2)
                    self.phenomena.append(wall)
                else:
                    if shock == 0b01:
                        wall = Phenomenon(110, -80, self.view.batch, 2)
                        self.phenomena.append(wall)
                    if shock == 0b11:
                        wall = Phenomenon(110, 0, self.view.batch, 2)
                        self.phenomena.append(wall)
                    if shock == 0b10:
                        wall = Phenomenon(110, 80, self.view.batch, 2)
                        self.phenomena.append(wall)

            # Update head angle
            if 'head_angle' in outcome:
                head_angle = outcome['head_angle']
                self.robot.rotate_head(head_angle)
                if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3":
                    # Create a new echo phenomenon
                    echo_distance = outcome['echo_distance']
                    if echo_distance > 0:  # echo measure 0 is false measure
                        print("Echo distance %i" % echo_distance)
                        x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                        y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                        obstacle = Phenomenon(x, y, self.view.batch)
                        self.phenomena.append(obstacle)

            # Update the azimuth
            if 'azimuth' in outcome:
                self.view.azimuth = outcome['azimuth']

            # Update the origin
            self.view.update_environment_matrix(displacement_matrix)


# Testing the controller by remote controlling the robot from the egocentric memory window
if __name__ == "__main__":
    emw = EgoMemoryWindow()
    controller = Controller(emw)

    @emw.event
    def on_text(text):
        """ Receiving the action from the window and calling the controller to send the action to the robot """
        if controller.enact_step == 0:
            if text == "/":  # Send the angle marked by the mouse click
                text = json.dumps({'action': '/', 'angle': emw.mouse_press_angle})
            controller.enact(text)
        else:
            print("Waiting for previous outcome before sending new action")

    # Schedule the controller to watch for the outcome received from the robot
    pyglet.clock.schedule_interval(controller.watch_outcome, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()
