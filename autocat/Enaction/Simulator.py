import math
import numpy as np
from pyrr import Quaternion, Vector3, matrix44
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.BodyMemory import point_to_echo_direction_distance
from ..Decider.Action import ACTION_SWIPE, ACTION_FORWARD, ACTION_SCAN
from ..Robot.Outcome import Outcome
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ..Utils import assert_almost_equal_angles


class Simulator:
    def __init__(self, workspace):
        self.workspace = workspace
        self.is_simulating = False
        self.simulation_time = 0
        self.simulated_outcome_dict = {}

    def begin(self):
        """Begin the simulation"""
        self.is_simulating = True
        self.simulation_time = 0
        # Initialize all the required fields because sometimes simulate is not called
        self.simulated_outcome_dict = {"clock": self.workspace.enaction.clock,
                                       "action": self.workspace.enaction.action.action_code,
                                       "duration1": self.workspace.enaction.simulation_duration * 1000,
                                       "head_angle": self.workspace.enaction.predicted_outcome.head_angle,
                                       "echo_distance": self.workspace.enaction.predicted_outcome.echo_distance,
                                       "yaw": self.workspace.enaction.command.yaw,
                                       "floor": 0, "color_index": 0, "status": "S"}

    def simulate(self, dt):
        """Simulate the enaction in the current memory"""
        enaction = self.workspace.enaction
        memory = self.workspace.memory

        # If the simulation is over, do nothing while waiting for the actual outcome
        if not self.is_simulating:
            return

        # dt *= 2
        # Check whether target time is elapsed
        self.simulation_time += dt
        if self.simulation_time >= enaction.simulation_duration:
            dt += enaction.simulation_duration - self.simulation_time  # Adjust to the exact duration
            self.is_simulating = False
            self.simulated_outcome_dict['duration1'] = enaction.simulation_duration * 1000

        # The intermediate displacement
        yaw_quaternion = Quaternion.from_z_rotation((enaction.simulation_rotation_speed * dt))
        way = 1
        if enaction.action.action_code == ACTION_SWIPE and enaction.command.speed_y < 0:
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

        # If crossed the line then stop the simulation
        # Must check before marking the place, and terminate to prevent overriding duration1
        # floor = 0
        # color_index = 0
        # self.simulated_outcome_dict['yaw'] = round(
        #     math.degrees(quaternion_to_direction_rad(enaction.command.intended_yaw_quaternion)))
        if memory.phenomenon_memory.terrain_confidence() < PHENOMENON_RECOGNIZED_CONFIDENCE:
            if enaction.action.action_code in [ACTION_FORWARD, ACTION_SWIPE]:
                floor_i, floor_j = point_to_cell(memory.allocentric_memory.robot_point +
                                                 memory.body_memory.body_quaternion * Vector3([ROBOT_FLOOR_SENSOR_X,
                                                                                               0, 0]))
                if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
                        (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
                        memory.allocentric_memory.grid[floor_i][floor_j].status[0] == EXPERIENCE_FLOOR:
                    self.is_simulating = False
                    self.simulated_outcome_dict['duration1'] = round(self.simulation_time * 1000)
                    if enaction.action.action_code == ACTION_FORWARD:
                        self.simulated_outcome_dict['floor'] = 3
                    else:
                        if enaction.command.speed_y > 0:
                            # Swipe left
                            self.simulated_outcome_dict['floor'] = 2
                            self.simulated_outcome_dict['yaw'] = 45
                        else:
                            # Swipe right
                            self.simulated_outcome_dict['floor'] = 1
                            self.simulated_outcome_dict['yaw'] = -45
                    self.simulated_outcome_dict['color_index'] = memory.allocentric_memory.grid[floor_i][floor_j].color_index
                else:
                    self.simulated_outcome_dict['floor'] = 0
        else:
            # If the terrain is recognized, use the predicted outcome
            self.simulated_outcome_dict['floor'] = enaction.predicted_outcome.floor
            self.simulated_outcome_dict['yaw'] = enaction.predicted_outcome.yaw
            self.simulated_outcome_dict['duration1'] = enaction.predicted_outcome.duration1
            self.simulated_outcome_dict['color_index'] = enaction.predicted_outcome.color_index
            # Stop the simulation after the predicted duration1
            if self.simulation_time * 1000 > enaction.predicted_outcome.duration1:
                self.is_simulating = False

        # Compute the simulated echo
        echoes = [[enaction.predicted_outcome.head_angle, enaction.predicted_outcome.echo_distance]]
        # for p in [p for p in self.workspace.memory.phenomenon_memory.phenomena.values() if p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO]:
        #     ego_center_point = self.workspace.memory.allocentric_to_egocentric(p.point)
        #     a, d = point_to_echo_direction_distance(ego_center_point)
        #     # Subtract the phenomenon's radius to obtain the egocentric echo distance
        #     d -= self.workspace.memory.phenomenon_memory.phenomenon_categories[BOX].long_radius
        #     if d > 0 and enaction.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90) or \
        #             assert_almost_equal_angles(math.radians(a), math.radians(head_direction_degree), 35):
        #         echoes.append([a, d])

        # Process the cells added by the user
        for ij in memory.allocentric_memory.user_cells:
            cell = memory.allocentric_memory.grid[ij[0]][ij[1]]
            if cell.status[1] == EXPERIENCE_ALIGNED_ECHO:
                p = cell.point()
                a, d = point_to_echo_direction_distance(memory.allocentric_to_egocentric(p))
                if enaction.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90) or \
                        assert_almost_equal_angles(math.radians(a), math.radians(head_direction_degree), 35):
                    echoes.append([a, d])
        np_echoes = np.array(echoes, dtype=int)
        a, d = np_echoes[np.argmin(np_echoes[:, 1])]
        self.simulated_outcome_dict['head_angle'], self.simulated_outcome_dict['echo_distance'] = int(a), int(d)

        # Mark the place
        memory.allocentric_memory.place_robot(memory.body_memory, enaction.clock)
        #
        # return self.is_simulating

    def end(self):
        """Terminate the simulation and return the simulated outcome"""
        # Empty the list of cells to be processed
        self.workspace.memory.allocentric_memory.user_cells = []
        self.is_simulating = False
        return Outcome(self.simulated_outcome_dict)
