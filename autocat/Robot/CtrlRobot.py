import json
import time
import socket
import math
from pyrr import Quaternion
from .RobotDefine import ROBOT_SETTINGS
from .Outcome import Outcome
from .Message import Message

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_INTENDING = 1
INTERACTION_STEP_ENACTING = 2
INTERACTION_STEP_INTEGRATING = 3
INTERACTION_STEP_REFRESHING = 4


class CtrlRobot:
    """The interface between the Workspace and the robot"""

    def __init__(self, workspace):

        self.robot_ip = ROBOT_SETTINGS[workspace.robot_id]["IP"][workspace.arena_id]
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
            self.send_command_to_robot()

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
                    print("Outcome:", outcome_string)
                    # Short outcome are for debug
                    if len(outcome_string) > 100:
                        outcome_dict = json.loads(outcome_string)
                        if outcome_dict['clock'] == self.workspace.enaction.clock:
                            self.terminate_enaction(outcome_dict)
                        else:
                            # Sometimes the previous outcome was received after the time out and we find it here
                            print("Received outcome does not match current enaction")
            else:
                # Timeout: reinitialize the cycle. This will resend the enaction
                self.workspace.memory = self.workspace.memory_snapshot
                self.workspace.interaction_step = INTERACTION_STEP_REFRESHING
                print("Timeout")

    def send_command_to_robot(self):
        """Send the enaction string to the robot and set the timeout"""
        enaction_string = self.workspace.enaction.command.serialize()
        print("Sending:", enaction_string)

        # Send the intended interaction string to the robot
        self.socket.sendto(bytes(enaction_string, 'utf-8'), (self.robot_ip, self.port))

        # Initialize the timeout
        self.expected_outcome_time = time.time() + self.workspace.enaction.command.timeout()

    def terminate_enaction(self, outcome_dict):
        """ Terminate the enaction using the outcome received from the robot."""

        # Process the outcome
        outcome = Outcome(outcome_dict)

        # Compute the compass_quaternion
        if outcome.compass_point is not None:
            # Subtract the offset from robot_define.py
            outcome.compass_point -= self.workspace.memory.body_memory.compass_offset
            # The compass point indicates the south so we must take the opposite and rotate by pi/2
            body_direction_rad = math.atan2(-outcome.compass_point[0], -outcome.compass_point[1])
            outcome.compass_quaternion = Quaternion.from_z_rotation(body_direction_rad)

        # Process the message received from other robot
        # message = None
        # if self.workspace.message is not None:
        #     message = Message(self.workspace.message)
        #     self.workspace.message = None  # Delete the message
        #     # If the message contains the focus point
        #     message.other_destination_ego = self.workspace.memory.polar_egocentric_to_egocentric(message.other_destination)
        #     # If the message contains the position
        #     # message.other_destination_ego = self.workspace.memory.allocentric_to_egocentric(message.other_destination)

        # Terminate the enaction
        self.workspace.enaction.terminate(outcome)
        self.workspace.interaction_step = INTERACTION_STEP_INTEGRATING
