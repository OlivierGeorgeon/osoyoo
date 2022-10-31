from .Decider.AgentCircle import AgentCircle
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator, TRUST_POSITION_PHENOMENON, TRUST_POSITION_ROBOT

CONTROL_MODE_AUTOMATIC = "auto"
CONTROL_MODE_MANUAL = "manual"
# TRUST_POSITION_PHENOMENON = "Phenomenon"
# TRUST_POSITION_ROBOT = "Robot"


class Workspace:
    """The Workspace Controller provides the main logics to control the robot:
        - main(dt): Updates memory and hexa_memory. Get the synthesizer going
        - get_intended_interaction(): Update the intended_interaction (called by CtrlRobot) ??
        - update_enacted_interaction(): updates the enacted interaction (called by CtrlRobot)
        - set_action(), put_decider_to_auto(), updates the user actions (called by CtrlHexaview)
    """
    def __init__(self):
        """Constructor"""
        self.memory = Memory()
        self.agent = AgentCircle(self)
        self.integrator = Integrator(self)

        self.intended_interaction = None
        self.enacted_interaction = {}

        self.decider_mode = CONTROL_MODE_MANUAL
        self.trust_mode = TRUST_POSITION_PHENOMENON
        # self.robot_ready = True
        # self.flag_for_need_of_action = True
        self.has_new_intended_interaction = False
        self.has_new_enacted_interaction = False
        self.has_new_outcome_been_treated = True
        self.flag_for_view_refresh = False

        self.focus_xy = None
        self.prompt_xy = None

    def main(self, dt):
        """1) If a new enacted_interaction has been received
             - update memory and hexa_memory
             - get the synthesizer going
           3) If ready, ask for a new intended_interaction to enact
        """
        # If there is a new enacted interaction
        if self.has_new_enacted_interaction:
            # Move the memories and add new experiences to egocentric memory
            self.memory.update_and_add_experiences(self.enacted_interaction)
            self.flag_for_view_refresh = True

            # Call the integrator. Could return an action (not used)
            integrator_action = self.integrator.integrate()
            # Update the robot's place in allocentric memory in case the Integrator has changed it
            self.memory.allocentric_memory.place_robot(self.memory.body_memory)
            # If the integrator need an action done, we save it
            if integrator_action is not None:
                pass  # OG to prevent actions proposed by the synthesize
                # self.action = integrator_action
                # self.has_new_action = True

            self.has_new_outcome_been_treated = True
            self.has_new_enacted_interaction = False

        # If ready, ask for a new intended interaction
        if self.intended_interaction is None and self.decider_mode == CONTROL_MODE_AUTOMATIC and self.has_new_outcome_been_treated:
                # and self.robot_ready:
            # self.robot_ready = False
            self.has_new_outcome_been_treated = False
            self.intended_interaction = self.agent.propose_intended_interaction(self.enacted_interaction)
            # self.integrator.last_action_had_focus = 'focus_x' in self.intended_interaction
            # self.integrator.last_action = self.intended_interaction
            self.has_new_intended_interaction = True
            
    def get_intended_interaction(self):
        """If the workspace has a new intended interaction then return it, otherwise return None
        Reset the intended_interaction. (Called by CtrlRobot)
        """
        if self.has_new_intended_interaction:
            self.has_new_intended_interaction = False
            return self.intended_interaction
            # return intended_interaction
        else:
            return None

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""
        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("The workspace received an empty enacted interaction")
            return

        # Manage focus catch and lost
        if self.focus_xy is not None:
            # If the focus was kept then update it
            if 'focus' in enacted_interaction:
                self.focus_xy = enacted_interaction['echo_xy']
            # If the focus was lost then reset it
            if 'focus' not in enacted_interaction:
                # The focus was lost, override the echo outcome
                self.focus_xy = None
                print("LOST FOCUS")
        else:
            if self.intended_interaction['action'] in ["-", "8"]:
                # Catch focus
                if 'echo_xy' in enacted_interaction:
                    print("CATCH FOCUS")
                    self.focus_xy = enacted_interaction['echo_xy']

        self.enacted_interaction = enacted_interaction
        self.has_new_enacted_interaction = True
        self.intended_interaction = None

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
            self.intended_interaction = {"action": user_key}
            if self.focus_xy is not None:
                self.intended_interaction['focus_x'] = int(self.focus_xy[0])
                self.intended_interaction['focus_y'] = int(self.focus_xy[1])
            self.has_new_intended_interaction = True
