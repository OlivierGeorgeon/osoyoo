class CtrlWorkspaceTest :
    """Blabla"""

    def __init__(self,workspace,ctrl_robot):
        """Constructor"""
        self.workspace = workspace
        self.ctrl_robot = ctrl_robot

        self.synthesizer = self.workspace.synthesizer
        
        self.flag_for_view_refresh = False

        self.enacted_interaction = {}
        self.has_new_outcome = False
        self.action = None
        self.has_new_action = False

        self.flag_for_need_of_action = True
    def main(self,dt):
        """Run the workspace"""
        # 1. We get the last outcome
        if self.ctrl_robot.has_new_outcome :            
            self.ctrl_robot.has_new_outcome = False
            outcome = self.ctrl_robot.outcome
            self.enacted_interaction = outcome
            # 2 We update the memories
            self.send_phenom_info_to_memory()
            self.send_position_change_to_hexa_memory()
            self.send_position_change_to_memory()
            self.flag_for_view_refresh = True
            #3 We call Synthesizer.Act and get the results
            synthesizer_action,synthesizer_results = self.workspace.synthesizer.act()
            #4 We update the hexamemory
            self.workspace.hexa_memory.update(synthesizer_results)
            #4 If the synthesizer need an action done, we save it
            if synthesizer_action is not None :
                self.action = synthesizer_action
        else :
            self.ctrl_robot.send_action(self.workspace.agent.action(None))
            
    def send_phenom_info_to_memory(self):
        """Send Enacted Interaction to Memory
        """
        # phenom_info = self.enacted_interaction['phenom_info']
        echo_array = self.enacted_interaction['echo_array'] if 'echo_array' in self.enacted_interaction else None
        #self.workspace.memory.update_memory(self.enacted_interaction['phenom_info'],echo_array)
        if self.workspace.memory is not None:
            self.workspace.memory.add_enacted_interaction(self.enacted_interaction)  # Added by Olivier 08/05/2022
            # self.workspace.memory.add(phenom_info)
            if echo_array is not None :
                self.workspace.memory.add_echo_array(echo_array)

    def send_position_change_to_memory(self):
        """Send position changes (angle,distance) to the Memory
        """
        if self.workspace.memory is not None :
            self.workspace.memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'])

    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.workspace.hexa_memory is not None:
            self.workspace.hexa_memory.azimuth = self.enacted_interaction['azimuth']
            self.workspace.hexa_memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'][0], self.enacted_interaction['translation'][1])
    