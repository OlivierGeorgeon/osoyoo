from pyrr import matrix44
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .AllocentricMemory.GridCell import CELL_UNKNOWN, CELL_PHENOMENON
from .EgocentricMemory.Experience import EXPERIENCE_FOCUS


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self, hexagrid_size=(100, 200), cell_radius=40):
        self.body_memory = BodyMemory()
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = AllocentricMemory(hexagrid_size[0], hexagrid_size[1], cell_radius=cell_radius)

        self.focus_i = None  # It may rather belong to allocentric memory
        self.focus_j = None

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

        self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'], enacted_interaction['clock'])
        # self.allocentric_memory.place_robot(self.body_memory)  # Must call it after synthesizer

    def update_allocentric(self, phenomena, focus_point, clock):
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
        if self.focus_i is not None:
            self.allocentric_memory.grid[self.focus_i][self.focus_j].status[3] = CELL_UNKNOWN
        if focus_point is not None:
            allo_focus = self.egocentric_to_allocentric(focus_point)
            self.focus_i, self.focus_j = self.allocentric_memory.convert_pos_in_cell(allo_focus[0], allo_focus[1])
            self.allocentric_memory.grid[self.focus_i][self.focus_j].status[3] = EXPERIENCE_FOCUS

    def egocentric_to_allocentric(self, point):
        """Return the point in allocentric coordinates from the point in egocentric coordinates"""
        # Rotate the point by the body direction and add the body position
        return matrix44.apply_to_vector(self.body_memory.body_direction_matrix(), point) \
            + self.allocentric_memory.robot_point
