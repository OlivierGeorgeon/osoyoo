from ..  Synthesizer.SynthesizerUserInteraction import SynthesizerUserInteraction
class SynthesizerUserContext(SynthesizerUserInteraction):
    """Synthesizer that have two modes : 
    Manual and Automatic.
    In Manual mode, the user can interact with the synthesizer.
    In Automatic mode, the synthesizer will try to find the best action for the user.
    """
    def __init__(self,memory,hexa_memory):
        """
        :param memory: Memory object
        :param hexa_memory: HexaMemory object
        :param control_mode: "auto" or "manual"
        """
        self.memory = None
        self.hexa_memory = None
        self.internal_hexa_grid = None
        self.last_used_id = None
        self.interactions_list = None
        self.max_delta = None
        self.obstacles_list = None
        self.last_used_id_on_last_round = None
        self.mode = None

        self.indecisive_cells = None
        self.synthetizing_step = None  # 0: idle. 1: Projection ready, waiting for decision. 2: decision made, hexamem adjusted.
        self.decided_cells = None
        self.cells_to_wipe = None
        self.change_RETREAT_DISTANCE = None
        self.flag_no = None
        self.need_user_action = None

        self.indecisive_interactions = []
        super().__init__(memory,hexa_memory)

        self.AUTOMATIC_MODE = "automatic"
        self.MANUAL_MODE = "manual"
        self.current_mode = self.AUTOMATIC_MODE

    def set_mode(self, mode):
        """AUTOMATIC : synthesizer use the known context
        MANUAL : synthesizer use the user's input on divergences"""
        if mode != self.AUTOMATIC_MODE and mode != self.MANUAL_MODE:
            raise ValueError("Wrong mode : {}".format(mode))
        else :
            self.current_mode = mode



    def act(self):
        """blabla"""
        if self.current_mode == self.MANUAL_MODE:
            super().act()
        else : 
            self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
            real_echos = self.treat_echos()
            self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
            self.context_analysis(real_echos)
            self.project_interactions_on_internal_hexagrid()
            self.comparison_step()

    ### treat_echos(self) is inchanged from SynthesizerUserInteraction, so we don't reimplement it
    
    def context_analysis(self, real_echos):
        """Compare the positions of the real echos with the positions of the known obstacle"""
    def project_interactions_on_internal_hexagrid(self):

        
