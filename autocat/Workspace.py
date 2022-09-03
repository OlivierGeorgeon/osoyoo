from .Agent.AgentCircle import AgentCircle
from .Memory.EgocentricMemory.EgocentricMemory import EgocentricMemory
from .Memory.HexaMemory.HexaMemory import HexaMemory
from .Synthesizer.Synthesizer import Synthesizer

# CONTROL_MODE_AUTOMATIC = "auto"
# CONTROL_MODE_MANUAL = "manual"


class Workspace:
    """The Workspace serves as the general container of the robot's cognitive architecture.
    It contains all the processes and the data of the cognitive architecture:
        the agent, the two memories, and the synthesizer.
    """

    def __init__(self, hexamemory_size=(100, 200), cell_radius=40):
        self.agent = AgentCircle()
        self.memory = EgocentricMemory()
        self.hexa_memory = HexaMemory(hexamemory_size[0], hexamemory_size[1], cell_radius=cell_radius)
        self.synthesizer = Synthesizer(self.memory, self.hexa_memory)

        # self.user_action = None
        # self.need_user_action = False
        # self.enact_step = 0
        # self.need_treatment_flag = False
        # self.f_user_action_ready = False
        # self.f_hexmem_changed = False
        # self.f_memory_changed = False
        # self.f_ready_for_hex_refresh = False
        # self.f_inde_cell_projected = False
        
        # self.f_reset_flag = False

        # self.intended_interaction = {}
        # self.f_agent_action_ready = False

        # self.control_mode = CONTROL_MODE_MANUAL

        # self.f_enacted_interaction_has_changed = False
        # self.f_new_things_in_memory = False
        # self.f_ready_for_next_loop = True
