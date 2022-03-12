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
        self.azimuth = 0

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


    ########################################################################
    def decay_test(self):
        """Test de decay sur la vue
        Return: Nombre d'éléments qui doivent être enlevés de la vue
        Author: TKnockaert
        
        to_remove = list()
        for pheno in self.phenomena:                        
            pheno.decay()
            if(not pheno.isAlive()):
                to_remove = to_remove.append(pheno)
        out = 1#len(to_remove)
        for to_be_removed in to_remove:
            self.phenomena.remove(to_be_removed)

        return out
        """
    ########################################################################
    def update_model(self):
        """ Updating the model from the latest received outcome """
        outcome = json.loads(self.outcome_bytes)
        floor = 0
        if 'floor' in outcome:
            floor = outcome['floor']
        shock = 0
        if 'shock' in outcome:
            shock = outcome['shock']
        blocked = False
        if 'blocked' in outcome:
            blocked = outcome['blocked']

        # floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

        if outcome['status'] == "T":  # If timeout no ego memory update
            print("No ego memory update")
        else:
            # Presupposed displacement of the robot relative to the environment
            translation = [0, 0]
            yaw = 0
            if self.action == "1":
                yaw = DEFAULT_YAW
            if self.action == "2":
                translation[0] = -STEP_FORWARD_DISTANCE
            if self.action == "3":
                yaw = -DEFAULT_YAW
            if self.action == "4":
                translation[1] = SHIFT_DISTANCE
            if self.action == "6":
                translation[1] = -SHIFT_DISTANCE
            if self.action == "8":
                if not blocked:
                    translation[0] = STEP_FORWARD_DISTANCE * outcome['duration'] / 1000

            # Actual measured displacement if any
            if 'yaw' in outcome:
                yaw = outcome['yaw']

            # Estimate displacement due to floor change retreat
            if floor > 0:  # Black line detected
                # Update the translation
                if self.action == "8":  # TODO Other actions
                    forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted

            # The displacement matrix of this interaction
            translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
            rotation_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
            displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

            # Translate and rotate all the phenomena
            for p in self.phenomena:
                p.displace(displacement_matrix)

            # Check if line detected
            if floor > 0:
                # Create a new lane crossing interaction
                line = Phenomenon(150, 0, self.view.batch, 1)  # the translation will be reapplied
                self.phenomena.append(line)

            # Check for collision when moving forward
            if self.action == "8" and floor == 0:
                if blocked:
                    # Create a new pressing interaction
                    wall = Phenomenon(ROBOT_FRONT_X, 0, self.view.batch, 2, 1)
                    self.phenomena.append(wall)
                else:
                    # Create a new blocked interaction
                    if shock == 0b01:
                        wall = Phenomenon(ROBOT_FRONT_X, -ROBOT_FRONT_Y, self.view.batch, 2)
                        self.phenomena.append(wall)
                    if shock == 0b11:
                        wall = Phenomenon(ROBOT_FRONT_X, 0, self.view.batch, 2)
                        self.phenomena.append(wall)
                    if shock == 0b10:
                        wall = Phenomenon(ROBOT_FRONT_X, ROBOT_FRONT_Y, self.view.batch, 2)
                        self.phenomena.append(wall)

            # Update head angle
            if 'head_angle' in outcome:
                head_angle = outcome['head_angle']
                self.view.robot.rotate_head(head_angle)
                if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3":
                    # Create a new echo phenomenon
                    echo_distance = outcome['echo_distance']
                    if echo_distance > 0:  # echo measure 0 is false measure
                        x = ROBOT_HEAD_X + math.cos(math.radians(head_angle)) * echo_distance
                        y = math.sin(math.radians(head_angle)) * echo_distance
                        obstacle = Phenomenon(x, y, self.view.batch, durability = 3, decayIntensity = 1 ) # TEST DURABILITY-DECAY
                        self.phenomena.append(obstacle)

            # Update the azimuth
            if 'azimuth' in outcome:
                self.view.azimuth = outcome['azimuth']
            else:
                self.azimuth -= yaw
            self.view.azimuth = self.azimuth

            # Update the origin
            self.view.update_environment_matrix(displacement_matrix)



                



# Testing the controller by remote controlling the robot from the egocentric memory window
if __name__ == "__main__":
    emw = EgoMemoryWindow()
    controller = Controller(emw)

    # emw2 = EgoMemoryWindow()
    # emw2.set_caption("Alocentric spatial memory")

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
