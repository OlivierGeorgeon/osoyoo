import json
from RobotDefine import *
import threading
from WifiInterface import WifiInterface
from Phenomenon import Phenomenon
import math
from OsoyooCar import OsoyooCar
from EgoMemoryWindow import EgoMemoryWindow
import pyglet


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
        self.outcome_string = ""

    def watch_outcome(self, dt):
        if self.enact_step == 2:
            print(self.outcome_string)
            outcome = json.loads(self.outcome_string)
            # floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

            # Presupposed displacement of the robot relative to the environment
            translation = [0, 0]
            rotation = 0
            if self.action == "1":
                rotation = 45
            if self.action == "2":
                translation[0] = -STEP_FORWARD_DISTANCE
            if self.action == "3":
                rotation = -45
            if self.action == "8":
                translation[0] = STEP_FORWARD_DISTANCE

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
                if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3":
                    # Create a new echo phenomenon
                    echo_distance = outcome['echo_distance']
                    print("Echo distance %i" % echo_distance)
                    x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                    y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                    obstacle = Phenomenon(x, y, self.view.batch)
                    self.phenomena.append(obstacle)
            self.enact_step = 0
            self.view.update_environment_matrix(translation, rotation)

    # Asynchronous interaction with the robot
    def enact(self, text):
        def enact_thread():
            print("Send " + self.action)
            self.outcome_string = self.wifiInterface.enact(self.action)
            print("Receive " + self.outcome_string)
            self.enact_step = 2

        self.action = text
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()


if __name__ == "__main__":
    emw = EgoMemoryWindow()
    controller = Controller(emw)

    @emw.event
    def on_text(text):
        if controller.enact_step == 0:
            if text == "/":  # Turn of the angle marked by the mouse click
                angle = int(math.degrees(math.atan2(emw.mouse_press_y, emw.mouse_press_x)))
                text = json.dumps({'action': '/', 'angle': angle})
            controller.enact(text)
        else:
            print("Waiting for previous outcome before sending new action")

    pyglet.clock.schedule_interval(controller.watch_outcome, 0.1)
    pyglet.app.run()
