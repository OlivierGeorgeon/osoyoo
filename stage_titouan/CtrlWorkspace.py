
class CtrlWorkspace():
    """Controller for everything involved in workspace (memory,hexamem,synthe,decider)"""
    
    def __init__(self,workspace):
        """Constructor"""
        self.workspace = workspace
        self.synthesizer = workspace.synthesizer
        
        self.work_step = 0
        self.need_user_action = False
        self.user_action = None
        self.f_user_action_ready = False
        self.f_new_interaction_done = False
        self.enacted_interaction = b'{"status":"T"}'
        self.decision_mode = "manual"
        self.need_user_to_command_robot = False

        self.interaction_to_enact = None
        self.f_interaction_to_enact_ready = False
        self.cell_inde_a_traiter = None

    def main(self,dt):
        """Handle the workspace work, from the moment the robot interaction is done,
        to the moment we have an action to command"""
        if self.interaction_to_enact is not None:
            print("reçu par workspace")
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
                print("aaabbbbccc")
                if self.enacted_interaction['status'] is not "T":
                    print ("aaaaaaaaaaaaaaaaaaaaaa ,", self.enacted_interaction)
                    self.send_phenom_info_to_memory()
                    self.send_position_change_to_hexa_memory()
                    self.send_position_change_to_memory()
                print("aaaaaaaaaaaaaabbbbccc")
        #1. Start the synthesizer process
        self.synthesizer.act(self.user_action)
        self.user_action = None
        self.need_user_action = False

        if self.synthesizer.synthetizing_step in [0,2]:
            " tout s'est bien passé" #donc rien à faire de particulier
        elif self.synthesizer.synthetizing_step is 1 :
            "on a besoin d'une action de l'user sur l'hexaview"
            self.need_user_action = True
            self.cell_inde_a_traiter = self.synthesizer.indecisive_cells[-1]
            return
        elif self.synthesizer.synthetizing_step is 3 :
            "le synthé a besoin d'une action du robot"
            self.interaction_to_enact = self.synthesizer.get_interaction_needed()
            self.f_interaction_to_enact_ready = True
            return

        if self.decision_mode == "automatic" :
            #  2. Start the decider process
            "padagent pour le moment"
        else :
            self.need_user_to_command_robot = True


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