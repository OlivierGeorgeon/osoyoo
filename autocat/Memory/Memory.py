from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .HexaMemory.HexaMemory import HexaMemory


class Memory:
    """The Workspace serves as the general container of the robot's cognitive architecture.
        It gathers: the agent, the two memories, and the synthesizer.
    """

    def __init__(self, hexagrid_size=(100, 200), cell_radius=40):
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = HexaMemory(hexagrid_size[0], hexagrid_size[1], cell_radius=cell_radius)

    def update_and_add_experiences(self, enacted_interaction):
        """ Process the enacted interaction to update the memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.tick()  # TODO Improve the decay mechanism in egocentric memory
        self.egocentric_memory.update_and_add_experiences(enacted_interaction)

        self.allocentric_memory.azimuth = enacted_interaction['azimuth']
        self.allocentric_memory.move(enacted_interaction['yaw'], enacted_interaction['translation'][0],
                                     enacted_interaction['translation'][1])

        # Cells in allocentric memory are updated by the Synthesizer
