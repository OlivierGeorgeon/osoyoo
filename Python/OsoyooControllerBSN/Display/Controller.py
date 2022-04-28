import sys
import json
from ..RobotDefine import *
import threading
from ..Wifi.WifiInterface import WifiInterface
from ..Display.Phenomenon import *
import math
from ..Display.OsoyooCar import OsoyooCar
from ..Display.EgoMemoryWindow import EgoMemoryWindow
from ..Display.ModalWindow import ModalWindow
import pyglet
from pyglet.window import key
from pyrr import matrix44


class Controller:
    def __init__(self, view: EgoMemoryWindow, robot_ip):
        # View
        self.view = view

        # Model
        self.wifiInterface = WifiInterface(robot_ip)
        self.phenomena = []
        self.robot = OsoyooCar(self.view.batch, self.view.background)

        self.action = ""
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0

        # Mouse press: select or unselect points
        def on_mouse_press(x, y, button, modifiers):
            self.mouse_press_x, self.mouse_press_y, self.mouse_press_angle = \
                self.view.set_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.phenomena:
                if p.is_near(self.mouse_press_x, self.mouse_press_y):
                    p.set_color("red")
                else:
                    p.set_color()

        # key press: delete selected points
        def on_key_press(symbol, modifiers):
            if symbol == key.DELETE:
                for p in self.phenomena:
                    if p.is_selected:
                        p.delete()
                        self.phenomena.remove(p)
            if symbol == key.INSERT:
                print("insert phenomenon")
                phenomenon = Phenomenon(self.mouse_press_x, self.mouse_press_y, self.view.batch, self.view.foreground, POINT_PHENOMENON)
                self.phenomena.append(phenomenon)

        self.view.push_handlers(on_mouse_press, on_key_press)

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

        # Translate and rotate all the phenomena
        for p in self.phenomena:
            p.displace(displacement_matrix)

        # Marker the new position
        position = Phenomenon(0, 0, self.view.batch, self.view.foreground, POINT_PLACE)
        self.phenomena.append(position)

        # Check if line detected
        if floor > 0:
            # Mark a new trespassing interaction
            line = Phenomenon(LINE_X, 0, self.view.batch, self.view.foreground, POINT_TRESPASS)
            self.phenomena.append(line)

        # Check for collision when moving forward
        if self.action == "8" and floor == 0:
            if blocked:
                # Create a new push interaction
                push = Phenomenon(110, 0, self.view.batch, self.view.foreground, POINT_PUSH)
                self.phenomena.append(push)
            else:
                # Create a new shock interaction
                if shock == 0b01:
                    wall = Phenomenon(110, -80, self.view.batch, self.view.foreground, POINT_SHOCK)
                    self.phenomena.append(wall)
                if shock == 0b11:
                    wall = Phenomenon(110, 0, self.view.batch, self.view.foreground, POINT_SHOCK)
                    self.phenomena.append(wall)
                if shock == 0b10:
                    wall = Phenomenon(110, 80, self.view.batch, self.view.foreground, POINT_SHOCK)
                    self.phenomena.append(wall)

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
                    echo = Phenomenon(x, y, self.view.batch, self.view.foreground, POINT_ECHO)
                    self.phenomena.append(echo)

        # Update the azimuth
        if 'azimuth' in outcome:
            self.view.azimuth = outcome['azimuth']


# Testing the controller by remote controlling the robot from the egocentric memory window
# Set the IP address. Run:
# py -m Python.OsoyooControllerBSN.Display.Controller <Robot's IP>
if __name__ == "__main__":
    ip = "192.168.4.1"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)
    emw = EgoMemoryWindow()
    controller = Controller(emw, ip)

    @emw.event
    def on_text(text):
        """ Receiving the action from the window and calling the controller to send the action to the robot """
        if text.upper() == "C":
            window = ModalWindow(controller.phenomena)
            return
        if controller.enact_step == 0:
            if text == "/":  # Send the angle marked by the mouse click
                # emw.on_text(text)
                text = json.dumps({'action': '/', 'angle': emw.mouse_press_angle})
            controller.enact(text)
        else:
            print("Waiting for previous outcome before sending new action")

    # Schedule the controller to watch for the outcome received from the robot
    pyglet.clock.schedule_interval(controller.watch_outcome, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()
