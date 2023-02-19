import numpy as np
import math
import copy
from pyrr import matrix44

from .Decider.AgentCircle import AgentCircle
from .Decider.Action import create_actions, ACTION_FORWARD, ACTION_ALIGN_ROBOT, ACTION_SCAN
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator
from .Robot.RobotDefine import DEFAULT_YAW, TURN_DURATION


DECIDER_KEY_CIRCLE = "A"  # Automatic mode: controlled by AgentCircle
DECIDER_KEY_USER = "M"  # Manual mode : controlled by the user

ENGAGEMENT_KEY_ROBOT = "R"  # The application controls the robot
ENGAGEMENT_KEY_IMAGINARY = "I"  # The application imagines the interaction

INTERACTION_STEP_IDLE = 0
INTERACTION_STEP_ENGAGING = 1
INTERACTION_STEP_INTENDING = 2
INTERACTION_STEP_ENACTING = 3
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

        self.intended_interaction = None
        self.enacted_interaction = {}

        self.decider_mode = DECIDER_KEY_USER
        self.engagement_mode = ENGAGEMENT_KEY_ROBOT
        self.interaction_step = INTERACTION_STEP_IDLE

        self.focus_point = None  # The point where the agent is focusing
        self.prompt_point = None  # The point where the agent is prompted do go

        # Controls which phenomenon to display
        self.ctrl_phenomenon_view = None

        self.clock = 0
        self.memory_for_simulation = copy.deepcopy(self.memory)
        self.memory_for_imaginary = None
        self.is_imagining = False

    def main(self, dt):
        """The main handler of the interaction cycle:
        organize the generation of the intended_interaction and the processing of the enacted_interaction."""
        # IDLE: Ready to choose the next intended interaction
        if self.interaction_step == INTERACTION_STEP_IDLE:
            if self.decider_mode == DECIDER_KEY_CIRCLE:
                # The decider chooses the next interaction
                self.intended_interaction = self.decider.propose_intended_interaction(self.enacted_interaction)
                self.interaction_step = INTERACTION_STEP_ENGAGING
            # Case DECIDER_KEY_USER is handled by self.process_user_key()

        # ENGAGING: Preparing the simulation and the enaction
        if self.interaction_step == INTERACTION_STEP_ENGAGING:
            # Add intended_interaction fields that are common to all deciders
            self.intended_interaction["clock"] = self.clock
            # Save a snapshot of memory
            self.actions[self.intended_interaction['action']].is_simulating = True
            if self.engagement_mode == ENGAGEMENT_KEY_ROBOT:
                # If engagement robot then send the command to the robot
                self.interaction_step = INTERACTION_STEP_INTENDING
                if self.is_imagining:
                    # Stop imagining and restore memory
                    self.memory.body_memory.body_direction_rad = self.memory_for_imaginary.body_memory.body_direction_rad
                    self.memory.allocentric_memory.robot_point = self.memory_for_imaginary.allocentric_memory.robot_point
                    self.is_imagining = False
            else:
                # If imagining then proceed to simulating the enaction
                self.interaction_step = INTERACTION_STEP_ENACTING
                if not self.is_imagining:
                    # Start imagining, save the memory
                    self.memory_for_imaginary = copy.deepcopy(self.memory)
                    self.is_imagining = True
            self.memory_for_simulation = copy.deepcopy(self.memory)

        # INTENDING: is handled by CtrlRobot

        # ENACTING: update body memory during the robot enaction or the imaginary simulation
        if self.interaction_step == INTERACTION_STEP_ENACTING:
            if self.actions[self.intended_interaction['action']].is_simulating:
                target_duration = None
                self.actions[self.intended_interaction['action']].simulate(self.memory, self.intended_interaction, dt)
            else:
                # End of the simulation
                if self.engagement_mode == ENGAGEMENT_KEY_IMAGINARY:
                    # Compute an imaginary enacted_interaction and proceed to integrating
                    self.update_enacted_interaction(self.imagine())
                    self.interaction_step = INTERACTION_STEP_INTEGRATING
                    # self.interaction_step = INTERACTION_STEP_REFRESHING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == INTERACTION_STEP_INTEGRATING:
            # Retrieve the memory before simulation
            self.memory.body_memory.body_direction_rad = self.memory_for_simulation.body_memory.body_direction_rad
            self.memory.allocentric_memory.robot_point = self.memory_for_simulation.allocentric_memory.robot_point

            # Update body memory and egocentric memory
            self.memory.update_and_add_experiences(self.enacted_interaction)

            # Call the integrator to create and update the phenomena
            self.integrator.integrate()

            # Update allocentric memory: robot, phenomena, focus
            self.memory.update_allocentric(self.integrator.phenomena, self.focus_point, self.prompt_point, self.clock)

            # Increment the clock if the enacted interaction was properly received
            if self.enacted_interaction['clock'] >= self.clock:  # don't increment if the robot is behind
                self.clock += 1

            self.interaction_step = INTERACTION_STEP_REFRESHING

        # REFRESHING: is handle by views and reset by CtrlPhenomenonDisplay

    def get_intended_interaction(self):
        """If the workspace has a new intended interaction then return it, otherwise return None
        Reset the intended_interaction. (Called by CtrlRobot)
        """
        if self.interaction_step == INTERACTION_STEP_INTENDING:
            self.interaction_step = INTERACTION_STEP_ENACTING
            return self.intended_interaction

        return None

    def update_enacted_interaction(self, enacted_interaction):
        """Update the enacted interaction (called by CtrlRobot)"""

        if "status" in enacted_interaction and enacted_interaction["status"] == "T":
            print("The workspace received an empty enacted interaction")
            self.memory.body_memory.body_direction_rad = self.memory_for_simulation.body_memory.body_direction_rad
            self.memory.allocentric_memory.robot_point = self.memory_for_simulation.allocentric_memory.robot_point

            # Reset the interaction step
            if self.decider_mode == DECIDER_KEY_CIRCLE:
                # If automatic mode then resend the same intended interaction unless the user has set another one
                self.interaction_step = INTERACTION_STEP_INTENDING
            else:
                # If user mode then abort the enaction and wait for a new action but don't increment the clock
                self.interaction_step = INTERACTION_STEP_IDLE
            return

        # # Increment the clock if the enacted interaction was properly received
        # if enacted_interaction['clock'] >= self.clock:  # don't increment if the robot is behind
        #     self.clock += 1

        # Manage focus catch and lost
        if self.focus_point is not None:
            # If the focus was kept then update it
            if 'focus' in enacted_interaction:
                if 'echo_xy' in enacted_interaction:  # Not sure why this is necessary
                    self.focus_point = np.array([enacted_interaction['echo_xy'][0],
                                                 enacted_interaction['echo_xy'][1], 0])
            # If the focus was lost then reset it
            if 'focus' not in enacted_interaction:
                # The focus was lost, override the echo outcome
                self.focus_point = None
                print("LOST FOCUS")
        else:
            if self.intended_interaction['action'] in [ACTION_SCAN, ACTION_FORWARD]:
                # Catch focus
                if 'echo_xy' in enacted_interaction:
                    print("CATCH FOCUS")
                    self.focus_point = np.array([enacted_interaction['echo_xy'][0],
                                                 enacted_interaction['echo_xy'][1], 0])

        # Move the prompt
        if self.prompt_point is not None:
            self.prompt_point = matrix44.apply_to_vector(enacted_interaction['displacement_matrix'], self.prompt_point)

        self.enacted_interaction = enacted_interaction
        self.intended_interaction = None
        self.interaction_step = INTERACTION_STEP_INTEGRATING

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() in [DECIDER_KEY_CIRCLE, DECIDER_KEY_USER]:
            self.decider_mode = user_key.upper()
        elif user_key.upper() in [ENGAGEMENT_KEY_ROBOT, ENGAGEMENT_KEY_IMAGINARY]:
            self.engagement_mode = user_key.upper()
        else:
            # Other keys are considered actions and sent to the robot
            if self.interaction_step == INTERACTION_STEP_IDLE:
                self.intended_interaction = {"action": user_key}
                # Go to the prompt point
                if self.prompt_point is not None:
                    if user_key == ACTION_FORWARD:
                        duration = np.linalg.norm(self.prompt_point) / self.actions[ACTION_FORWARD].translation_speed[0]
                        self.intended_interaction['duration'] = int(duration * 1000)
                    if user_key == ACTION_ALIGN_ROBOT:
                        angle = math.atan2(self.prompt_point[1], self.prompt_point[0])
                        self.intended_interaction['angle'] = int(math.degrees(angle))
                # Focus on the focus point
                if self.focus_point is not None:
                    self.intended_interaction['focus_x'] = int(self.focus_point[0])  # Convert to python int
                    self.intended_interaction['focus_y'] = int(self.focus_point[1])
                self.interaction_step = INTERACTION_STEP_ENGAGING

    def imagine(self):
        """Return the imaginary enacted interaction"""
        enacted_interaction = self.intended_interaction.copy()
        action_code = self.intended_interaction['action']

        # TODO retrieve the position from memory
        target_duration = self.actions[action_code].target_duration
        rotation_speed = self. actions[action_code].rotation_speed_rad
        if action_code == ACTION_FORWARD:
            if 'duration' in self.intended_interaction:
                target_duration = self.intended_interaction['duration'] / 1000
        if action_code == ACTION_ALIGN_ROBOT:
            if 'angle' in self.intended_interaction:
                target_duration = math.fabs(self.intended_interaction['angle']) * TURN_DURATION / DEFAULT_YAW
                if self.intended_interaction['angle'] < 0:
                    rotation_speed = -self.actions[action_code].rotation_speed_rad

        # displacement
        translation = self.actions[action_code].translation_speed * target_duration
        yaw_rad = rotation_speed * target_duration

        translation_matrix = matrix44.create_from_translation(-translation)
        rotation_matrix = matrix44.create_from_z_rotation(yaw_rad)
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

        enacted_interaction['translation'] = translation
        enacted_interaction['yaw'] = round(math.degrees(yaw_rad))
        enacted_interaction['azimuth'] = 0  # Is computed by bodymemory
        enacted_interaction['displacement_matrix'] = displacement_matrix
        enacted_interaction['head_angle'] = 0
        enacted_interaction['points'] = []

        print("intended interaction", self.intended_interaction)
        print("enacted interaction", enacted_interaction)

        return enacted_interaction
