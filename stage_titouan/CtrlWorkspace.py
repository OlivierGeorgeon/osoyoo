class CtrlWorkspace:
    """The Workspace Controller provides the main logics to controll the robot
        - main(dt): Updates memory and hexa_memory. Get the synthesizer going
        - get_intended_interaction(): Update the intended_interaction (called by CtrlRobot) ??
        - update_enacted_interaction(): updates the enacted interaction (called by CtrlRobot)
        - set_action(), put_decider_to_auto(), updates the user actions (called by CtrlHexaview)
        """

    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.intended_interaction = None
        self.enacted_interaction = {}

        self.decider_mode = "manual"
        self.robot_ready = True
        self.flag_for_need_of_action = True
        self.has_new_action = False
        self.has_new_enacted_interaction = False
        self.has_new_outcome_been_treated = True
        self.flag_for_view_refresh = False

    def main(self, dt):
        """1) If a new enacted_interaction has been received
             - update memory and hexa_memory
             - get the synthesizer going
           3) If ready, ask for a new intended_interaction to enact"""
        focus_lost = False
        # 1. If there is a new enacted interaction
        if self.has_new_enacted_interaction:
            self.has_new_enacted_interaction = False

            # 2 We update the memories
            self.workspace.memory.tick()
            self.send_phenom_info_to_memory()
            self.send_position_change_to_hexa_memory()
            self.send_position_change_to_memory()
            self.flag_for_view_refresh = True

            # 3 We call Synthesizer.Act and get the results, the synthesizer will update the hexa_memory
            synthesizer_action, synthesizer_results, focus_lost = self.workspace.synthesizer.act()

            # 4 If the synthesizer need an action done, we save it
            if synthesizer_action is not None:
                pass  # OG to prevent actions proposed by the synthesize
                # self.action = synthesizer_action
                # self.has_new_action = True
            self.has_new_outcome_been_treated = True

        # 2 If ready, ask for a new intended interaction
        if self.intended_interaction is None and self.decider_mode == "auto" and self.has_new_outcome_been_treated \
                and self.robot_ready:
            self.robot_ready = False
            self.has_new_outcome_been_treated = False
            # outcome_ag = self.workspace.agent.result(self.enacted_interaction)
            # self.action = self.workspace.agent.action(outcome_ag, focus_lost)
            self.intended_interaction = self.workspace.agent.propose_intended_interaction(self.enacted_interaction, focus_lost)
            self.workspace.synthesizer.last_action_had_focus = 'focus_x' in self.intended_interaction
            self.workspace.synthesizer.last_action = self.intended_interaction
            self.has_new_action = True
            
    def send_phenom_info_to_memory(self):
        """Send Enacted Interaction to Memory
        """
        echo_array = self.enacted_interaction['echo_array'] if 'echo_array' in self.enacted_interaction else None
        if self.workspace.memory is not None:
            self.workspace.memory.add_enacted_interaction(self.enacted_interaction)  # Added by Olivier 08/05/2022
            if echo_array is not None:
                self.workspace.memory.add_echo_array(echo_array)
            # if self.intended_interaction is not None:
            #     self.workspace.memory.add_action(self.intended_interaction)

    def send_position_change_to_memory(self):
        """Send position changes (angle,distance) to the Memory
        """
        if self.workspace.memory is not None:
            self.workspace.memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'])

    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.workspace.hexa_memory is not None:
            self.workspace.hexa_memory.azimuth = self.enacted_interaction['azimuth']
            self.workspace.hexa_memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'][0],
                                            self.enacted_interaction['translation'][1])
    
    def get_intended_interaction(self):
        """Return (True, intended_interaction) if there is one, else (False, None)
        Reset the intended_interaction
        Called by CtrlRobot"""
        if self.has_new_action:
            self.has_new_action = False
            if 'focus_x' in self.intended_interaction:
                self.workspace.synthesizer.last_action_had_focus = True
            # returno = True, self.intended_interaction
            returno = self.intended_interaction
            self.intended_interaction = None
            return returno
        else:
            # return False, None
            return None

    def set_action(self, action):
        """Set the action to enact (called by CtrlHexaview)"""
        self.intended_interaction = action
        self.has_new_action = True

    def put_decider_to_auto(self):
        """Put the decider in auto mode (called by CtrlHexaview)"""
        self.decider_mode = "auto"

    def put_decider_to_manual(self):
        """Put the decider in manual mode (called by CtrlHexaview)"""
        self.decider_mode = "manual"

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""
        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("CtrlWorkspaceTest received empty outcome")
            return
        self.enacted_interaction = enacted_interaction
        self.has_new_enacted_interaction = True
    
    def change_agent(self, agent):
        # self.agent = agent
        self.workspace.agent = agent
