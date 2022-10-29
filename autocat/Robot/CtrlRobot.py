import json
import numpy
import threading
import math
from .RobotDefine import *
from .WifiInterface import WifiInterface
from ..Memory.EgocentricMemory.Experience import *
from ..Integrator.Integrator import TRUST_POSITION_PHENOMENON
from ..Integrator.Phenomenon import PHENOMENON_DELTA

ENACT_STEP_IDLE = 0
ENACT_STEP_ENACTING = 1
ENACT_STEP_END = 2

KEY_EXPERIENCES = 'points'
KEY_IMPACT = 'shock'

FOCUS_DELTA = 300  # (mm) Maximum delta to keep focus

class CtrlRobot:
    """Handle the communication with the robot:
        - When the workspace controller has an intended_interaction, compute the command string and send it to the robot
        - When the outcome string is received from the robot, compute the enacted_interaction and send it to the
          workspace controller
    """

    def __init__(self, robot_ip, workspace):

        self.robot_ip = robot_ip
        self.workspace = workspace
        self.wifiInterface = WifiInterface(robot_ip)
        # self.azimuth = 0  # Integrated from the yaw if the robot does not return compass data

        self.forward_speed = numpy.array([FORWARD_SPEED, 0])  # Need numpy arrays to compute average
        self.backward_speed = numpy.array([-FORWARD_SPEED, 0])
        self.leftward_speed = numpy.array([0, LATERAL_SPEED])
        self.rightward_speed = numpy.array([0, -LATERAL_SPEED])

        # Used in an asynchronous Thread
        self.enact_step = ENACT_STEP_IDLE
        self.intended_interaction = None  # Need random initialization
        self.outcome_bytes = None  # Default status T timeout

    def main(self, dt):
        """Handle the communication with the robot."""
        if self.enact_step == ENACT_STEP_END:
            self.workspace.robot_ready = True
            # self.robot_has_finished_acting = True
            self.enact_step = ENACT_STEP_IDLE
        # if self.robot_has_finished_acting:
            # self.robot_has_finished_acting = False
            enacted_interaction = self.outcome_to_enacted_interaction()
            self.workspace.update_enacted_interaction(enacted_interaction)

        if self.enact_step == ENACT_STEP_IDLE:
            # self.has_new_action_to_enact, intended_interaction = self.ctrl_workspace.get_intended_interaction()
            intended_interaction = self.workspace.get_intended_interaction()
            if intended_interaction is not None:
                self.intended_interaction_to_action(intended_interaction)

    def intended_interaction_to_action(self, intended_interaction):
        """ Creating an asynchronous thread to send the action to the robot and to wait for the outcome """

        def enact_thread():
            """ Sending the action to the robot and waiting for the outcome """
            intended_interaction_string = json.dumps(self.intended_interaction)
            print("Sending: " + intended_interaction_string)
            self.outcome_bytes = self.wifiInterface.enact(intended_interaction_string)
            print("Receive: ", end="")
            print(self.outcome_bytes)
            self.enact_step = ENACT_STEP_END  # Now we have received the outcome from the robot

        # Add the estimated speed to the action
        if intended_interaction['action'] == '8':
            intended_interaction['speed'] = int(self.forward_speed[0])
        if intended_interaction['action'] == '2':
            intended_interaction['speed'] = -int(self.backward_speed[0])
        if intended_interaction['action'] == '4':
            intended_interaction['speed'] = int(self.leftward_speed[1])
        if intended_interaction['action'] == '6':
            intended_interaction['speed'] = -int(self.rightward_speed[1])

        self.intended_interaction = intended_interaction
        self.enact_step = ENACT_STEP_ENACTING  # Now we send the intended interaction to the robot for enaction
        thread = threading.Thread(target=enact_thread)
        thread.start()

    def outcome_to_enacted_interaction(self):
        """ Computes the enacted interaction from the robot's outcome data """
        action = self.intended_interaction.get('action')
        is_focussed = ('focus_x' in self.intended_interaction)  # The focus point was sent to the robot
        enacted_interaction = json.loads(self.outcome_bytes)
        enacted_interaction[KEY_EXPERIENCES] = []

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

        # If the robot does not return the azimuth then return 0. The azimuth will be computed by BodyMemory
        if 'azimuth' not in enacted_interaction:
             # self.azimuth = 0  # yaw  # yaw is counterclockwise, azimuth is clockwise
             enacted_interaction['azimuth'] = 0  # self.azimuth

        # If the robot returns compass_x and compass_y then recompute the azimuth
        if 'compass_x' in enacted_interaction:
            # Subtract the offset from robot_define.py
            enacted_interaction['compass_x'] -= COMPASS_X_OFFSET
            enacted_interaction['compass_y'] -= COMPASS_Y_OFFSET
            azimuth = math.degrees(math.atan2(enacted_interaction['compass_y'], enacted_interaction['compass_x']))
            # The compass point indicates the south so we must rotate it of 180° to obtain the azimuth
            azimuth += 180
            if azimuth >= 360:
                azimuth -= 360
            # Override the azimuth returned by the robot.
            # (They are equal unless COMPASS_X_OFFSET or COMPASS_X_OFFSET are non zero)
            enacted_interaction['azimuth'] = int(azimuth)

        # Interaction Floor line
        if enacted_interaction['floor'] > 0:
            enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_FLOOR, LINE_X, 0))
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
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_ALIGNED_ECHO, *echo_xy))
                # Return the echo_xy to possibly use as focus
                enacted_interaction['echo_xy'] = echo_xy

        # Interaction shock
        if KEY_IMPACT in enacted_interaction and action == '8':
            if enacted_interaction[KEY_IMPACT] == 0b01:  # Impact on the right
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, -ROBOT_FRONT_Y))
            if enacted_interaction[KEY_IMPACT] == 0b11:  # Impact on the front
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, 0))
            if enacted_interaction[KEY_IMPACT] == 0b10:  # Impact on the left
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_IMPACT, ROBOT_FRONT_X, ROBOT_FRONT_Y))

        # Interaction block
        if 'blocked' in enacted_interaction and action == '8':
            if enacted_interaction['blocked']:
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_BLOCK, ROBOT_FRONT_X, 0))
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
            # print("Distance between echo and focus:", distance)
            if math.dist(echo_xy, expected_focus_xy) < FOCUS_DELTA:
                additional_xy = expected_focus_xy - echo_xy
                # print("additional translation:", additional_xy)
                # The focus has been kept
                enacted_interaction['focus'] = True

                # If trust the phenomenon then adjust the displacement
                if self.workspace.trust_mode == TRUST_POSITION_PHENOMENON:
                    translation += additional_xy
                    translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
                    displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                    # Adjust the speed
                    if action == '8' and enacted_interaction['duration1'] >= 1000:
                        self.forward_speed = (self.forward_speed + translation) / 2
                        # print("New forward speed:", self.forward_speed)
                    if action == '2' and enacted_interaction['duration1'] >= 1000:
                        self.backward_speed = (self.backward_speed + translation) / 2
                        # print("New backward speed:", self.backward_speed)
                    if action == '4' and enacted_interaction['duration1'] >= 1000:
                        self.leftward_speed = (self.leftward_speed + translation) / 2
                        # print("New leftward speed:", self.leftward_speed)
                    if action == '6' and enacted_interaction['duration1'] >= 1000:
                        self.rightward_speed = (self.rightward_speed + translation) / 2
                        # print("New rightward speed:", self.rightward_speed)
            else:
                ""
                # print("Lost focus with distance:", distance)

        # Return the displacement
        enacted_interaction['translation'] = translation
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
                # enacted_interaction['echo_array'].append((tmp_x, tmp_y))
                enacted_interaction[KEY_EXPERIENCES].append((EXPERIENCE_LOCAL_ECHO, tmp_x, tmp_y))

        print(enacted_interaction)

        return enacted_interaction
