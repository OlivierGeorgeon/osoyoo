import json
import time
import socket
import math
import numpy as np
from pyrr import matrix44
from .RobotDefine import RETREAT_DISTANCE, RETREAT_DISTANCE_Y, LINE_X, ROBOT_FRONT_X, ROBOT_FRONT_Y, ROBOT_HEAD_X
from .Enaction import Enaction
from .Color import category_color
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR, EXPERIENCE_IMPACT, \
    EXPERIENCE_LOCAL_ECHO, EXPERIENCE_BLOCK
from ..Decider.Action import ACTION_FORWARD

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_INTENDING = 1
INTERACTION_STEP_ENACTING = 2
INTERACTION_STEP_INTEGRATING = 3
INTERACTION_STEP_REFRESHING = 4

KEY_EXPERIENCES = 'points'
KEY_IMPACT = 'impact'

FOCUS_MAX_DELTA = 100  # (mm) Maximum delta to keep focus


class CtrlRobot:
    """The interface between the Workspace and the robot"""

    def __init__(self, robot_ip, workspace):

        self.robot_ip = robot_ip
        self.workspace = workspace
        self.port = 8888
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.robot_ip, self.port))  # Not necessary for UDP
        self.socket.settimeout(0)
        self.expected_outcome_time = 0.

    def main(self, dt):
        """The main handler of the communication to and from the robot."""
        # If INTENDING then send the interaction to the robot
        if self.workspace.interaction_step == INTERACTION_STEP_INTENDING:
            self.workspace.interaction_step = INTERACTION_STEP_ENACTING
            self.send_enaction_to_robot()

        # While the robot is enacting the interaction, check for the outcome
        if self.workspace.interaction_step == INTERACTION_STEP_ENACTING and not self.workspace.is_imagining:
            if time.time() < self.expected_outcome_time:
                outcome_string = None
                try:
                    outcome_string, _ = self.socket.recvfrom(512)
                except socket.timeout:   # Time out error if outcome not yet received
                    print(".", end='')
                except OSError as e:
                    if e.args[0] == 10035:
                        print(".", end='')
                    else:
                        print(e)
                if outcome_string is not None:  # Sometimes it receives a None outcome. I don't know why
                    print()
                    print("Receive:", outcome_string)
                    # Short outcome are for debug
                    if len(outcome_string) > 100:
                        self.send_enacted_interaction_to_workspace(outcome_string)
            else:
                # Timeout: resend the enaction
                self.workspace.memory = self.workspace.memory_snapshot
                self.workspace.interaction_step = INTERACTION_STEP_IDLE
                print("Timeout")

    def send_enaction_to_robot(self):
        """Send the enaction string to the robot and set the timeout"""
        enaction_string = self.workspace.intended_enaction.serialize()
        print("Sending:", enaction_string)

        # Send the intended interaction string to the robot
        self.socket.sendto(bytes(enaction_string, 'utf-8'), (self.robot_ip, self.port))

        # Initialize the timeout
        self.expected_outcome_time = time.time() + self.workspace.intended_enaction.timeout()

    def send_enacted_interaction_to_workspace(self, outcome_string):
        """ Computes the enacted interaction from the robot's outcome data."""
        outcome = json.loads(outcome_string)
        action_code = outcome['action']

        enacted_enaction = Enaction(self.workspace.actions[action_code], outcome['clock'], None, None)

        # Translation integrated from the action's speed multiplied by the duration1
        translation = self.workspace.actions[action_code].translation_speed * (float(outcome['duration1']) / 1000.0)
        # TODO Take the yaw into account

        # Yaw presupposed or returned by the robot
        yaw = self.workspace.actions[action_code].target_duration \
              * math.degrees(self.workspace.actions[action_code].rotation_speed_rad)
        if 'yaw' in outcome:
            yaw = outcome['yaw']
        enacted_enaction.yaw = yaw

        # If the robot does not return the azimuth then return 0. The azimuth will be computed by BodyMemory
        if 'azimuth' in outcome:
            enacted_enaction.azimuth = outcome['azimuth']

        # If the robot returns compass_x and compass_y then recompute the azimuth
        # (They differ if the compass offset has been adjusted)
        if 'compass_x' in outcome:
            # Subtract the offset from robot_define.py
            compass_x = outcome['compass_x'] - self.workspace.memory.body_memory.compass_offset[0]
            compass_y = outcome['compass_y'] - self.workspace.memory.body_memory.compass_offset[1]
            # The compass point indicates the south so we must rotate it of 180° to obtain the azimuth
            enacted_enaction.azimuth = round(math.degrees(math.atan2(compass_y, compass_x)) + 180) % 360
            enacted_enaction.compass_point = np.array([compass_x, compass_y, 0], dtype=int)

        # Interaction Floor line
        if outcome['floor'] > 0:
            # Update the translation
            if outcome['floor'] == 0b01:
                # Black line on the right
                translation += [-RETREAT_DISTANCE, RETREAT_DISTANCE_Y, 0]
            elif outcome['floor'] == 0b10:
                # Black line on the left
                translation += [-RETREAT_DISTANCE, -RETREAT_DISTANCE_Y, 0]
            else:
                # Black line on the front
                translation += [-RETREAT_DISTANCE, 0, 0]

        # Interaction ECHO
        if outcome['echo_distance'] < 10000:
            x = ROBOT_HEAD_X + math.cos(math.radians(outcome['head_angle'])) * outcome['echo_distance']
            y = math.sin(math.radians(outcome['head_angle'])) * outcome['echo_distance']
            enacted_enaction.echo_point = np.array([x, y, 0], dtype=int)

        # Interaction impact
        # (The forward translation is already correct since it is integrated during duration1)

        # Interaction blocked
        # (The forward translation is already correct since it is integrated during duration1)

        # The estimated displacement of the environment relative to the robot caused by this interaction
        translation_matrix = matrix44.create_from_translation(-translation)
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        # https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/geometry/geo-tran.html#:~:text=A%20rotation%20matrix%20and%20a,rotations%20followed%20by%20a%20translation.
        # Multiply the rotation by the translation results in simply adding the translation values to the matrix.
        # The point will be rotated around origin and then the translation will be added
        # displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)  # Historic Version
        # Multiply the translation by the rotation will compute a matrix
        # that will first translate the point and then rotate it around it new origin
        # This better processes floor retreat
        displacement_matrix = matrix44.multiply(translation_matrix, rotation_matrix)  # Try translate and then rotate

        # Return the displacement
        outcome['translation'] = translation
        enacted_enaction.translation = translation
        outcome['rotation_matrix'] = rotation_matrix
        enacted_enaction.rotation_matrix = rotation_matrix
        outcome['displacement_matrix'] = displacement_matrix
        enacted_enaction.displacement_matrix = displacement_matrix
        enacted_enaction.duration1 = outcome['duration1']
        enacted_enaction.head_angle = outcome['head_angle']
        if 'floor' in outcome:
            enacted_enaction.floor = outcome['floor']
        if 'impact' in outcome:
            enacted_enaction.impact = outcome['impact']
        if 'blocked' in outcome:
            enacted_enaction.blocked = outcome['blocked']
        enacted_enaction.color_index = category_color(outcome['color'])

        # The echo array
        if "echos" in outcome:
            enacted_enaction.echos = outcome['echos']

        # if "echo_array" not in outcome:
        #     outcome["echo_array"] = []
        # # Compute the position of each echo point in the echo array
        # for i in range(100, -99, -5):
        #     ed_str = "ed"+str(i)
        #     if ed_str in outcome:
        #         ha = i
        #         ed = outcome[ed_str]
        #         tmp_x = ROBOT_HEAD_X + math.cos(math.radians(ha)) * ed
        #         tmp_y = math.sin(math.radians(ha)) * ed
        #         local_echo_p = (EXPERIENCE_LOCAL_ECHO, tmp_x, tmp_y)
        #         outcome[KEY_EXPERIENCES].append(local_echo_p)
        #         enacted_enaction.enacted_points.append(local_echo_p)
        # print(enacted_interaction)

        self.workspace.intended_enaction = None
        self.workspace.enacted_enaction = enacted_enaction
        self.workspace.interaction_step = INTERACTION_STEP_INTEGRATING
