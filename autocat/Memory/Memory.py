import numpy as np
from pyrr import matrix44
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .PhenomenonMemory.PhenomenonMemory import PhenomenonMemory
from .PhenomenonMemory.PhenomenonTerrain import ABS

HEXAGRID_WIDTH = 100
HEXAGRID_HEIGHT = 200
CELL_RADIUS = 40


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self):
        self.body_memory = BodyMemory()
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = AllocentricMemory(HEXAGRID_WIDTH, HEXAGRID_HEIGHT, cell_radius=CELL_RADIUS)
        self.phenomenon_memory = PhenomenonMemory()

    def __str__(self):
        return "Memory Robot position (" + str(round(self.allocentric_memory.robot_point[0])) + "," +\
                                           str(round(self.allocentric_memory.robot_point[1])) + ")"

    def update_and_add_experiences(self, enacted_interaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.manage_focus(enacted_interaction)

        self.body_memory.set_head_direction_degree(enacted_interaction['head_angle'])
        # TODO Keep the simulation and adjust the robot position
        # Translate the robot before applying the yaw
        self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'],
                                     enacted_interaction['clock'])
        self.body_memory.rotate_degree(enacted_interaction['yaw'], enacted_interaction['azimuth'])

        self.egocentric_memory.update_and_add_experiences(enacted_interaction, self.body_memory.body_direction_rad)

        # # TODO Keep the simulation and adjust the robot position
        # self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'],
        #                              enacted_interaction['clock'])

        # The integrator may subsequently update the robot's position

    def update_allocentric(self, clock):
        """Allocate the phenomena to the cells of allocentric memory"""
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
        saved_memory = Memory()
        # Clone body memory
        saved_memory.body_memory = self.body_memory.save()
        # Clone egocentric memory
        saved_memory.egocentric_memory = self.egocentric_memory.save()
        # Clone allocentric memory
        saved_memory.allocentric_memory = self.allocentric_memory.save(saved_memory.egocentric_memory.experiences)
        # Clone phenomenon memory
        saved_memory.phenomenon_memory = self.phenomenon_memory.save(saved_memory.egocentric_memory.experiences)

        return saved_memory

    def is_near_terrain_origin(self):
        """Return True if the robot is near the origin of the terrain"""
        if len(self.phenomenon_memory.phenomena) > 0:
            delta = self.phenomenon_memory.phenomena[0].origin_prompt() - self.allocentric_memory.robot_point
            return np.linalg.norm(delta) < 100
        else:
            return False
