import numpy as np
import math
from playsound import playsound
from pyrr import matrix44

from .Decider.AgentCircle import AgentCircle
from .Decider.Action import create_actions, ACTION_FORWARD, ACTIONS, ACTION_ALIGN_ROBOT
from .Decider.Interaction import Interaction, OUTCOME_DEFAULT
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator
from .Robot.Enaction import Enaction, SIMULATION_STEP_OFF
from .Robot.CtrlRobot import INTERACTION_STEP_INTENDING, INTERACTION_STEP_ENACTING

KEY_DECIDER_CIRCLE = "A"  # Automatic mode: controlled by AgentCircle
KEY_DECIDER_USER = "M"  # Manual mode : controlled by the user
KEY_ENGAGEMENT_ROBOT = "R"  # The application controls the robot
KEY_ENGAGEMENT_IMAGINARY = "I"  # The application imagines the interaction
KEY_DECREASE_CONFIDENCE = "D"
KEY_INCREASE_CONFIDENCE = "P"
KEY_CLEAR = "C"

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_ENGAGING = 1
# INTERACTION_STEP_INTENDING = 2
# INTERACTION_STEP_ENACTING = 3
INTERACTION_STEP_INTEGRATING = 4
INTERACTION_STEP_REFRESHING = 5


class Workspace:
    """The Workspace supervises the interaction cycle. It produces the intended_interaction
    and processes the enacted interaction """
    def __init__(self):
        self.actions = create_actions()

        self.memory = Memory()
        self.decider = AgentCircle(self)
        self.integrator = Integrator(self)

        self.intended_enaction = None
        self.enactions = {}  # The stack of enactions to enact next
        self.enacted_interaction = {}

        self.decider_mode = KEY_DECIDER_USER
        self.engagement_mode = KEY_ENGAGEMENT_ROBOT
        self.interaction_step = INTERACTION_STEP_IDLE

        # Controls which phenomenon to display
        self.ctrl_phenomenon_view = None

        self.clock = 0
        self.memory_snapshot = None
        self.is_imagining = False

    def main(self, dt):
        """The main handler of the interaction cycle:
        organize the generation of the intended_interaction and the processing of the enacted_interaction."""
        # IDLE: Ready to choose the next intended interaction
        if self.interaction_step == INTERACTION_STEP_IDLE:
            if self.decider_mode == KEY_DECIDER_CIRCLE:
                # The decider chooses the next interaction
                # self.intended_enaction = self.decider.propose_intended_enaction(self.enacted_interaction)
                self.enactions[self.clock] = self.decider.propose_intended_enaction(self.enacted_interaction)
                # self.interaction_step = INTERACTION_STEP_ENGAGING
            if self.clock in self.enactions:
                # Take the nextenaction from the stack
                self.intended_enaction = self.enactions[self.clock]
                self.interaction_step = INTERACTION_STEP_ENGAGING
            # Case DECIDER_KEY_USER is handled by self.process_user_key()

        # ENGAGING: Preparing the simulation and the enaction
        if self.interaction_step == INTERACTION_STEP_ENGAGING:
            # Initialize the simulation of the action
            self.intended_enaction.start_simulation()

            # Manage the memory snapshot
            if self.is_imagining:
                # If stop imagining then restore memory from the snapshot
                if self.engagement_mode == KEY_ENGAGEMENT_ROBOT:
                    self.memory = self.memory_snapshot.save()  # Keep the snapshot saved
                    self.is_imagining = False
                    # print("Restored", self.memory)
                # (If continue imagining then keep the previous snapshot)
            else:
                # If was not previously imagining then take a new memory snapshot
                self.memory_snapshot = self.memory.save()  # Fail when trying to save an affordance created during imaginary
                if self.engagement_mode == KEY_ENGAGEMENT_IMAGINARY:
                    # Start imagining
                    self.is_imagining = True

            # Manage the imaginary mode
            if self.is_imagining:
                # If imagining then proceed to simulating the enaction
                self.interaction_step = INTERACTION_STEP_ENACTING
            else:
                # If engagement robot then send the command to the robot
                self.interaction_step = INTERACTION_STEP_INTENDING

        # INTENDING: is handled by CtrlRobot

        # ENACTING: update body memory during the robot enaction or the imaginary simulation
        if self.interaction_step == INTERACTION_STEP_ENACTING:
            if self.intended_enaction.simulation_step != SIMULATION_STEP_OFF:
                self.intended_enaction.simulate(self.memory, dt)
            else:
                # End of the simulation
                if self.is_imagining:
                    # Compute an imaginary enacted_interaction and proceed to integrating
                    self.update_enacted_interaction(self.intended_enaction.imagine())
                    self.interaction_step = INTERACTION_STEP_INTEGRATING
                    # self.interaction_step = INTERACTION_STEP_REFRESHING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == INTERACTION_STEP_INTEGRATING:
            # If not imagining then restore the memory from the snapshot
            if not self.is_imagining:
                self.memory = self.memory_snapshot
            # (If imagining then keep the imagined memory until back to robot engagement mode)

            # Update body memory and egocentric memory
            self.memory.update_and_add_experiences(self.enacted_interaction)

            # Call the integrator to create and update the phenomena
            # Currently we don't create phenomena in imaginary mode because phenomena are not saved in memory
            # TODO save the phenomena in memory so they can be created during imaginary mode
            if not self.is_imagining:
                self.integrator.integrate()

            # Update allocentric memory: robot, phenomena, focus
            self.memory.update_allocentric(self.integrator.phenomena, self.clock)

            # Increment the clock if the enacted interaction was properly received
            if self.enacted_interaction['clock'] >= self.clock:  # don't increment if the robot is behind
                self.clock += 1

            self.interaction_step = INTERACTION_STEP_REFRESHING

        # REFRESHING: is handled by views and reset by CtrlPhenomenonDisplay

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""

        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("The workspace received an empty enacted interaction")
            # restore memory from snapshot
            self.memory = self.memory_snapshot

            # Reset the interaction step
            if self.decider_mode == KEY_DECIDER_CIRCLE:
                # If automatic mode then resend the same intended interaction unless the user has set another one
                self.interaction_step = INTERACTION_STEP_INTENDING
            else:
                # If user mode then abort the enaction and wait for a new action but don't increment the clock
                self.interaction_step = INTERACTION_STEP_IDLE
                # TODO # Refresh the views to show memory before simulation
            return

        # # Increment the clock if the enacted interaction was properly received
        # if enacted_interaction['clock'] >= self.clock:  # don't increment if the robot is behind
        #     self.clock += 1

        self.enacted_interaction = enacted_interaction
        self.intended_enaction = None
        self.interaction_step = INTERACTION_STEP_INTEGRATING

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() in [KEY_DECIDER_CIRCLE, KEY_DECIDER_USER]:
            self.decider_mode = user_key.upper()
        elif user_key.upper() in [KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY]:
            self.engagement_mode = user_key.upper()
        elif user_key.upper() in ACTIONS:
            # Keys that correspond to actions
            if self.interaction_step == INTERACTION_STEP_IDLE:
                ii = Interaction.create_or_retrieve(self.actions[user_key], OUTCOME_DEFAULT)
                self.enactions[self.clock] = Enaction(ii, self.clock, self.memory.egocentric_memory.focus_point, self.memory.egocentric_memory.prompt_point)
                # self.interaction_step = INTERACTION_STEP_ENGAGING
                if user_key.upper() == ACTION_ALIGN_ROBOT and self.memory.egocentric_memory.prompt_point is not None:
                    ii2 = Interaction.create_or_retrieve(self.actions[ACTION_FORWARD], OUTCOME_DEFAULT)
                    self.enactions[self.clock + 1] = Enaction(ii2, self.clock + 1, self.memory.egocentric_memory.focus_point, self.memory.egocentric_memory.prompt_point)

        if user_key.upper() == KEY_CLEAR:
            # Clear the stack of enactions
            playsound('autocat/Assets/R3.wav', False)
            self.enactions = {}
