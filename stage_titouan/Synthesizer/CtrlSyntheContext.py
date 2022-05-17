class CtrlSyntheContext():
    """j'essaie de simplifier le bordel"""
    def __init__(self,workspace):
        self.workspace = workspace
        self.synthesizer = workspace.synthesizer
        self.need_user_action = False
        self.user_action = None


    def main(self,dt):
        """handle the schmilblik"""
        if self.need_user_action and self.workspace.f_user_action_ready :
            self.user_action = self.workspace.user_action
            self.workspace.user_action = None
            self.workspace.f_user_action_ready = False
            self.synthesizer.user_action = self.user_action
        synthesizer = self.synthesizer
        synthesizer.act()
        #synthesizer.synthesize()
        self.need_user_action = synthesizer.synthetizing_step == 1
        if self.need_user_action : print("need user action")
        self.workspace.cell_inde_a_traiter = self.workspace.synthesizer.indecisive_cells[-1] if self.need_user_action else []
        self.workspace.need_user_action = self.need_user_action
        
