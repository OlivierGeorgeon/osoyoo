class CtrlWorkspace:
    """Handle the logic of the workspace
    Is send the last enacted interaction by CtrlRobot and the last 
    user interaction by CtrlHexaview
    Use those data to:
    1) update memory and hexa_memory 
    2) get the synthesizer going
    3) retrieve a new action to enact (which is retrieved by CtrlRobot externally)"""

    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.synthesizer = self.workspace.synthesizer
        self.flag_for_view_refresh = False
        self.enacted_interaction = {}
        self.has_new_outcome = False
        self.action = None
        self.has_new_action = False
        self.decider_mode = "manual"
        self.flag_for_need_of_action = True
        self.agent = self.workspace.agent
        self.has_new_outcome_been_treated = True
        self.robot_ready = True

    def main(self, dt):
        """1) update memory and hexa_memory 
           2) get the synthesizer going
           3) retrieve a new action to enact (which is retrieved by CtrlRobot externally)"""
        focus_lost = False
        # 1. We get the last outcome
        if self.has_new_outcome :            
            self.has_new_outcome = False
            # 2 We update the memories
            self.workspace.memory.tick()
            self.send_phenom_info_to_memory()
            self.send_position_change_to_hexa_memory()
            self.send_position_change_to_memory()
            self.flag_for_view_refresh = True
            #3 We call Synthesizer.Act and get the results, the synthesizer will update the hexa_memory
            synthesizer_action,synthesizer_results, focus_lost = self.workspace.synthesizer.act()
            #4 If the synthesizer need an action done, we save it
            if synthesizer_action is not None :
                self.action = synthesizer_action
                self.has_new_action = True
            self.has_new_outcome_been_treated = True
        if self.action is None and self.decider_mode == "auto" and self.has_new_outcome_been_treated and self.robot_ready :
            self.robot_ready = False
            self.has_new_outcome_been_treated = False
            outcome_ag = self.workspace.agent.result(self.enacted_interaction)
            self.action = self.workspace.agent.action(outcome_ag, focus_lost)
            self.workspace.synthesizer.last_action_had_focus = 'focus_x' in self.action
            self.synthesizer.last_action = self.action
            self.has_new_action = True
            
    def send_phenom_info_to_memory(self):
        """Send Enacted Interaction to Memory
        """
        echo_array = self.enacted_interaction['echo_array'] if 'echo_array' in self.enacted_interaction else None
        if self.workspace.memory is not None:
            self.workspace.memory.add_enacted_interaction(self.enacted_interaction)  # Added by Olivier 08/05/2022
            if echo_array is not None :
                self.workspace.memory.add_echo_array(echo_array)
            if self.action is not None :
                self.workspace.memory.add_action(self.action)

    def send_position_change_to_memory(self):
        """Send position changes (angle,distance) to the Memory
        """
        if self.workspace.memory is not None :
            self.workspace.memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'])

    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.workspace.hexa_memory is not None:
            self.workspace.hexa_memory.azimuth = self.enacted_interaction['azimuth']
            self.workspace.hexa_memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'][0],
                                            self.enacted_interaction['translation'][1])
    
    def get_action_to_enact(self):
        """Return True,action_to_enact if there is a new action else
        return False,None"""
        if self.has_new_action :
            self.has_new_action = False
            if 'focus_x' in self.action :
                self.workspace.synthesizer.last_action_had_focus = True
            returno = True,self.action
            self.action = None
            return returno
        else :
            return False,None
        
    def set_action(self,action):
        """Set the action to enact"""
        self.action = action
        self.has_new_action = True

    def put_decider_to_auto(self):
        """Put the decider in auto mode"""
        self.decider_mode = "auto"

    def put_decider_to_manual(self):
        """Put the decider in manual mode"""
        self.decider_mode = "manual"

    def update_outcome(self, outcome):
        "Update the enacted interaction"
        if "status" in outcome and outcome["status"] == "T":
            print("CtrlWorkspaceTest received empty outcome")
            return
        self.enacted_interaction = outcome
        self.has_new_outcome = True
    
    def change_agent(self, agent):
        self.agent = agent
        self.workspace.agent = agent
