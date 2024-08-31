import json
import time
import socket
# from ..Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, \
#     ENACTION_STEP_INTEGRATING, ENACTION_STEP_RENDERING
from . import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, ENACTION_STEP_INTEGRATING, \
    ENACTION_STEP_RENDERING
from ..Memory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE
from ..Integrator.OutcomeCode import outcome_code, outcome_code_focus
from . import KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Proposer.Interaction import OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS
from ..Proposer.Action import ACTION_SCAN
from ..Robot import NO_ECHO_DISTANCE
from ..Robot.Outcome import Outcome
from ..SoundPlayer import SoundPlayer, SOUND_SURPRISE
from ..Proposer.AttentionMechanism import AttentionMechanism


class Enacter:
    def __init__(self, workspace):
        self.workspace = workspace
        self.attention_mechanism = AttentionMechanism(workspace)
        self.interaction_step = ENACTION_STEP_IDLE
        self.memory_snapshot = None
        self.is_imagining = False
        self.memory_before_imaginary = None
        self.view_reset_flag = False

        self.robot_ip = ROBOT_SETTINGS[workspace.robot_id]["IP"][workspace.arena_id]
        self.port = 8888
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.connect((self.robot_ip, self.port))  # Not necessary for UDP. Generates an error on my mac
        self.socket.settimeout(0)
        self.send_time = 0.
        self.time_out = 0.

    def main(self, dt):
        """Controls the enaction."""
        # RENDERING: last only one cycle
        if self.interaction_step == ENACTION_STEP_RENDERING:
            self.interaction_step = ENACTION_STEP_IDLE
            self.view_reset_flag = False

        # IDLE: Ready to choose the next intended interaction
        if self.interaction_step == ENACTION_STEP_IDLE:
            # Manage the memory snapshot
            if self.is_imagining:
                # If stop imagining then restore memory from the snapshot
                if self.workspace.engagement_mode == KEY_ENGAGEMENT_ROBOT:
                    self.workspace.memory = self.memory_before_imaginary
                    self.is_imagining = False
                    self.interaction_step = ENACTION_STEP_RENDERING
                    self.view_reset_flag = True
            else:
                # If start imagining then take a new memory snapshot
                if self.workspace.engagement_mode == KEY_ENGAGEMENT_IMAGINARY:
                    self.memory_before_imaginary = self.workspace.memory.save()
                    self.is_imagining = True

            # When the next enaction is in the stack, prepare the enaction
            if self.workspace.composite_enaction is not None:
                # Take the current enaction from the composite interaction
                self.workspace.enaction = self.workspace.composite_enaction.current_enaction()
                # Take a memory snapshot to restore at the end of the enaction
                # self.workspace.memory.emotion_code = self.workspace.enaction.predicted_memory.emotion_code
                self.memory_snapshot = self.workspace.memory.save()
                # Show the prompt in memory
                if self.workspace.enaction.trajectory.prompt_point is not None:
                    self.workspace.memory.egocentric_memory.prompt_point = \
                        self.workspace.enaction.trajectory.prompt_point.copy()
                    self.workspace.memory.allocentric_memory.update_prompt(
                        self.workspace.memory.egocentric_to_allocentric(
                            self.workspace.memory.egocentric_memory.prompt_point), self.workspace.memory.clock)
                # Begin the enaction
                self.workspace.enaction.begin(self.workspace.memory.body_memory.body_quaternion)
                # Begin the simulation
                self.workspace.simulator.begin()
                if self.is_imagining:
                    # If imagining then proceed to simulating the enaction
                    self.interaction_step = ENACTION_STEP_ENACTING
                else:
                    # If not imagining then proceed to COMMANDING to send the command to the robot
                    self.interaction_step = ENACTION_STEP_COMMANDING

        # COMMANDING: CtrlRobot sends the command to the robot and moves on to ENACTING
        if self.workspace.enacter.interaction_step == ENACTION_STEP_COMMANDING:
            self.workspace.enacter.interaction_step = ENACTION_STEP_ENACTING
            self.send_command_to_robot()

        # ENACTING: Simulate the enaction in memory
        if self.interaction_step == ENACTION_STEP_ENACTING:
            self.workspace.simulator.simulate(dt)
            # If imagining then check for the end of the simulation
            if self.is_imagining:
                if not self.workspace.simulator.is_simulating:
                    self.interaction_step = ENACTION_STEP_INTEGRATING
            # If not imagining then CtrlRobot will terminate the enaction and proceed to INTEGRATING
            else:
                if time.time() < self.send_time + self.time_out:
                    outcome_string = None
                    try:
                        outcome_string, _ = self.socket.recvfrom(512)
                    except socket.timeout:  # Time out error if outcome not yet received
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
                            # If action scan then set default value for no echo
                            if outcome_dict['action'] == ACTION_SCAN:
                                if 'echos' not in outcome_dict or outcome_dict['echos'] is None:
                                    outcome_dict['echos'] = {}
                                for angle in range(-90, 91, self.workspace.enaction.command.span):
                                    outcome_dict['echos'][str(angle)] = outcome_dict['echos'].get(str(angle),
                                                                                                  NO_ECHO_DISTANCE)
                            # Terminate the enaction
                            self.workspace.enaction.outcome = Outcome(outcome_dict)
                            self.workspace.enacter.interaction_step = ENACTION_STEP_INTEGRATING
                else:
                    # Timeout: reinitialize the cycle. This will resend the enaction
                    self.workspace.enacter.interaction_step = ENACTION_STEP_COMMANDING
                    print(f". Timeout {self.time_out:.3f} .", end='')

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == ENACTION_STEP_INTEGRATING:
            # Terminate the simulation
            simulated_outcome = self.workspace.simulator.end()
            print("Simulated outcome", simulated_outcome)
            if self.is_imagining:
                self.workspace.enaction.outcome = simulated_outcome

            # Terminate the enaction using the outcome that come from the robot or from the simulation
            self.workspace.enaction.terminate()

            # Restore the memory from the snapshot. TODO make it more elegant
            neurotransmitters = self.workspace.memory.body_memory.neurotransmitters.copy()
            confidence = self.workspace.memory.phenomenon_memory.terrain_confidence()
            position_confidence = None
            if self.workspace.memory.place_memory.current_place_cell() is not None:
                position_confidence = self.workspace.memory.place_memory.current_place_cell().position_confidence
            self.workspace.memory = self.memory_snapshot
            self.workspace.memory.body_memory.neurotransmitters[:] = neurotransmitters
            if self.workspace.memory.phenomenon_memory.terrain() is not None:
                self.workspace.memory.phenomenon_memory.terrain().confidence = confidence
            if self.workspace.memory.place_memory.current_place_cell() is not None:
                self.workspace.memory.place_memory.current_place_cell().position_confidence = position_confidence

            # Retrieve possible message from other robot
            if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                    self.workspace.message is not None:
                self.workspace.enaction.message = self.workspace.message
                print("Message", self.workspace.message.message_string)

            # Update memory, possibly create new place cell and phenomena
            self.workspace.memory.update(self.workspace.enaction)
            # Show the current place cell in PlaceCellView
            self.workspace.show_place_cell(self.workspace.memory.place_memory.current_cell_id)

            # Select the focus - May be included in the attention mechanism
            # self.select_focus(self.workspace.memory)

            # Compute the outcome code which depends on the updated memory
            self.workspace.enaction.outcome_code = outcome_code(self.workspace.memory,
                                                   self.workspace.enaction.trajectory, self.workspace.enaction.outcome)

            # Express surprise if the enaction failed
            if not self.workspace.enaction.succeed():
                SoundPlayer.play(SOUND_SURPRISE)
                # if failed due to no floor and no impact
                if self.workspace.enaction.outcome.floor == 0 and \
                        self.workspace.memory.phenomenon_memory.focus_phenomenon_id is not None \
                        and self.workspace.enaction.outcome.impact == 0:
                    # Lost focus to DOT phenomenon  TODO improve
                    self.workspace.enaction.outcome_code = OUTCOME_LOST_FOCUS

            # Manage attention
            # Focus at the nearest phenomenon, or near the dot phenomenon it if it was lost
            self.attention_mechanism.update_focus()
            if self.workspace.memory.egocentric_memory.focus_point is not None \
                    and self.workspace.enaction.outcome_code == OUTCOME_NO_FOCUS:
                self.workspace.enaction.outcome_code = outcome_code_focus(
                    self.workspace.memory.egocentric_memory.focus_point, self.workspace.memory)

            # Track the prediction errors
            self.workspace.prediction_error.log(self.workspace.enaction)
            # Calibrate
            self.workspace.calibrator.calibrate()

            # Log the trace
            self.workspace.tracer = self.workspace.tracer.bind(**self.workspace.memory.trace_dict())
            self.workspace.tracer.info("", **self.workspace.enaction.trace_dict())
            self.workspace.tracer = self.workspace.tracer.new()

            # Increment the clock
            if self.workspace.enaction.clock >= self.workspace.memory.clock:  # don't increment if the robot is behind
                self.workspace.memory.clock += 1
            else:
                print("Clock not incremented")  # TODO If never happens then remove the test

            # If the composite enaction is over or aborted due to floor or impact
            if not self.workspace.composite_enaction.increment():
                self.workspace.composite_enaction = None

            self.interaction_step = ENACTION_STEP_RENDERING

        # RENDERING: Will be reset to IDLE in the next cycle

    def select_focus(self, memory):
        """Select a focus based on the phenomena in memory"""

        # Look for DOT phenomena
        k_d = {k: memory.allocentric_to_egocentric(p.point)[0] for k, p in memory.phenomenon_memory.phenomena.items()
               if p.phenomenon_type == EXPERIENCE_FLOOR and memory.allocentric_to_egocentric(p.point)[0] >
               ROBOT_FLOOR_SENSOR_X}
        if len(k_d) > 0:
            # Focus at the closest DOT phenomenon
            closest_key = min(k_d, key=k_d.get)
            memory.phenomenon_memory.focus_phenomenon_id = closest_key
            closest_dot_phenomenon = memory.phenomenon_memory.phenomena[closest_key]
            memory.allocentric_memory.update_focus(closest_dot_phenomenon.point, memory.clock)
            memory.egocentric_memory.focus_point = memory.allocentric_to_egocentric(closest_dot_phenomenon.point)

        # # If no focus then look for phenomena that could attract focus
        # if memory.egocentric_memory.focus_point is None:
        #     # The dict of distances of the dot phenomena beyond the floor sensor
        #     k_d = {k: memory.allocentric_to_egocentric(p.point)[0] for k, p in memory.phenomenon_memory.phenomena.items()
        #            if p.phenomenon_type == EXPERIENCE_FLOOR and memory.allocentric_to_egocentric(p.point)[0] > ROBOT_FLOOR_SENSOR_X}
        #     if len(k_d) > 0:
        #         # Focus at the closest phenomenon
        #         closest_key = min(k_d, key=k_d.get)
        #         memory.phenomenon_memory.focus_phenomenon_id = closest_key
        #         closest_dot_phenomenon = memory.phenomenon_memory.phenomena[closest_key]
        #         memory.allocentric_memory.update_focus(closest_dot_phenomenon.point, memory.clock)
        #         memory.egocentric_memory.focus_point = memory.allocentric_to_egocentric(closest_dot_phenomenon.point)

    def send_command_to_robot(self):
        """Send the command string to the robot and set the timeout"""
        command_string = self.workspace.enaction.command.serialize()
        # print("Sending:", enaction_string)
        self.socket.sendto(bytes(command_string, 'utf-8'), (self.robot_ip, self.port))
        # Initialize the timeout
        self.send_time = time.time()
        self.time_out = self.workspace.enaction.command.timeout()
