from .Decider.AgentCircle import AgentCircle
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator, TRUST_POSITION_PHENOMENON, TRUST_POSITION_ROBOT

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
        self.synthesizer = Integrator(self)  # Moved from workspace by OG 04/09/2022

        self.intended_interaction = None
        self.enacted_interaction = {}

        self.decider_mode = CONTROL_MODE_MANUAL
        self.trust_mode = TRUST_POSITION_ROBOT
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
        # focus_lost = False
        # If there is a new enacted interaction
        if self.has_new_enacted_interaction:
            self.has_new_enacted_interaction = False

            # Move the memories and add new experiences to egocentric memory
            # self.memory.egocentric_memory.tick()
            # self.memory.egocentric_memory.update_and_add_experiences(self.enacted_interaction)
            self.memory.update_and_add_experiences(self.enacted_interaction)

            # self.send_position_change_to_hexa_memory()

            self.flag_for_view_refresh = True

            # Call the synthesizer. Could return an action (not used)
            synthesizer_action = self.synthesizer.integrate()

            self.memory.allocentric_memory.place_robot(self.memory.body_memory)

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
            self.intended_interaction = self.agent.propose_intended_interaction(self.enacted_interaction)
            self.synthesizer.last_action_had_focus = 'focus_x' in self.intended_interaction
            self.synthesizer.last_action = self.intended_interaction
            self.has_new_action = True
            
    def get_intended_interaction(self):
        """Return (True, intended_interaction) if there is one, else (False, None)
        Reset the intended_interaction
        (Called by CtrlRobot)
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

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""
        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("The workspace received an empty enacted interaction")
            return
        self.enacted_interaction = enacted_interaction
        self.has_new_enacted_interaction = True

    def process_user_key(self, user_key):
        if user_key.upper() == "A":
            self.decider_mode = CONTROL_MODE_AUTOMATIC
        elif user_key.upper() == "M":
            self.decider_mode = CONTROL_MODE_MANUAL
        elif user_key.upper() == "R":
            self.trust_mode = TRUST_POSITION_ROBOT
        elif user_key.upper() == "P":
            self.trust_mode = TRUST_POSITION_PHENOMENON
        else:
            action = {"action": user_key}
            self.intended_interaction = action
            self.has_new_action = True

    # def set_action(self, action):
    #     """Set the action to enact (called by CtrlHexaview)"""
    #     self.intended_interaction = action
    #     self.has_new_action = True
    #
    # def put_decider_to_auto(self):
    #     """Put the decider in auto mode (called by CtrlHexaview)"""
    #     self.decider_mode = CONTROL_MODE_AUTOMATIC
    #
    # def put_decider_to_manual(self):
    #     """Put the decider in manual mode (called by CtrlHexaview)"""
    #     self.decider_mode = CONTROL_MODE_MANUAL
