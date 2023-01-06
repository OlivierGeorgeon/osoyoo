from .Decider.AgentCircle import AgentCircle
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator

CONTROL_MODE_AUTOMATIC = "auto"
CONTROL_MODE_MANUAL = "manual"

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_INTENDED = 1
INTERACTION_STEP_ENACTING = 2
INTERACTION_STEP_ENACTED = 3


class Workspace:
    """The Workspace supervises the interaction cycle. It produces the intended_interaction
    and processes the enacted interaction """
    def __init__(self):
        self.memory = Memory()
        self.decider = AgentCircle(self)
        self.integrator = Integrator(self)

        self.intended_interaction = None
        self.enacted_interaction = {}

        self.control_mode = CONTROL_MODE_MANUAL
        self.interaction_step = INTERACTION_STEP_IDLE
        self.intended_interaction_is_ready_to_send = False
        self.has_new_enacted_interaction = False
        self.has_new_outcome_been_treated = True
        self.flag_for_view_refresh = False

        self.focus_xy = None
        self.prompt_xy = None

        # Controls which phenomenon to display
        self.ctrl_phenomenon_view = None

        self.clock = 0

    def main(self, dt):
        """The main handler of the interaction cycle:
        organize the generation of the intended_interaction and the processing of the enacted_interaction."""
        # If AUTOMATIC mode then ask the Decider for the intended interaction
        if self.control_mode == CONTROL_MODE_AUTOMATIC:
            # If ready, ask the decider for a new intended interaction
            if self.intended_interaction is None and self.has_new_outcome_been_treated:
                if self.interaction_step == INTERACTION_STEP_IDLE:
                    self.intended_interaction = self.decider.propose_intended_interaction(self.enacted_interaction)
                    self.has_new_outcome_been_treated = False
                    self.intended_interaction_is_ready_to_send = True
                    self.interaction_step = INTERACTION_STEP_INTENDED

        # If there is a new enacted interaction
        if self.has_new_enacted_interaction:
            if self.interaction_step == INTERACTION_STEP_ENACTED:
                # Update body memory and egocentric memory
                self.memory.update_and_add_experiences(self.enacted_interaction)

                # Call the integrator to create and update the phenomena.
                self.integrator.integrate()

                # Update allocentric memory: robot, phénomena
                # self.memory.allocentric_memory.place_robot(self.memory.body_memory)
                self.memory.update_allocentric(self.integrator.phenomena)

                self.flag_for_view_refresh = True
                self.has_new_outcome_been_treated = True
                self.has_new_enacted_interaction = False
                self.interaction_step = INTERACTION_STEP_IDLE

    def get_intended_interaction(self):
        """If the workspace has a new intended interaction then return it, otherwise return None
        Reset the intended_interaction. (Called by CtrlRobot)
        """
        if self.intended_interaction_is_ready_to_send:
            if self.interaction_step == INTERACTION_STEP_INTENDED:
                self.intended_interaction_is_ready_to_send = False
                self.interaction_step = INTERACTION_STEP_ENACTING
                return self.intended_interaction

        return None

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""
        self.clock += 1
        enacted_interaction["clock"] = self.clock

        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("The workspace received an empty enacted interaction")
            # If CONTROL_MODE_AUTOMATIC resend the same intended interaction unless the user has set another one
            if self.control_mode == CONTROL_MODE_AUTOMATIC:
                self.intended_interaction_is_ready_to_send = True
                self.interaction_step = INTERACTION_STEP_INTENDED
            else:
                self.interaction_step = INTERACTION_STEP_IDLE
            return

        # Manage focus catch and lost
        if self.focus_xy is not None:
            # If the focus was kept then update it
            if 'focus' in enacted_interaction:
                if 'echo_xy' in enacted_interaction:  # Not sure why this is necessary
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
        self.interaction_step = INTERACTION_STEP_ENACTED

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() == "A":
            self.control_mode = CONTROL_MODE_AUTOMATIC
        elif user_key.upper() == "M":
            self.control_mode = CONTROL_MODE_MANUAL
        else:
            self.intended_interaction = {"action": user_key}
            if self.focus_xy is not None:
                self.intended_interaction['focus_x'] = int(self.focus_xy[0])
                self.intended_interaction['focus_y'] = int(self.focus_xy[1])
            self.intended_interaction_is_ready_to_send = True
            if self.interaction_step == INTERACTION_STEP_IDLE:
                self.interaction_step = INTERACTION_STEP_INTENDED
