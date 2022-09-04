from .Decider.AgentCircle import AgentCircle
from .Memory.Memory import Memory
from .Synthesizer.Synthesizer import Synthesizer

CONTROL_MODE_AUTOMATIC = "auto"
CONTROL_MODE_MANUAL = "manual"


class Workspace:
    """The Workspace Controller provides the main logics to control the robot:
        - main(dt): Updates memory and hexa_memory. Get the synthesizer going
        - get_intended_interaction(): Update the intended_interaction (called by CtrlRobot) ??
        - update_enacted_interaction(): updates the enacted interaction (called by CtrlRobot)
        - set_action(), put_decider_to_auto(), updates the user actions (called by CtrlHexaview)
    """

    def __init__(self):
        """Constructor"""
        self.agent = AgentCircle()
        self.memory = Memory()
        self.synthesizer = Synthesizer(self)  # Moved from workspace by OG 04/09/2022

        self.intended_interaction = None
        self.enacted_interaction = {}

        self.decider_mode = CONTROL_MODE_MANUAL
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
           3) If ready, ask for a new intended_interaction to enact
        """
        focus_lost = False
        # If there is a new enacted interaction
        if self.has_new_enacted_interaction:
            self.has_new_enacted_interaction = False

            # Assimilate the enacted interaction in egocentric memory
            self.memory.egocentric_memory.tick()  # TODO Improve the decay mechanism in egocentric memory
            self.memory.egocentric_memory.assimilate(self.enacted_interaction)

            # Update position in hexa memory
            self.send_position_change_to_hexa_memory()

            # Add new experiences to memory
            self.flag_for_view_refresh = True

            # We call Synthesizer.Act and get the results, the synthesizer will update the hexa_memory
            synthesizer_action, synthesizer_results, focus_lost = self.synthesizer.act()

            # If the synthesizer need an action done, we save it
            if synthesizer_action is not None:
                pass  # OG to prevent actions proposed by the synthesize
                # self.action = synthesizer_action
                # self.has_new_action = True
            self.has_new_outcome_been_treated = True

        # If ready, ask for a new intended interaction
        if self.intended_interaction is None and self.decider_mode == CONTROL_MODE_AUTOMATIC and self.has_new_outcome_been_treated \
                and self.robot_ready:
            self.robot_ready = False
            self.has_new_outcome_been_treated = False
            self.intended_interaction = self.agent.propose_intended_interaction(self.enacted_interaction,
                                                                                          focus_lost)
            self.synthesizer.last_action_had_focus = 'focus_x' in self.intended_interaction
            self.synthesizer.last_action = self.intended_interaction
            self.has_new_action = True
            
    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.memory.hexa_memory is not None:
            self.memory.hexa_memory.azimuth = self.enacted_interaction['azimuth']
            self.memory.hexa_memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'][0],
                                         self.enacted_interaction['translation'][1])
    
    def get_intended_interaction(self):
        """Return (True, intended_interaction) if there is one, else (False, None)
        Reset the intended_interaction
        Called by CtrlRobot
        """
        if self.has_new_action:
            self.has_new_action = False
            if 'focus_x' in self.intended_interaction:
                self.synthesizer.last_action_had_focus = True
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
        self.decider_mode = CONTROL_MODE_AUTOMATIC

    def put_decider_to_manual(self):
        """Put the decider in manual mode (called by CtrlHexaview)"""
        self.decider_mode = CONTROL_MODE_MANUAL

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""
        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("CtrlWorkspaceTest received empty outcome")
            return
        self.enacted_interaction = enacted_interaction
        self.has_new_enacted_interaction = True
