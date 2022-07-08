import json
import math
import numpy
import threading
from pyrr import matrix44
from stage_titouan.Robot.RobotDefine import *
from stage_titouan.Robot.WifiInterface import WifiInterface
from stage_titouan.Memory.EgocentricMemory.Interactions.Interaction import *

class CtrlRobot:
    """Made to work with CtrlWorkspace"""
    def __init__(self,ctrl_workspace,robot_ip):
        self.ctrl_workspace = ctrl_workspace
        self.wifiInterface = WifiInterface(robot_ip)

        self.intended_interaction = {'action': "8"}  # Need random initialization

        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout
        self.azimuth = 0

        self.robot_has_started_acting = False
        self.robot_has_finished_acting =False
        self.enacted_interaction = {}
        self.forward_speed = [FORWARD_SPEED, 0]
        self.backward_speed = [-FORWARD_SPEED, 0]
        self.leftward_speed = [0, LATERAL_SPEED]
        self.rightward_speed = [0, -LATERAL_SPEED]


    def main(self,dt):
        """Handle the communications with the robot."""
        if self.enact_step == 2:
            self.robot_has_started_acting = False
            self.robot_has_finished_acting = True
            self.enact_step = 0
        if self.robot_has_finished_acting:
            self.robot_has_finished_acting = False
            self.enacted_interaction = self.translate_robot_data()
            self.ctrl_workspace.enacted_interaction = self.enacted_interaction
            self.ctrl_workspace.f_new_interaction_done = True
            self.ctrl_workspace.f_interaction_to_enact_ready = False  # OG
        if self.ctrl_workspace.f_interaction_to_enact_ready and not self.robot_has_started_acting:
            print("LAAAAAAAAAAAAAA")
            self.command_robot(self.ctrl_workspace.interaction_to_enact)
            self.ctrl_workspace.interaction_to_enact = None
            self.robot_has_started_acting = True
            # self.ctrl_workspace.f_interaction_to_enact_ready = False  # OG
            
    
    def command_robot(self, intended_interaction):
        """ Creating an asynchronous thread to send the command to the robot and to wait for the outcome """
        self.outcome_bytes = "Waiting"

        def enact_thread():
            """ Sending the command to the robot and waiting for the outcome """
            action_string = json.dumps(self.intended_interaction)
            print("Sending: " + action_string)
            self.outcome_bytes = self.wifiInterface.enact(action_string)
            print("Receive: ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2  # Now we have received the outcome from the robot

        # self.action = action
        self.intended_interaction = intended_interaction
        self.enact_step = 1  # Now we send the command to the robot for enaction
        thread = threading.Thread(target=enact_thread)
        thread.start()

    def translate_robot_data(self):
        """ Computes the enacted interaction from the robot's outcome data """
        action = self.intended_interaction['action']
        is_focussed = ('focus_x' in self.intended_interaction)  # The focus point was sent to the robot
        enacted_interaction = json.loads(self.outcome_bytes)
        enacted_interaction['points'] = []

        # If timeout then we consider that there was no enacted interaction
        if enacted_interaction['status'] == "T":
            return enacted_interaction

        # Presupposed displacement of the robot relative to the environment
        translation, yaw = [0, 0], 0
        if action == "1":
            yaw = DEFAULT_YAW
        if action == "2":
            # translation = self.backward_speed * (enacted_interaction['duration1'] / 1000)
            translation = [i * enacted_interaction['duration1'] / 1000 for i in self.backward_speed]
        if action == "3":
            yaw = -DEFAULT_YAW
        if action == "4":
            # translation = self.leftward_speed * (enacted_interaction['duration1'] / 1000)
            translation = [i * enacted_interaction['duration1'] / 1000 for i in self.leftward_speed]
        if action == "6":
            # translation = self.rightward_speed * (enacted_interaction['duration1'] / 1000)
            translation = [i * enacted_interaction['duration1'] / 1000 for i in self.rightward_speed]
        if action == "8":
            # translation = self.forward_speed * (enacted_interaction['duration1'] / 1000)
            translation = [i * enacted_interaction['duration1'] / 1000 for i in self.forward_speed]

        # If the robot returns yaw then use it
        if 'yaw' in enacted_interaction:
            yaw = enacted_interaction['yaw']
        else:
            enacted_interaction['yaw'] = yaw

        # If the robot does not return the azimuth then sum it from the yaw
        if 'azimuth' not in enacted_interaction:
            self.azimuth -= yaw  # yaw is counterclockwise, azimuth is clockwise
            enacted_interaction['azimuth'] = self.azimuth

        # If the robot returns compass_x and compass_y then recompute the azimuth
        if 'compass_x' in enacted_interaction:
            # Subtract the offset from robot_define.py
            enacted_interaction['compass_x'] -= COMPASS_X_OFFSET
            enacted_interaction['compass_y'] -= COMPASS_Y_OFFSET
            self.azimuth = math.degrees(math.atan2(enacted_interaction['compass_y'], enacted_interaction['compass_x']))
            self.azimuth += 180;
            if self.azimuth >= 360:
                self.azimuth -= 360
            # Override the azimuth returned by the robot
            enacted_interaction['azimuth'] = int(self.azimuth)
            print("compass_x", enacted_interaction['compass_x'], "compass_y", enacted_interaction['compass_y'], "azimuth", int(self.azimuth))

        # Interaction trespassing
        if enacted_interaction['floor'] > 0:
            enacted_interaction['points'].append((INTERACTION_TRESPASSING, LINE_X, 0))
            # The resulting translation
            translation[0] -= RETREAT_DISTANCE
            if enacted_interaction['floor'] == 0b01:  # Black line on the right
                translation[1] = RETREAT_DISTANCE_Y
            if enacted_interaction['floor'] == 0b10:  # Black line on the left
                translation[1] = -RETREAT_DISTANCE_Y

        # Interaction ECHO for actions involving scanning
        echo_xy = [0, 0]
        if action in ['-', '*', '+', '8', '2', '1', '3', '4', '6']:
            if enacted_interaction['echo_distance'] < 10000:
                echo_xy[0] = int(ROBOT_HEAD_X + math.cos(math.radians(enacted_interaction['head_angle']))
                                 * enacted_interaction['echo_distance'])
                echo_xy[1] = int(math.sin(math.radians(enacted_interaction['head_angle']))
                                 * enacted_interaction['echo_distance'])
                enacted_interaction['points'].append((INTERACTION_ECHO, *echo_xy)) 
                # Return the echo_xy to possibly use as focus
                enacted_interaction['echo_xy'] = echo_xy

        # Interaction shock
        if 'shock' in enacted_interaction and action == '8':
            if enacted_interaction['shock'] == 0b01:  # Shock on the right
                enacted_interaction['points'].append((INTERACTION_SHOCK, ROBOT_FRONT_X, -ROBOT_FRONT_Y))
            if enacted_interaction['shock'] == 0b11:  # Shock on the front
                enacted_interaction['points'].append((INTERACTION_SHOCK, ROBOT_FRONT_X, 0))
            if enacted_interaction['shock'] == 0b10:  # Shock on the left
                enacted_interaction['points'].append((INTERACTION_SHOCK, ROBOT_FRONT_X, ROBOT_FRONT_Y))

        # Interaction block
        if 'blocked' in enacted_interaction and action == '8':
            if enacted_interaction['blocked']:
                enacted_interaction['points'].append((INTERACTION_BLOCK, ROBOT_FRONT_X, 0))
                translation[0] = 0  # Cancel forward translation

        # The estimated displacement of the environment relative to the robot caused by this interaction
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

        # If focussed then adjust the displacement
        if is_focussed:
            # The new estimated position of the focus point
            expected_focus_xy = matrix44.apply_to_vector(displacement_matrix,
                                                         [self.intended_interaction['focus_x'],
                                                          self.intended_interaction['focus_y'], 0])[0:2]
            # The distance between the echo and the expected focus position
            distance = int(math.dist(echo_xy, expected_focus_xy))
            print("Distance between echo and focus:", distance)
            if distance < 100:
                additional_xy = expected_focus_xy - echo_xy
                print("additional translation:", additional_xy)
                # The focus has been kept
                enacted_interaction['focus'] = True
                # Adjust the displacement
                translation += additional_xy
                translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
                displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                # Adjust the speed
                if action == '8' and enacted_interaction['duration1'] >= 1000:
                    self.forward_speed = (self.forward_speed + translation) / 2
                    print("New forward speed:", self.forward_speed)
                if action == '2' and enacted_interaction['duration1'] >= 1000:
                    self.backward_speed = (self.backward_speed + translation) / 2
                    print("New backward speed:", self.backward_speed)
                if action == '4' and enacted_interaction['duration1'] >= 1000:
                    self.leftward_speed = (self.leftward_speed + translation) / 2
                    print("New leftward speed:", self.leftward_speed)
                if action == '6' and enacted_interaction['duration1'] >= 1000:
                    self.rightward_speed = (self.rightward_speed + translation) / 2
                    print("New rightward speed:", self.rightward_speed)
            else:
                print("Lost focus with distance:", distance)

        # Return the displacement
        enacted_interaction['translation'] = translation
        enacted_interaction['displacement_matrix'] = displacement_matrix

        # The echo array
        enacted_interaction["echo_array"] = [] if not "echo_array" in enacted_interaction.keys() else enacted_interaction["echo_array"]
        for i in range(100,-99,-5):
                    edstr = "ed"+str(i)

                    if edstr in enacted_interaction:
                        ha =i
                        ed = enacted_interaction[edstr]
                        tmp_x = ROBOT_HEAD_X + math.cos(math.radians(ha)) * ed
                        tmp_y = math.sin(math.radians(ha)) * ed
                        enacted_interaction['echo_array'].append((tmp_x, tmp_y))

        self.enacted_interaction = enacted_interaction

        return enacted_interaction
