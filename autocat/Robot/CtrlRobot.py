import json
import time
import socket
from .RobotDefine import ROBOT_SETTINGS
from .Outcome import Outcome

ENACTION_STEP_IDLE = 0
ENACTION_STEP_COMMANDING = 1
ENACTION_STEP_ENACTING = 2
ENACTION_STEP_INTEGRATING = 3
ENACTION_STEP_RENDERING = 4


class CtrlRobot:
    """The interface between the Workspace and the robot"""

    def __init__(self, workspace):

        self.robot_ip = ROBOT_SETTINGS[workspace.robot_id]["IP"][workspace.arena_id]
        self.workspace = workspace
        self.port = 8888
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.connect((self.robot_ip, self.port))  # Not necessary for UDP. Generates an error on my mac
        self.socket.settimeout(0)
        self.send_time = 0.
        self.time_out = 0.
        # self.expected_outcome_time = 0.

    def main(self, dt):
        """The main handler of the communication to and from the robot."""
        # If COMMANDING then send the interaction to the robot
        if self.workspace.enacter.interaction_step == ENACTION_STEP_COMMANDING:
            self.workspace.enacter.interaction_step = ENACTION_STEP_ENACTING
            self.send_command_to_robot()

        # While the robot is enacting the interaction, check for the outcome
        if self.workspace.enacter.interaction_step == ENACTION_STEP_ENACTING and not self.workspace.enacter.is_imagining:
            if time.time() < self.send_time + self.time_out:
                outcome_string = None
                try:
                    outcome_string, _ = self.socket.recvfrom(512)
                except socket.timeout:   # Time out error if outcome not yet received
                    print("t", end='')
                except OSError as e:
                    if e.args[0] in [35, 10035]:
                        print(".", end='')
                    else:
                        print(e)
                # If the outcome was received and packet longer than debug packet
                if outcome_string is not None and len(outcome_string) > 100:
                    outcome_dict = json.loads(outcome_string)
                    if outcome_dict['clock'] == self.workspace.enaction.clock:
                        print()  # New line after the waiting dots
                        print("Outcome:", outcome_string)
                        # If the robot does not return the yaw (no IMU) then use the command yaw
                        if 'yaw' not in outcome_dict:
                            outcome_dict['yaw'] = self.workspace.enaction.command.yaw
                        # Terminate the enaction
                        self.workspace.enaction.outcome = Outcome(outcome_dict)
                        self.workspace.enacter.interaction_step = ENACTION_STEP_INTEGRATING
                        # else:
                        # Previous outcome received again: Perhaps the command was resent during first reception
                        # print(f"Outcome {outcome_dict['clock']} was received again")
                        # Reset the time out. This will resend the next command right away
                        # self.expected_outcome_time = time.time()
            else:
                # Timeout: reinitialize the cycle. This will resend the enaction
                # serotonin = self.workspace.memory.body_memory.serotonin  # Handel user change  TODO improve
                # dopamine = self.workspace.memory.body_memory.dopamine  # Handel user change
                # noradrenaline = self.workspace.memory.body_memory.noradrenaline  # Handel user change
                # confidence = self.workspace.memory.phenomenon_memory.terrain_confidence()
                # self.workspace.memory = self.workspace.enacter.memory_snapshot
                # self.workspace.memory.body_memory.serotonin = serotonin
                # self.workspace.memory.body_memory.dopamine = dopamine
                # self.workspace.memory.body_memory.noradrenaline = noradrenaline
                # if self.workspace.memory.phenomenon_memory.terrain() is not None:
                #     self.workspace.memory.phenomenon_memory.terrain().confidence = confidence
                # self.workspace.enacter.interaction_step = ENACTION_STEP_REFRESHING
                self.workspace.enacter.interaction_step = ENACTION_STEP_COMMANDING
                print(f". Timeout {self.time_out:.3f} .", end='')

    def send_command_to_robot(self):
        """Send the enaction string to the robot and set the timeout"""
        enaction_string = self.workspace.enaction.command.serialize()
        # print("Sending:", enaction_string)

        # Send the intended interaction string to the robot
        self.socket.sendto(bytes(enaction_string, 'utf-8'), (self.robot_ip, self.port))

        # Initialize the timeout
        self.send_time = time.time()
        self.time_out = self.workspace.enaction.command.timeout()
        # self.expected_outcome_time = time.time() + self.workspace.enaction.command.timeout()
