from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .AllocentricMemory.GridCell import CELL_UNKNOWN, CELL_PHENOMENON


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self, hexagrid_size=(100, 200), cell_radius=40):
        self.body_memory = BodyMemory()
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = AllocentricMemory(hexagrid_size[0], hexagrid_size[1], cell_radius=cell_radius)

    def update_and_add_experiences(self, enacted_interaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.body_memory.set_head_direction_degree(enacted_interaction['head_angle'])
        self.body_memory.rotate_degree(enacted_interaction['yaw'], enacted_interaction['azimuth'])

        # self.egocentric_memory.tick()
        self.egocentric_memory.update_and_add_experiences(enacted_interaction, self.body_memory.body_direction_rad)

        self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'])
        # self.allocentric_memory.place_robot(self.body_memory)  # Must call it after synthesizer

    def update_allocentric(self, phenomena):
        """Allocate the phenomena to the cells of allocentric memory"""
        # Clear the previous phenomena
        self.allocentric_memory.clear_phenomena()
        # Place the phenomena again
        for p in phenomena:
            for a in p.affordances:
                # Attribute the status of the affordance
                cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(a.point[0]+p.point[0],
                                                                             a.point[1]+p.point[1])
                self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, a.experience.type)
                # Attribute this phenomenon to this cell
                self.allocentric_memory.grid[cell_x][cell_y].phenomenon = p
            cell_i, cell_j = self.allocentric_memory.convert_pos_in_cell(p.point[0], p.point[1])
            self.allocentric_memory.apply_status_to_cell(cell_i, cell_j, CELL_PHENOMENON)  # Mark the origin
            # self.allocentric_memory.grid[cell_i][cell_j].allocate_phenomenon(p)  # Mark the origin of the phenomenon

        # Place the affordances that are not attached to phenomena
        for affordance in self.allocentric_memory.affordances:
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(affordance.point[0], affordance.point[1])
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, affordance.experience.type)

        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory)

    # def decay(self, clock):
    #     """Remove the experiences from egocentric memory when they are two lod"""
    #     self.egocentric_memory.decay(clock)
