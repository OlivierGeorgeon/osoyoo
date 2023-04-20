import json
import time
import socket
import math
import numpy as np
from pyrr import matrix44
from .RobotDefine import RETREAT_DISTANCE, RETREAT_DISTANCE_Y, LINE_X, ROBOT_FRONT_X, ROBOT_FRONT_Y, ROBOT_HEAD_X
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR, EXPERIENCE_IMPACT, \
    EXPERIENCE_LOCAL_ECHO, EXPERIENCE_BLOCK
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_RIGHTWARD, ACTION_LEFTWARD

# ENACT_STEP_IDLE = 0
# ENACT_STEP_ENACTING = 1
INTERACTION_STEP_INTENDING = 2
INTERACTION_STEP_ENACTING = 3

KEY_EXPERIENCES = 'points'
KEY_IMPACT = 'impact'

FOCUS_MAX_DELTA = 100  # (mm) Maximum delta to keep focus
# ENACTION_DEFAULT_TIMEOUT = 6  # Seconds


class CtrlRobot:
    """The interface between the Workspace and the robot"""

    def __init__(self, robot_ip, workspace):

        self.robot_ip = robot_ip
        self.workspace = workspace
        self.port = 8888
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.robot_ip, self.port))  # Not necessary for UDP
        self.socket.settimeout(0)

        # Class variables used in an asynchronous Thread
        # self.enact_step = ENACT_STEP_IDLE
        self.expected_outcome_time = 0.

    def main(self, dt):
        """The main handler of the communication to and from the robot."""
        # If the robot is idle, check for an intended interaction in the workspace and send it to the robot
        # if self.enact_step == ENACT_STEP_IDLE:
        if self.workspace.interaction_step == INTERACTION_STEP_INTENDING:
            self.workspace.interaction_step = INTERACTION_STEP_ENACTING
            # enaction = self.workspace.intended_enaction
            # if enaction is not None:
            self.send_enaction_to_robot(self.workspace.intended_enaction)
            # self.enact_step = ENACT_STEP_ENACTING

        # While the robot is enacting the interaction, check for the outcome
        if self.workspace.interaction_step == INTERACTION_STEP_ENACTING:
            # if self.enact_step == ENACT_STEP_ENACTING:
            if time.time() < self.expected_outcome_time:
                try:
                    outcome, address = self.socket.recvfrom(512)
                    if outcome is not None:  # Sometimes it receives a None outcome. I don't know why
                        print()
                        print("Receive:", outcome)
                        self.send_enacted_interaction_to_workspace(outcome)
                        # self.enact_step = ENACT_STEP_IDLE  # Now we have received the outcome from the robot
                except socket.timeout:   # Time out error if outcome not yet received
                    print(".", end='')
                except OSError as e:
                    if e.args[0] == 10035:
                        print(".", end='')
                    else:
                        print(e)
                # except socket.error as error:
                #     print(error)
            else:
                self.send_enacted_interaction_to_workspace(b'{"status":"T"}')
                print("Receive: No outcome")
                # self.enact_step = ENACT_STEP_IDLE

    def send_enaction_to_robot(self, enaction):
        """Send the enaction string to the robot and set the timeout"""
        enaction_string = enaction.serialize()
        print("Sending: " + enaction_string)

        # Send the intended interaction string to the robot
        self.socket.sendto(bytes(enaction_string, 'utf-8'), (self.robot_ip, self.port))

        # Initialize the timeout
        self.expected_outcome_time = time.time() + enaction.timeout()

    def send_enacted_interaction_to_workspace(self, outcome):
        """ Computes the enacted interaction from the robot's outcome data."""
        enacted_interaction = json.loads(outcome)

        enacted_interaction[KEY_EXPERIENCES] = []

        # If timeout then we consider that there was no enacted interaction
        if enacted_interaction['status'] == "T":
            self.workspace.update_enacted_interaction(enacted_interaction)
            return

        # Translation integrated from the action's speed multiplied by the duration1
        action_code = enacted_interaction['action']
        translation = self.workspace.actions[action_code].translation_speed * (enacted_interaction['duration1'] / 1000)

        # Yaw presupposed or returned by the robot
        yaw = self.workspace.actions[action_code].target_duration * self.workspace.actions[action_code].rotation_speed_rad
        if 'yaw' in enacted_interaction:
            yaw = enacted_interaction['yaw']
        else:
            enacted_interaction['yaw'] = yaw

        # If the robot does not return the azimuth then return 0. The azimuth will be computed by BodyMemory
        if 'azimuth' not in enacted_interaction:
            enacted_interaction['azimuth'] = 0

        # If the robot returns compass_x and compass_y then recompute the azimuth
        # (They differ if the compass offset has been adjusted)
        if 'compass_x' in enacted_interaction:
            # Subtract the offset from robot_define.py
            enacted_interaction['compass_x'] -= self.workspace.memory.body_memory.compass_offset[0]
            enacted_interaction['compass_y'] -= self.workspace.memory.body_memory.compass_offset[1]
            azimuth = math.degrees(math.atan2(enacted_interaction['compass_y'], enacted_interaction['compass_x']))
            # The compass point indicates the south so we must rotate it of 180° to obtain the azimuth
            azimuth = round(azimuth + 180) % 360
            enacted_interaction['azimuth'] = azimuth

        # Interaction Floor line
        if enacted_interaction['floor'] > 0:
            enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_FLOOR, LINE_X, 0))
            # Update the x translation
            translation[0] -= RETREAT_DISTANCE
            # Set the y translation
            if enacted_interaction['floor'] == 0b01:  # Black line on the right
                translation[1] = RETREAT_DISTANCE_Y
            if enacted_interaction['floor'] == 0b10:  # Black line on the left
                translation[1] = -RETREAT_DISTANCE_Y

        # Interaction ECHO for actions involving scanning
        echo_point = [0, 0, 0]
        # if action_code in ['-', '*', '+', '8', '2', '1', '3', '4', '6']:
        echo_point[0] = round(ROBOT_HEAD_X + math.cos(math.radians(enacted_interaction['head_angle']))
                              * enacted_interaction['echo_distance'])
        echo_point[1] = round(math.sin(math.radians(enacted_interaction['head_angle']))
                              * enacted_interaction['echo_distance'])
        if enacted_interaction['echo_distance'] < 10000:
            enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_ALIGNED_ECHO, *echo_point))
        # Return the echo_xy to possibly use as focus
        enacted_interaction['echo_xy'] = echo_point

        # Interaction impact
        # (The forward translation is already correct since it is integrated during duration1)
        if KEY_IMPACT in enacted_interaction and action_code == ACTION_FORWARD:
            if enacted_interaction[KEY_IMPACT] == 0b01:  # Impact on the right
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, -ROBOT_FRONT_Y))
            if enacted_interaction[KEY_IMPACT] == 0b11:  # Impact on the front
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, 0))
            if enacted_interaction[KEY_IMPACT] == 0b10:  # Impact on the left
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, ROBOT_FRONT_Y))

        # Interaction blocked
        if 'blocked' in enacted_interaction and action_code == ACTION_FORWARD:
            if enacted_interaction['blocked']:
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_BLOCK, ROBOT_FRONT_X, 0))
                translation = np.array([0, 0, 0], dtype=float)  # Reset the translation

        # The estimated displacement of the environment relative to the robot caused by this interaction
        translation_matrix = matrix44.create_from_translation(-translation)
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

        # # If focussed then adjust the displacement
        # if self.workspace.memory.egocentric_memory.focus_point is not None:
        #     # The new estimated position of the focus point
        #     # prediction_focus_point = matrix44.apply_to_vector(displacement_matrix, self.workspace.memory.egocentric_memory.focus_point)
        #     # The error between the expected and the actual position of the echo
        #     # prediction_error_focus = prediction_focus_point - echo_point
        #     # The focus displacement was simulated in egocentric memory
        #     prediction_error_focus = self.workspace.memory.egocentric_memory.focus_point - echo_point
        #
        #     # if math.dist(echo_point, prediction_focus_point) < FOCUS_MAX_DELTA:
        #     if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA:
        #         # The focus has been kept
        #         enacted_interaction['focus'] = True
        #         # If the action has been completed
        #         if enacted_interaction['duration1'] >= 1000:
        #             # If the head is forward then correct longitudinal displacements
        #             if -20 < enacted_interaction['head_angle'] < 20:
        #                 if action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
        #                     translation[0] = translation[0] + prediction_error_focus[0]
        #                     self.workspace.actions[action_code].adjust_translation_speed(translation)
        #             # If the head is sideways then correct lateral displacements
        #             if 60 < enacted_interaction['head_angle'] or enacted_interaction['head_angle'] < -60:
        #                 if action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
        #                     translation[1] = translation[1] + prediction_error_focus[1]
        #                     self.workspace.actions[action_code].adjust_translation_speed(translation)
        #             # Update the displacement matrix according to the new translation
        #             translation_matrix = matrix44.create_from_translation(-translation)
        #             displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        #     else:
        #         # The focus has been lost
        #         # enacted_interaction['lost_focus'] = True
        #         print("Lost focus with prediction error:", prediction_error_focus)

        # Return the displacement
        enacted_interaction['translation'] = translation
        enacted_interaction['rotation_matrix'] = rotation_matrix
        enacted_interaction['displacement_matrix'] = displacement_matrix

        # The echo array
        if "echo_array" not in enacted_interaction:
            enacted_interaction["echo_array"] = []
        # Compute the position of each echo point in the echo array
        for i in range(100, -99, -5):
            ed_str = "ed"+str(i)
            if ed_str in enacted_interaction:
                ha = i
                ed = enacted_interaction[ed_str]
                tmp_x = ROBOT_HEAD_X + math.cos(math.radians(ha)) * ed
                tmp_y = math.sin(math.radians(ha)) * ed
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_LOCAL_ECHO, tmp_x, tmp_y))
        # print(enacted_interaction)

        self.workspace.update_enacted_interaction(enacted_interaction)
