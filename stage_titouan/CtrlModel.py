class CtrlModel():
    """Controller for everything involved in workspace (memory,hexamem,synthe,decider)"""
    
    def __init__(self,workspace):
        """Constructor"""
        self.workspace = workspace
        self.synthesizer = workspace.synthesizer
        self.need_user_action = False
        self.work_step = 0
        self.user_action = None
        self.f_new_interaction_done = False
        self.enacted_interaction = {}

    def main(self,dt):
        """Handle the workspace work, from the moment the robot interaction is done,
        to the moment we have an action to command"""
        if self.f_new_interaction_done :
            self.f_new_interaction_done = False
            if self.work_step == 0 or self.work_step == 4:
                #Whole processus has ended normally, now we :
                #0. Update the memory with the last interaction
                # and change position in hexa_memory and memory
                #1. Start the synthesizer process
                # If the synthesizer process is finished :
                    #2. Start the decider process
                    #3. Send the command to the robot (i.e. update command_robot and let CtrlRobot use it)
                # Else we need to send the command given by the synthesizer to the robot

                #0. Update the memory with the last interaction and change position in hexa_memory and memory
                self.send_phenom_info_to_memory()
                self.send_position_change_to_hexa_memory()
                self.send_position_change_to_memory()

                #1. Start the synthesizer process
                self.synthesizer.act()

                if self.synthesizer.synthetizing_step is in [0,2]:


        


    def send_phenom_info_to_memory(self):
        """Send Enacted Interaction to Memory
        """
        # phenom_info = self.enacted_interaction['phenom_info']
        echo_array = self.enacted_interaction['echo_array']
        if self.workspace.memory is not None:
            self.workspace.memory.add_enacted_interaction(self.enacted_interaction)  # Added by Olivier 08/05/2022
            # self.workspace.memory.add(phenom_info)
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