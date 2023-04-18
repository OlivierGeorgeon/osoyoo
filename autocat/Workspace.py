import numpy as np
import math
from playsound import playsound
from pyrr import matrix44

from .Decider.AgentCircle import AgentCircle
from .Decider.Action import create_actions, ACTION_FORWARD, ACTION_ALIGN_ROBOT, ACTION_SCAN, SIMULATION_STEP_OFF, \
    ACTION_BACKWARD, ACTIONS, ACTION_LEFTWARD, ACTION_RIGHTWARD
from .Decider.Interaction import Interaction, OUTCOME_DEFAULT
from .Memory.Memory import Memory
from .Integrator.Integrator import Integrator
from .Robot.RobotDefine import DEFAULT_YAW, TURN_DURATION
from .Robot.Enaction import Enaction


KEY_DECIDER_CIRCLE = "A"  # Automatic mode: controlled by AgentCircle
KEY_DECIDER_USER = "M"  # Manual mode : controlled by the user

KEY_ENGAGEMENT_ROBOT = "R"  # The application controls the robot
KEY_ENGAGEMENT_IMAGINARY = "I"  # The application imagines the interaction

KEY_DECREASE_CONFIDENCE = "D"
KEY_INCREASE_CONFIDENCE = "P"

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

        self.decider_mode = KEY_DECIDER_USER
        self.engagement_mode = KEY_ENGAGEMENT_ROBOT
        self.interaction_step = INTERACTION_STEP_IDLE

        self.focus_point = None  # The point where the agent is focusing
        self.prompt_point = None  # The point where the agent is prompted do go

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
                self.intended_interaction = self.decider.propose_intended_interaction(self.enacted_interaction)
                self.interaction_step = INTERACTION_STEP_ENGAGING
            # Case DECIDER_KEY_USER is handled by self.process_user_key()

        # ENGAGING: Preparing the simulation and the enaction
        if self.interaction_step == INTERACTION_STEP_ENGAGING:
            # Add intended_interaction fields that are common to all deciders
            # self.intended_interaction["clock"] = self.clock
            # self.intended_interaction.modifier["clock"] = self.clock
            # if self.focus_point is not None:
            #     self.intended_interaction.modifier['focus_x'] = int(self.focus_point[0])
            #     self.intended_interaction.modifier['focus_y'] = int(self.focus_point[1])
            # Add the estimated speed to the interaction
            # if self.intended_interaction.action.action_code == ACTION_FORWARD:
            #     self.intended_interaction.modifier['speed'] = int(
            #         self.actions[ACTION_FORWARD].translation_speed[0])
            # if self.intended_interaction.action.action_code == ACTION_BACKWARD:
            #     self.intended_interaction.modifier['speed'] = -int(
            #         self.actions[ACTION_BACKWARD].translation_speed[0])
            # if self.intended_interaction.action.action_code == ACTION_LEFTWARD:
            #     self.intended_interaction.modifier['speed'] = int(
            #         self.actions[ACTION_LEFTWARD].translation_speed[1])
            # if self.intended_interaction.action.action_code == ACTION_RIGHTWARD:
            #     self.intended_interaction.modifier['speed'] = -int(
            #         self.actions[ACTION_RIGHTWARD].translation_speed[1])
            # Initialize the simulation of the action
            self.intended_interaction.interaction.action.start_simulation(self.intended_interaction)

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
                self.memory_snapshot = self.memory.save()
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
            if self.intended_interaction.interaction.action.simulation_step != SIMULATION_STEP_OFF:
                # target_duration = None
                self.intended_interaction.interaction.action.simulate(self.memory, dt)
            else:
                # End of the simulation
                # if self.engagement_mode == ENGAGEMENT_KEY_IMAGINARY:
                if self.is_imagining:
                    # Compute an imaginary enacted_interaction and proceed to integrating
                    self.update_enacted_interaction(self.imagine())
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
            self.integrator.integrate()

            # Update allocentric memory: robot, phenomena, focus
            self.memory.update_allocentric(self.integrator.phenomena, self.focus_point, self.prompt_point, self.clock)

            # Increment the clock if the enacted interaction was properly received
            if self.enacted_interaction['clock'] >= self.clock:  # don't increment if the robot is behind
                self.clock += 1

            self.interaction_step = INTERACTION_STEP_REFRESHING

        # REFRESHING: is handled by views and reset by CtrlPhenomenonDisplay

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
                playsound('autocat/Assets/R5.wav', False)
                print("LOST FOCUS")
        else:
            if enacted_interaction['action'] in [ACTION_SCAN, ACTION_FORWARD]:
                # Catch focus
                if 'echo_xy' in enacted_interaction:
                    print("CATCH FOCUS")
                    playsound('autocat/Assets/R11.wav', False)
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
        if user_key.upper() in [KEY_DECIDER_CIRCLE, KEY_DECIDER_USER]:
            self.decider_mode = user_key.upper()
        elif user_key.upper() in [KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY]:
            self.engagement_mode = user_key.upper()
        elif user_key.upper() in ACTIONS:
            # Other keys are considered actions and sent to the robot
            if self.interaction_step == INTERACTION_STEP_IDLE:
                intended_interaction = Interaction.create_or_retrieve(self.actions[user_key], OUTCOME_DEFAULT)
                self.intended_interaction = Enaction(intended_interaction, self.clock, self.focus_point, self.prompt_point)
                # # Go to the prompt point
                # if self.prompt_point is not None:
                #     if user_key in [ACTION_FORWARD, ACTION_BACKWARD]:
                #         duration = np.linalg.norm(self.prompt_point) / self.actions[ACTION_FORWARD].translation_speed[0]
                #         self.intended_interaction.modifier['duration'] = int(duration * 1000)
                #     if user_key == ACTION_ALIGN_ROBOT:
                #         angle = math.atan2(self.prompt_point[1], self.prompt_point[0])
                #         self.intended_interaction.modifier['angle'] = int(math.degrees(angle))
                # Focus on the focus point
                # if self.focus_point is not None:
                #     self.intended_interaction['focus_x'] = int(self.focus_point[0])  # Convert to python int
                #     self.intended_interaction['focus_y'] = int(self.focus_point[1])
                self.interaction_step = INTERACTION_STEP_ENGAGING
        if user_key.upper() == 'S':
            playsound('autocat/Assets/R3.wav', False)
            print("played")

    def imagine(self):
        """Return the imaginary enacted interaction"""
        # enacted_interaction = self.intended_interaction.copy()
        enacted_interaction = {'action': self.intended_interaction.interaction.action.action_code,
                               'clock': self.intended_interaction.clock}

        # action_code = self.intended_interaction['action']

        # TODO retrieve the position from memory
        # target_duration = self.intended_interaction.action.target_duration
        # rotation_speed = self.intended_interaction.action.rotation_speed_rad
        # # if action_code == ACTION_FORWARD:
        # if 'duration' in self.intended_interaction.modifier:
        #     target_duration = self.intended_interaction.modifier['duration'] / 1000
        # # if action_code == ACTION_ALIGN_ROBOT:
        # if 'angle' in self.intended_interaction.modifier:
        #     target_duration = math.fabs(self.intended_interaction.modifier['angle']) * TURN_DURATION / DEFAULT_YAW
        #     if self.intended_interaction.modifier['angle'] < 0:
        #         rotation_speed = -self.intended_interaction.action.rotation_speed_rad

        # displacement
        # translation = self.actions[action_code].translation_speed * target_duration
        # yaw_rad = rotation_speed * target_duration
        # No additional displacement because the displacement was already simulated
        translation = np.array([0, 0, 0], dtype=float)
        yaw_rad = 0

        translation_matrix = matrix44.create_from_translation(-translation)
        rotation_matrix = matrix44.create_from_z_rotation(yaw_rad)
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)

        enacted_interaction['translation'] = translation
        enacted_interaction['yaw'] = round(math.degrees(yaw_rad))
        enacted_interaction['azimuth'] = 0  # Is computed by body_memory
        enacted_interaction['displacement_matrix'] = displacement_matrix
        enacted_interaction['head_angle'] = 0
        enacted_interaction['points'] = []

        print("intended interaction", self.intended_interaction)
        print("enacted interaction", enacted_interaction)

        return enacted_interaction
