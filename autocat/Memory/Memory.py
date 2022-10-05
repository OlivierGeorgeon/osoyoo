from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory


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
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.body_memory.set_head_direction_degree(enacted_interaction['head_angle'])
        # self.body_memory.set_body_direction_degree(enacted_interaction['azimuth'])
        self.body_memory.rotate_degree(enacted_interaction['yaw'], enacted_interaction['azimuth'])

        self.egocentric_memory.tick()  # TODO Improve the decay mechanism in egocentric memory
        self.egocentric_memory.update_and_add_experiences(enacted_interaction)

        self.allocentric_memory.move(self.body_memory.body_direction_rad, enacted_interaction['translation'])