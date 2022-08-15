from . Memory.EgocentricMemory.MemoryV1 import MemoryV1
from . Memory.HexaMemory.HexaMemory import HexaMemory
from .Synthesizer.Synthesizer import Synthesizer
from .Agent.CircleBehavior import CircleBehavior
class Workspace :
    """Contain all the data of the model : the two memories, the synthesizer and the agent"""

    def __init__(self,hexamemory_size = (100,200), cell_radius = 20):
        self.memory = MemoryV1()
        self.hexa_memory = HexaMemory(hexamemory_size[0],hexamemory_size[1],cell_radius = cell_radius)
        self.synthesizer = Synthesizer(self.memory,self.hexa_memory)
        self.user_action = None
        #FLAGS :
        self.need_user_action = False
        self.enact_step = 0
        self.need_traitement_flag = False
        self.f_user_action_ready = False
        self.f_hexmem_changed = False
        self.f_memory_changed = False
        self.f_ready_for_hex_refresh = False
        self.f_inde_cell_projected = False
        
        self.f_reset_flag = False

        self.intended_interaction = {}
        # self.agent_action = None
        self.f_agent_action_ready = False
        # self.action_angle = None

        self.CONTROL_MODE_AUTOMATIC = "auto"
        self.CONTROL_MODE_MANUAL = "manual"
        self.control_mode = self.CONTROL_MODE_MANUAL

        # self.enacted_interaction = {} Commenté par Olivier le 5/6/2022
        self.f_enacted_interaction_has_changed = False
        self.f_new_things_in_memory = False

        self.f_ready_for_next_loop = True

        #self.agent = CircleBehavior()
        self.agent = None

    def reset(self):
        self.action_reset()
    def action_reset(self):
        print("A FAIRE") #TODO
        self.synthesizer.reset()
        self.memory.reset()
        self.hexa_memory.reset()
        self.f_reset_flag = True
        self.user_action = None
        #FLAGS :
        self.need_user_action = False
        self.enact_step = 0
        self.need_traitement_flag = False
        self.f_user_action_ready = False
        self.f_hexmem_changed = False
        self.f_memory_changed = False
        self.f_ready_for_hex_refresh = False
        self.f_inde_cell_projected = False
        
        self.f_reset_flag = False

        self.agent_action = None
        self.f_agent_action_ready = False
        self.action_angle = None

        self.CONTROL_MODE_AUTOMATIC = "auto"
        self.CONTROL_MODE_MANUAL = "manual"
        self.control_mode =  self.CONTROL_MODE_MANUAL


        self.enacted_interaction = {}
        self.f_enacted_interaction_has_changed = False
        self.f_new_things_in_memory = False

        self.f_ready_for_next_loop = True