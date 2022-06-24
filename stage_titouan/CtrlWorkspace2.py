from .Agent.CircleBehavior import CircleBehavior

class CtrlWorkspace2():
    """Workspace controller for synthesizerauto"""

    def __init__(self,workspace,need_user_to_command_robot= True):
        """Constructor"""
        self.workspace = workspace
        self.synthesizer = workspace.synthesizer
        self.f_new_interaction_done = False
        self.work_step = 0
        self.enacted_interaction = {'status': 'T'}
        self.interaction_to_enact = {'action' : '0'}
        self.flag_for_view_refresh = False
        self.agent = CircleBehavior()
        self.f_interaction_to_enact_ready = False
        self.need_user_to_command_robot = need_user_to_command_robot
    def reset(self):
        """Reset"""
        self.workspace.reset()

    def main(self,dt):
        """Handle the workspace work, from the moment the robot interaction is done,
        to the moment we have an action to command"""
        if self.interaction_to_enact is None :
            self.interaction_to_enact = {'action' : '0'}
        if self.f_new_interaction_done :
            self.flag_for_view_refresh = True
            self.f_new_interaction_done = False
            
            if self.enacted_interaction['status'] != "T":
                    # Update the memories
                    self.send_phenom_info_to_memory()
                    self.send_position_change_to_hexa_memory()
                    self.send_position_change_to_memory()
                    #do the synthesizer work
                    action_synthe=self.synthesizer.act()
                    print("AGNGNGNGNGNGNG")
                    if(not self.f_interaction_to_enact_ready):
                        if action_synthe is not None:
                            print("ACTION SYNTHE :", action_synthe)
                            print("INTERACTIONO TO ENACTO :", self.interaction_to_enact)
                            self.interaction_to_enact["action"] = action_synthe
                            self.f_interaction_to_enact_ready = True
                            #return action_synthe
                        elif not self.need_user_to_command_robot:
                                outcome = self.agent.result(self.enacted_interaction)
                                action = self.agent.action(outcome)
                                self.interaction_to_enact = self.agent.intended_interaction(action)
                                self.f_interaction_to_enact_ready = True
                        else :
                            self.interaction_to_enact["action"] = '8'
                            self.f_interaction_to_enact_ready = True
            print("self.interaction_to_enact :", self.interaction_to_enact)
            
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
    