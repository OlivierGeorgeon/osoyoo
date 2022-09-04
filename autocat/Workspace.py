from .Memory.EgocentricMemory.EgocentricMemory import EgocentricMemory
from .Memory.HexaMemory.HexaMemory import HexaMemory


class Workspace:
    """The Workspace serves as the general container of the robot's cognitive architecture.
        It gathers: the agent, the two memories, and the synthesizer.
    """

    def __init__(self, hexamemory_size=(100, 200), cell_radius=40):
        self.egocentric_memory = EgocentricMemory()
        self.hexa_memory = HexaMemory(hexamemory_size[0], hexamemory_size[1], cell_radius=cell_radius)
