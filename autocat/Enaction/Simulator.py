import math
import numpy as np
from pyrr import Quaternion, Vector3, matrix44
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Memory.PhenomenonMemory import PHENOMENON_ENCLOSED_CONFIDENCE
from ..Proposer.Action import ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Outcome import Outcome
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ..Utils import assert_almost_equal_angles, translation_quaternion_to_matrix, point_to_head_direction_distance
from .Predict import RETREAT_YAW

SIMULATION_SPEED = 1  # 0.5


class Simulator:
    def __init__(self, workspace):
        self.workspace = workspace
        self.is_simulating = False
        self.simulation_time = 0
        self.simulated_outcome_dict = {}
        self.simulation_duration = 0

    def begin(self):
        """Begin the simulation"""
        self.is_simulating = True
        self.simulation_time = 0
        self.simulation_duration = self.workspace.enaction.command.duration / SIMULATION_SPEED / 1000.

        # Initialize all the required fields of the outcome because sometimes simulate() is not called
        self.simulated_outcome_dict = {"clock": self.workspace.enaction.clock,
                                       "action": self.workspace.enaction.action.action_code,
                                       "head_angle": self.workspace.enaction.predicted_outcome.head_angle,
                                       "echo_distance": self.workspace.enaction.predicted_outcome.echo_distance,
                                       'floor': self.workspace.enaction.predicted_outcome.floor,
                                       'yaw': self.workspace.enaction.predicted_outcome.yaw,
                                       'duration1': self.workspace.enaction.predicted_outcome.duration1,
                                       'color_index': self.workspace.enaction.predicted_outcome.color_index
                                       }

    def simulate(self, dt):
        """Simulate the enaction in the current memory"""
        enaction = self.workspace.enaction
        memory = self.workspace.memory

        # If the simulation is over, do nothing while waiting for the actual outcome
        if not self.is_simulating:
            return

        # Check whether target time is elapsed
        self.simulation_time += dt
        if self.simulation_time >= self.simulation_duration:
            # Adjust to the exact duration
            dt += self.simulation_duration - self.simulation_time
            self.is_simulating = False

        # The delta displacement
        translation = enaction.command.speed * dt * SIMULATION_SPEED
        yaw_quaternion = Quaternion.from_z_rotation(enaction.command.rotation_speed_rad * SIMULATION_SPEED * dt)
        displacement_matrix = translation_quaternion_to_matrix(-translation, yaw_quaternion.inverse)

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
        # Simulate the rotations in body memory
        memory.body_memory.body_quaternion = memory.body_memory.body_quaternion.cross(yaw_quaternion)

        # Simulate the movement of the head to the focus
        if memory.egocentric_memory.focus_point is not None:
            head_direction_degree, _ = point_to_head_direction_distance(memory.egocentric_memory.focus_point)
            # head_direction_degree = max(-90, min(head_direction_degree, 90))
            memory.body_memory.set_head_direction_degree(head_direction_degree)
        # else:
        #     head_direction_degree = memory.body_memory.head_direction_degree()

        # Simulate the movement of the head when SCAN
        if enaction.action.action_code == ACTION_SCAN:
            head_angle = -90 + 180 * self.simulation_time * SIMULATION_SPEED / enaction.action.target_duration
            memory.body_memory.set_head_direction_degree(head_angle)

        # Simulate the displacement in allocentric memory
        memory.allocentric_memory.robot_point += memory.body_memory.body_quaternion * Vector3(translation)

        # If terrain is not enclosed then check for floor cells
        if memory.phenomenon_memory.terrain_confidence() < PHENOMENON_ENCLOSED_CONFIDENCE:
            if enaction.action.action_code in [ACTION_FORWARD, ACTION_SWIPE]:
                i, j = point_to_cell(memory.allocentric_memory.robot_point +
                                     memory.body_memory.body_quaternion * Vector3([ROBOT_FLOOR_SENSOR_X, 0, 0]))
                # If crossed the line then stop the simulation
                # Must check before marking the place, and terminate to prevent overriding duration1
                if (memory.allocentric_memory.min_i <= i <= memory.allocentric_memory.max_i) and \
                        (memory.allocentric_memory.min_j <= j <= memory.allocentric_memory.max_j) and \
                        memory.allocentric_memory.grid[i][j].status[0] == EXPERIENCE_FLOOR:
                    self.is_simulating = False
                    self.simulated_outcome_dict['duration1'] = round(self.simulation_time * 1000)
                    if enaction.action.action_code == ACTION_FORWARD:
                        self.simulated_outcome_dict['floor'] = 3
                    else:
                        if enaction.command.speed[1] > 0:
                            # Swipe left
                            self.simulated_outcome_dict['floor'] = 2
                            self.simulated_outcome_dict['yaw'] = RETREAT_YAW
                        else:
                            # Swipe right
                            self.simulated_outcome_dict['floor'] = 1
                            self.simulated_outcome_dict['yaw'] = -RETREAT_YAW
                    self.simulated_outcome_dict['color_index'] = memory.allocentric_memory.grid[i][j].color_index
                else:
                    self.simulated_outcome_dict['floor'] = 0

        # If the terrain is enclosed, use the predicted outcome
        else:
            # Stop the simulation after the predicted duration1
            if self.simulation_time * 1000 > enaction.predicted_outcome.duration1:
                self.is_simulating = False

        # The echoes predicted from known phenomena
        echoes = [[enaction.predicted_outcome.head_angle, enaction.predicted_outcome.echo_distance]]
        # The echoes added by the user
        for ij in memory.allocentric_memory.user_cells:
            cell = memory.allocentric_memory.grid[ij[0]][ij[1]]
            if cell.status[1] == EXPERIENCE_ALIGNED_ECHO:
                p = cell.point()
                a, d = point_to_head_direction_distance(memory.allocentric_to_egocentric(p))
                if enaction.action.action_code == ACTION_SCAN and \
                        assert_almost_equal_angles(math.radians(a), 0, 125) or \
                        assert_almost_equal_angles(math.radians(a), memory.body_memory.head_direction_rad, 35):
                    echoes.append([a, d])
        # The closest echo
        np_echoes = np.array(echoes, dtype=int)
        a, d = np_echoes[np.argmin(np_echoes[:, 1])]
        self.simulated_outcome_dict['head_angle'], self.simulated_outcome_dict['echo_distance'] = int(a), int(d)

        # Mark the place
        memory.allocentric_memory.place_robot(memory.body_memory, enaction.clock)

    def end(self):
        """Terminate the simulation and return the simulated outcome"""
        # Empty the list of cells clicked by the user
        self.workspace.memory.allocentric_memory.user_cells = []
        # Force stop the simulation if it is not yet stopped
        self.is_simulating = False
        return Outcome(self.simulated_outcome_dict)
