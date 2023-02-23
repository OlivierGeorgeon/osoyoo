from pyrr import matrix44
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .AllocentricMemory.GridCell import CELL_UNKNOWN, CELL_PHENOMENON

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

    def update_and_add_experiences(self, enacted_interaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.body_memory.set_head_direction_degree(enacted_interaction['head_angle'])
        self.body_memory.rotate_degree(enacted_interaction['yaw'], enacted_interaction['azimuth'])

        self.egocentric_memory.update_and_add_experiences(enacted_interaction, self.body_memory.body_direction_rad)

        self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'],
                                     enacted_interaction['clock'])
        # The integrator may subsequently update the robot's position

    def update_allocentric(self, phenomena, focus_point, prompt_point, clock):
        """Allocate the phenomena to the cells of allocentric memory"""
        # Clear the previous phenomena
        self.allocentric_memory.clear_phenomena()
        # Place the phenomena again
        for p in phenomena:
            for a in p.affordances:
                # Attribute the status of the affordance
                cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(a.point[0]+p.point[0],
                                                                             a.point[1]+p.point[1])
                self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, a.experience.type, a.experience.clock)
                # Attribute this phenomenon to this cell
                self.allocentric_memory.grid[cell_x][cell_y].phenomenon = p
            cell_i, cell_j = self.allocentric_memory.convert_pos_in_cell(p.point[0], p.point[1])
            self.allocentric_memory.apply_status_to_cell(cell_i, cell_j, CELL_PHENOMENON, clock)  # Mark the origin

        # Place the affordances that are not attached to phenomena
        for affordance in self.allocentric_memory.affordances:
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(affordance.point[0], affordance.point[1])
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, affordance.experience.type, clock)

        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory, clock)

        # Update the focus in allocentric memory
        allo_focus = self.egocentric_to_allocentric(focus_point)
        self.allocentric_memory.update_focus(allo_focus)
        # Update the prompt in allocentric memory
        allo_prompt = self.egocentric_to_allocentric(prompt_point)
        self.allocentric_memory.update_prompt(allo_prompt)

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
        # Subtract the body position and rotate the point by the opposite body direction
        ego_point = point - self.allocentric_memory.robot_point
        rotation_matrix = matrix44.create_from_z_rotation(self.body_memory.body_direction_rad)
        return matrix44.apply_to_vector(rotation_matrix, ego_point)

    def save(self):
        """Return a clone of memory to save a snapshot"""
        saved_memory = Memory()
        # Copy body memory
        saved_memory.body_memory = self.body_memory.save()
        # saved_memory.body_memory.head_direction_rad = self.body_memory.head_direction_rad
        # saved_memory.body_memory.body_direction_rad = self.body_memory.body_direction_rad

        # Copy egocentric memory
        saved_memory.egocentric_memory = self.egocentric_memory.save()

        # Copy allocentric memory
        # saved_memory.allocentric_memory.robot_point = self.allocentric_memory.robot_point.copy()
        # TODO use the experiences that were cloned in saved egocentric memory
        saved_memory.allocentric_memory = self.allocentric_memory.save()

        return saved_memory
