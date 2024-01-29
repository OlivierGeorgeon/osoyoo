import math
import numpy as np
import matplotlib
import os
from pyrr import Quaternion, Vector3, matrix44, vector3
from ..Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, \
    ENACTION_STEP_INTEGRATING, ENACTION_STEP_REFRESHING
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS
from ..Memory.Memory import Memory
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.PhenomenonMemory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE, BOX
from ..Memory.BodyMemory import point_to_echo_direction_distance
from ..Decider.Action import ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Decider.Decider import CONFIDENCE_CONFIRMED_FOCUS
from ..Robot.Outcome import Outcome
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ..Utils import short_angle, quaternion_to_direction_rad, assert_almost_equal_angles
from .Plot import plot, PREDICTION_ERROR_WINDOW


class Enacter:
    def __init__(self, workspace):
        self.workspace = workspace
        self.interaction_step = ENACTION_STEP_IDLE
        self.memory_snapshot = None
        self.is_simulating = False
        self.simulation_duration1 = 0
        self.simulated_outcome = None

        self.forward_duration1_prediction_error = {}  # (ms)
        self.yaw_prediction_error = {}                # (degree)
        self.compass_prediction_error = {}            # (degree)
        self.focus_direction_prediction_error = {}    # (degree)
        self.focus_distance_prediction_error = {}     # (mm)

    def main(self, dt):
        """Controls the enaction."""
        if self.interaction_step == ENACTION_STEP_IDLE:
            # When the next enaction is in the stack, prepare the enaction
            if self.workspace.composite_enaction is not None:
                # Take the current enaction from the composite interaction
                self.workspace.enaction = self.workspace.composite_enaction.current_enaction()
                # Take a memory snapshot to restore at the end of the enaction
                self.memory_snapshot = self.workspace.memory.save()
                # Begin the enaction and attribute the clock
                self.workspace.enaction.begin(self.workspace.clock, self.workspace.memory.body_memory.body_quaternion)
                self.is_simulating = True
                if self.workspace.is_imagining:
                    # If imagining then proceed to simulating the enaction
                    print("Simulated command", self.workspace.enaction.serialize())
                    self.interaction_step = ENACTION_STEP_ENACTING
                else:
                    # If not imagining then proceed to COMMANDING to send the command to the robot
                    self.interaction_step = ENACTION_STEP_COMMANDING

        # COMMANDING: CtrlRobot sends the command to the robot and moves on to ENACTING

        # ENACTING: Simulate the enaction in memory
        if self.interaction_step == ENACTION_STEP_ENACTING:
            if self.is_simulating:
                self.simulated_outcome = self.simulate(dt)
            elif self.workspace.is_imagining:
                # If imagining then use the imagined outcome when the simulation is finished
                self.workspace.enaction.terminate(self.simulated_outcome)
                if not self.workspace.composite_enaction.increment(self.simulated_outcome):
                    self.workspace.composite_enaction = None
                self.interaction_step = ENACTION_STEP_INTEGRATING
            # If not imagining then CtrlRobot will return the outcome and proceed to INTEGRATING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == ENACTION_STEP_INTEGRATING:
            # Restore the memory from the snapshot
            self.workspace.memory = self.memory_snapshot

            # Retrieve possible message from other robot
            if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                    self.workspace.message is not None:
                self.workspace.enaction.message = self.workspace.message
                print("Message", self.workspace.message.message_string)
                # self.workspace.message = None

            # Force terminate the simulation
            if self.is_simulating:
                self.is_simulating = False
                print("Force terminate simulation")

            # Update body memory and egocentric memory
            self.workspace.memory.update_and_add_experiences(self.workspace.enaction)

            # Call the integrator to create and update the phenomena
            self.workspace.integrator.integrate()

            # Update allocentric memory: robot, phenomena, focus
            self.workspace.memory.update_allocentric(self.workspace.clock)

            # Track the prediction errors
            self.prediction_error(self.simulated_outcome)

            # Increment the clock if the enacted interaction was properly received
            if self.workspace.enaction.clock >= self.workspace.clock:  # don't increment if the robot is behind
                self.workspace.clock += 1

            self.interaction_step = ENACTION_STEP_REFRESHING

        # REFRESHING: Will be reset to IDLE in the next cycle

    def simulate(self, dt):
        """Simulate the enaction in memory. Reset self.is_simulating when the simulation ends"""
        enaction = self.workspace.enaction
        memory: Memory = self.workspace.memory

        # Check whether target time is elapsed
        enaction.simulation_time += dt
        if enaction.simulation_time >= enaction.simulation_duration:
            dt += enaction.simulation_duration - enaction.simulation_time  # Adjust to the exact duration
            self.is_simulating = False
            self.simulation_duration1 = enaction.simulation_duration * 1000

        # The intermediate displacement
        yaw_quaternion = Quaternion.from_z_rotation((enaction.simulation_rotation_speed * dt))
        way = 1
        if enaction.action.action_code == ACTION_SWIPE and enaction.command.speed is not None \
                and enaction.command.speed < 0:
            way = -1
        translation = enaction.action.translation_speed * dt * way
        yaw_matrix = matrix44.create_from_quaternion(yaw_quaternion)
        translation_matrix = matrix44.create_from_translation(-translation)
        displacement_matrix = matrix44.multiply(yaw_matrix, translation_matrix)

        # Simulate the displacement of experiences
        for experience in memory.egocentric_memory.experiences.values():
            experience.displace(displacement_matrix)
        # Simulate the displacement of the focus and prompt
        if memory.egocentric_memory.focus_point is not None:
            memory.egocentric_memory.focus_point = matrix44.apply_to_vector(displacement_matrix,
                                                                            memory.egocentric_memory.focus_point)
        if memory.egocentric_memory.prompt_point is not None:
            memory.egocentric_memory.prompt_point = matrix44.apply_to_vector(displacement_matrix,
                                                                             memory.egocentric_memory.prompt_point)
        # Displacement in body memory
        memory.body_memory.body_quaternion = memory.body_memory.body_quaternion.cross(yaw_quaternion)
        if memory.egocentric_memory.focus_point is not None:
            # Keep the head aligned to the focus
            head_direction_degree, _ = point_to_echo_direction_distance(memory.egocentric_memory.focus_point)
            head_direction_degree = max(-90, min(head_direction_degree, 90))
            memory.body_memory.set_head_direction_degree(head_direction_degree)
        else:
            head_direction_degree = memory.body_memory.head_direction_degree()

        # Update allocentric memory
        memory.allocentric_memory.robot_point += memory.body_memory.body_quaternion * Vector3(translation)

        # If crossed the line then stop the simulation (must do before marking the place)
        floor = 0
        color_index = 0
        yaw = round(math.degrees(quaternion_to_direction_rad(enaction.command.predicted_yaw_quaternion)))
        if memory.phenomenon_memory.terrain_confidence() < PHENOMENON_RECOGNIZED_CONFIDENCE:
            if enaction.action.action_code in [ACTION_FORWARD, ACTION_SWIPE]:
                floor_i, floor_j = point_to_cell(memory.allocentric_memory.robot_point +
                                                 memory.body_memory.body_quaternion * Vector3([ROBOT_FLOOR_SENSOR_X,
                                                                                               0, 0]))
                if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
                    (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
                        memory.allocentric_memory.grid[floor_i][floor_j].status[0] == EXPERIENCE_FLOOR:
                    self.is_simulating = False
                    self.simulation_duration1 = enaction.simulation_time * 1000
                    if enaction.action.action_code == ACTION_FORWARD:
                        floor = 3
                        # self.simulation_duration1 += 400  # Add the inertia
                    else:
                        if enaction.command.speed is None or enaction.command.speed > 0:
                            # Swipe left
                            floor = 2
                            yaw = 45
                        else:
                            # Swipe right
                            floor = 1
                            yaw = -45
                    color_index = memory.allocentric_memory.grid[floor_i][floor_j].color_index
                else:
                    floor = 0
        elif enaction.predicted_distance_to_line is not None:
            floor = enaction.predicted_floor
            if floor == 1:
                yaw = -45
            elif floor == 2:
                yaw = 45
            if enaction.action.action_code == ACTION_FORWARD:
                self.simulation_duration1 = (enaction.predicted_distance_to_line - ROBOT_FLOOR_SENSOR_X) * 1000 / \
                                            ROBOT_SETTINGS[self.workspace.robot_id]["forward_speed"]
            else:
                self.simulation_duration1 = enaction.predicted_distance_to_line * 1000 / \
                                            ROBOT_SETTINGS[self.workspace.robot_id]["lateral_speed"]

        # Compute the simulated echo
        echoes = [[enaction.predicted_head_direction, enaction.predicted_echo_distance]]
        # for p in [p for p in self.workspace.memory.phenomenon_memory.phenomena.values() if p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO]:
        #     ego_center_point = self.workspace.memory.allocentric_to_egocentric(p.point)
        #     a, d = point_to_echo_direction_distance(ego_center_point)
        #     # Subtract the phenomenon's radius to obtain the egocentric echo distance
        #     d -= self.workspace.memory.phenomenon_memory.phenomenon_categories[BOX].long_radius
        #     if d > 0 and enaction.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90) or \
        #             assert_almost_equal_angles(math.radians(a), math.radians(head_direction_degree), 35):
        #         echoes.append([a, d])

        # Process the cells added by the user
        for ij in self.workspace.memory.allocentric_memory.user_cells:
            cell = self.workspace.memory.allocentric_memory.grid[ij[0]][ij[1]]
            if cell.status[1] == EXPERIENCE_ALIGNED_ECHO:
                p = cell.point()
                a, d = point_to_echo_direction_distance(self.workspace.memory.allocentric_to_egocentric(p))
                if enaction.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90) or \
                        assert_almost_equal_angles(math.radians(a), math.radians(head_direction_degree), 35):
                    echoes.append([a, d])
        # if len(echoes) > 0:
        np_echoes = np.array(echoes, dtype=int)
        head_angle, echo_distance = np_echoes[np.argmin(np_echoes[:, 1])]

        # else:
        #     head_angle, echo_distance = 0, 10000

        # Mark the place
        memory.allocentric_memory.place_robot(memory.body_memory, enaction.clock)

        # Simulate an echo from the focus point
        # if memory.egocentric_memory.focus_point is None:
        #     head_angle, echo_distance = 0, 10000
        # else:
        #     head_angle, echo_distance = point_to_echo_direction_distance(memory.egocentric_memory.focus_point)

        # Return the simulated outcome
        outcome_string = {"action": self.workspace.enaction.action.action_code, "clock": self.workspace.enaction.clock,
                          "floor": floor, "duration1": round(self.simulation_duration1), "status": "I", "yaw": yaw,
                          "head_angle": head_angle, "echo_distance": echo_distance, "color_index": color_index}
        # Print the simulated outcome at the end of the simulation
        if not self.is_simulating:
            print("Simulated outcome", outcome_string)
            # Empty the list of cells to be processed
            self.workspace.memory.allocentric_memory.user_cells = []
        return Outcome(outcome_string)

    def prediction_error(self, simulated_outcome):
        """Compute the prediction errors"""
        enaction = self.workspace.enaction

        # Translation duration1

        if self.workspace.enaction.action.action_code in [ACTION_FORWARD] and self.workspace.enaction.outcome.duration1 != 0:  #, ACTION_SWIPE]:
            pe = (simulated_outcome.duration1 - self.workspace.enaction.outcome.duration1)/self.workspace.enaction.outcome.duration1
            self.forward_duration1_prediction_error[self.workspace.enaction.clock] = pe
            self.forward_duration1_prediction_error.pop(self.workspace.enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Translate duration1 (simulation - measured)=", round(pe),
                  "Average:", round(float(np.mean(list(self.forward_duration1_prediction_error.values())))),
                  "std:", round(float(np.std(list(self.forward_duration1_prediction_error.values())))))

        # yaw

        pe = math.degrees(-short_angle(enaction.command.predicted_yaw_quaternion, enaction.yaw_quaternion))
        self.yaw_prediction_error[self.workspace.enaction.clock] = pe
        self.yaw_prediction_error.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Yaw (command - measure)=", round(pe, 1),
              "Average:", round(float(np.mean(list(self.yaw_prediction_error.values()))), 1),
              "std:", round(float(np.std(list(self.yaw_prediction_error.values()))), 1))

        # Compass prediction error

        self.compass_prediction_error[self.workspace.enaction.clock] = \
            math.degrees(self.workspace.enaction.body_direction_delta)
        self.compass_prediction_error.pop(self.workspace.enaction.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Compass (integrated direction - compass measure)=",
              round(self.compass_prediction_error[self.workspace.enaction.clock], 2), "Average:",
              round(float(np.mean(list(self.compass_prediction_error.values()))), 2), "std:",
              round(float(np.std(list(self.compass_prediction_error.values()))), 2))

        # If focus is confident then track its prediction error

        if self.workspace.enaction.focus_confidence >= CONFIDENCE_CONFIRMED_FOCUS:
            self.focus_direction_prediction_error[self.workspace.enaction.clock] = \
                self.workspace.enaction.focus_direction_prediction_error
            self.focus_direction_prediction_error.pop(self.workspace.enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Focus direction (integration - measure)=",
                  self.workspace.enaction.focus_direction_prediction_error,
                  "Average:", round(float(np.mean(list(self.focus_direction_prediction_error.values())))),
                  "std:", round(float(np.std(list(self.focus_direction_prediction_error.values())))))
            self.focus_distance_prediction_error[self.workspace.enaction.clock] = \
                self.workspace.enaction.focus_distance_prediction_error
            self.focus_distance_prediction_error.pop(self.workspace.enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Focus distance (integration - measure)=",
                  self.workspace.enaction.focus_distance_prediction_error,
                  "Average:", round(float(np.mean(list(self.focus_distance_prediction_error.values())))),
                  "std:", round(float(np.std(list(self.focus_distance_prediction_error.values())))))

        # Trace the terrain origin prediction error

        terrain = self.workspace.memory.phenomenon_memory.terrain()
        if terrain is not None:
            terrain.origin_prediction_error.pop(self.workspace.enaction.clock - PREDICTION_ERROR_WINDOW, None)
            if self.workspace.enaction.clock in terrain.origin_prediction_error:
                print("Prediction Error Terrain origin (integration - measure)=",
                      round(terrain.origin_prediction_error[self.workspace.enaction.clock]),
                      "Average:", round(float(np.mean(list(terrain.origin_prediction_error.values())))),
                      "std:", round(float(np.std(list(terrain.origin_prediction_error.values())))))

    def plot_prediction_errors(self):
        """Show the prediction error plots"""
        # The agg backend avoids interfering with pyglet windows
        # https://matplotlib.org/stable/users/explain/figure/backends.html
        matplotlib.use('agg')
        # Create the log directory if it does not exist because it is not included in git
        if not os.path.exists("log"):
            os.makedirs("log")
        # Generate the plots
        plot(self.workspace.enacter.forward_duration1_prediction_error, "Forward duration (%)", "Translation")
        plot(self.workspace.enacter.yaw_prediction_error, "Yaw (degrees)", "yaw")
        plot(self.compass_prediction_error, "Compass (degree)", "Compass")
        plot(self.focus_direction_prediction_error, "Focus direction (degree)", "Focus_direction")
        plot(self.focus_distance_prediction_error, "Focus distance (mm)", "Focus_distance")
        terrain = self.workspace.memory.phenomenon_memory.terrain()
        if terrain is not None:
            plot(terrain.origin_prediction_error, "Terrain origin (mm)", "Origin")
