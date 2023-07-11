import math
import numpy as np
from pyrr import matrix44, quaternion, Quaternion
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .PhenomenonMemory.PhenomenonMemory import PhenomenonMemory, TER
from .AllocentricMemory.Hexagonal_geometry import CELL_RADIUS
from ..Decider.Action import ACTION_SWIPE
# from ..Utils import rotate_vector_z


GRID_WIDTH = 100   # Number of cells wide
GRID_HEIGHT = 200  # Number of cells high
NEAR_HOME = 300    # (mm) Max distance to consider near home
SIMULATION_TIME_RATIO = 1  # 0.5   # The simulation speed is slower than the real speed because ...
# SIMULATION_STEP_OFF = 0
# SIMULATION_STEP_ON = 1  # More step will be used to take wifi transmission time into account


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.body_memory = BodyMemory(robot_id)
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = AllocentricMemory(GRID_WIDTH, GRID_HEIGHT, cell_radius=CELL_RADIUS)
        self.phenomenon_memory = PhenomenonMemory()
        self.body_direction_deltas = {}  # Used to calibrate GYRO_COEF

    def __str__(self):
        return "Memory Robot position (" + str(round(self.allocentric_memory.robot_point[0])) + "," +\
                                           str(round(self.allocentric_memory.robot_point[1])) + ")"

    def update_and_add_experiences(self, enacted_enaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.focus_point = enacted_enaction.focus_point
        self.egocentric_memory.prompt_point = enacted_enaction.prompt_point

        self.body_memory.set_head_direction_degree(enacted_enaction.outcome.head_angle)
        # TODO Keep the simulation and adjust the robot position
        # Translate the robot before applying the yaw
        # self.allocentric_memory.move(self.body_memory.get_body_direction_rad(), enacted_enaction.translation,
        #                              enacted_enaction.clock)
        self.allocentric_memory.move(self.body_memory.body_quaternion, enacted_enaction.translation,
                                     enacted_enaction.clock)
        self.body_memory.body_quaternion = enacted_enaction.body_quaternion

        # Keep a dictionary of the direction deltas to check gyro_coef is correct
        self.body_direction_deltas[enacted_enaction.clock] = enacted_enaction.body_direction_delta
        self.body_direction_deltas = {key: d for key, d in self.body_direction_deltas.items() if key > enacted_enaction.clock-10 }
        print("Average delta compass-yaw:", round(math.degrees(np.mean(list(self.body_direction_deltas.values()))), 2))

        self.egocentric_memory.update_and_add_experiences(enacted_enaction)

        # # TODO Keep the simulation and adjust the robot position
        # self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'],
        #                              enacted_interaction['clock'])

        # The integrator may subsequently update the robot's position

    def update_allocentric(self, clock):
        """Update allocentric memory on the basis of body, phenomenon, and egocentric memory"""
        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory, clock)

        # Mark the affordances
        self.allocentric_memory.update_affordances(self.phenomenon_memory.phenomena, clock)

        # Update the focus in allocentric memory
        allo_focus = self.egocentric_to_allocentric(self.egocentric_memory.focus_point)
        self.allocentric_memory.update_focus(allo_focus, clock)

        # Update the prompt in allocentric memory
        allo_prompt = self.egocentric_to_allocentric(self.egocentric_memory.prompt_point)
        self.allocentric_memory.update_prompt(allo_prompt, clock)

    def egocentric_to_polar_egocentric(self, point):
        """Return the position of the point relative to the robot in absolute polar direction"""
        if point is None:
            return None
        return quaternion.apply_to_vector(self.body_memory.body_quaternion, point)
        # return matrix44.apply_to_vector(self.body_memory.body_direction_matrix(), point)

    def egocentric_to_allocentric(self, point):
        """Return the point in allocentric coordinates from the point in egocentric coordinates"""
        # Rotate the point by the body direction and add the body position
        if point is None:
            return None
        return matrix44.apply_to_vector(self.body_memory.body_direction_matrix(), point) \
            + self.allocentric_memory.robot_point

    def allocentric_to_egocentric(self, point):
        """Return the point in egocentric coordinates from the point in allocentric coordinates"""
        if point is None:
            return None
        # Subtract the body position
        ego_point = point - self.allocentric_memory.robot_point
        # Rotate the point by the opposite body direction using the transposed rotation matrix
        return matrix44.apply_to_vector(self.body_memory.body_direction_matrix().T, ego_point)

    def save(self):
        """Return a clone of memory for memory snapshot"""
        saved_memory = Memory(self.robot_id)
        # Clone body memory
        saved_memory.body_memory = self.body_memory.save()
        # Clone egocentric memory
        saved_memory.egocentric_memory = self.egocentric_memory.save()
        # Clone allocentric memory
        saved_memory.allocentric_memory = self.allocentric_memory.save(saved_memory.egocentric_memory.experiences)
        # Clone phenomenon memory
        saved_memory.phenomenon_memory = self.phenomenon_memory.save(saved_memory.egocentric_memory.experiences)
        saved_memory.body_direction_deltas = {key: d for key, d in self.body_direction_deltas.items()}

        return saved_memory

    def is_near_terrain_origin(self):
        """Return True if the robot is near the origin of the terrain"""
        if TER in self.phenomenon_memory.phenomena:
            delta = self.phenomenon_memory.phenomena[TER].origin_point() - self.allocentric_memory.robot_point
            return np.linalg.norm(delta) < NEAR_HOME
        else:
            return False

    def simulate(self, enaction, dt):
        """Simulate the enaction in memory. Return True during the simulation, and False when it ends"""

        # Check the target time
        ongoing_simulation = True
        enaction.simulation_time += dt
        if enaction.simulation_time >= enaction.simulation_duration:
            dt += enaction.simulation_duration - enaction.simulation_time  # Adjust to the exact duration
            ongoing_simulation = False

        # The intermediate displacement
        yaw_quaternion = Quaternion.from_z_rotation((enaction.simulation_rotation_speed * dt))
        way = 1
        if enaction.action.action_code == ACTION_SWIPE and enaction.command.speed is not None and enaction.command.speed < 0:
            way = -1
        translation = enaction.action.translation_speed * dt * SIMULATION_TIME_RATIO * way
        yaw_matrix = matrix44.create_from_inverse_of_quaternion(yaw_quaternion)
        translation_matrix = matrix44.create_from_translation(-translation)
        displacement_matrix = matrix44.multiply(yaw_matrix, translation_matrix)

        # Simulate the displacement of experiences
        for experience in self.egocentric_memory.experiences.values():
            experience.displace(displacement_matrix)
        # Simulate the displacement of the focus and prompt
        if self.egocentric_memory.focus_point is not None:
            self.egocentric_memory.focus_point = matrix44.apply_to_vector(displacement_matrix,
                                                                            self.egocentric_memory.focus_point)
        if self.egocentric_memory.prompt_point is not None:
            self.egocentric_memory.prompt_point = matrix44.apply_to_vector(displacement_matrix,
                                                                             self.egocentric_memory.prompt_point)
        # Displacement in body memory
        self.body_memory.body_quaternion = self.body_memory.body_quaternion.cross(yaw_quaternion)

        # Update allocentric memory
        self.allocentric_memory.robot_point += quaternion.apply_to_vector(self.body_memory.body_quaternion, translation)
        self.allocentric_memory.place_robot(self.body_memory, enaction.clock)

        return ongoing_simulation
