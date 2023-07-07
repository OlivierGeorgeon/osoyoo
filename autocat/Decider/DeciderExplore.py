########################################################################################
# This decider makes the robot explore the parts of the terrain that are not yet known
# Activation 0: default. 2: the terrain has an absolute reference
########################################################################################

import math
import numpy as np
from pyrr import quaternion, matrix44
from playsound import playsound
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD
from . Interaction import Interaction, OUTCOME_DEFAULT
from ..Robot.Enaction import Enaction
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from . Decider import Decider

CLOCK_TO_GO_HOME = 8  # Number of interactions before going home
# EXPLORATION_STEP_INIT = 0
# EXPLORATION_STEP_ROTATE = 1
# EXPLORATION_STEP_FORWARD = 2
# EXPLORATION_STEP_SWIPE_LEFT = 3
# EXPLORATION_STEP_SWIPE_RIGHT = 4
OUTCOME_ORIGIN = "O"
OUTCOME_LEFT = "LO"
OUTCOME_RIGHT = "RO"
OUTCOME_FAR_LEFT = "FL"
OUTCOME_FAR_RIGHT = "FR"
OUTCOME_COLOR = "CL"


class DeciderExplore(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        # self.workspace = workspace
        # self.anticipated_outcome = OUTCOME_DEFAULT

        # self.exploration_step = EXPLORATION_STEP_INIT
        point = np.array([-2000, 2000, 0])  # Begin with North West
        self.prompt_points = [point]
        # Visit 6 points from North West to south East every pi/6
        self.nb_points = 6
        rotation_matrix = matrix44.create_from_z_rotation(-math.pi/6)
        for i in range(1, self.nb_points):
            point = matrix44.apply_to_vector(rotation_matrix, point)
            self.prompt_points.append(point)
        self.prompt_index = 0
        self.action = "-"

    def activation_level(self):
        """The level of activation of this decider: 0: default, 2 if the terrain has an origin """
        activation_level = 0
        # Activate when the terrain phenomenon has an absolute point
        if TER in self.workspace.memory.phenomenon_memory.phenomena:
            if self.workspace.memory.phenomenon_memory.phenomena[TER].origin_point() is not None:
                activation_level = 2
        return activation_level

    # def propose_intended_enaction(self, enacted_enaction):
    #     """Propose the next intended enaction from the previous enacted interaction.
    #     This is the main method of the agent"""
    #     # Compute a specific outcome suited for this agent
    #     outcome = self.outcome(enacted_enaction)
    #     # Compute the intended enaction
    #     return self.intended_enaction(outcome)

    def outcome(self, enacted_enaction):
        """ Convert the enacted interaction into an outcome adapted to the explore behavior """
        outcome = OUTCOME_DEFAULT

        # On startup return DEFAULT
        if enacted_enaction is None:
            return outcome

        # If color outcome
        if enacted_enaction.outcome.color_index > 0:
            outcome = OUTCOME_COLOR
            print("Outcome color")

        # Look for the floor experience
        if enacted_enaction.outcome.floor > 0 and enacted_enaction.outcome.color_index == 0:
            # If the floor is not colored then figure out if the robot is on the right or on the left
            if self.workspace.memory.phenomenon_memory.phenomena[TER].absolute_affordance() is not None:
                relative_quaternion = quaternion.cross(self.workspace.memory.body_memory.body_quaternion,
                                      quaternion.inverse(self.workspace.memory.phenomenon_memory.phenomena[TER].absolute_affordance().experience.body_direction_quaternion()))
                print("Relative quaternion", repr(relative_quaternion))
                if quaternion.rotation_angle(relative_quaternion) > math.pi:
                    # relative_quaternion = -1 * relative_quaternion  # The quaternion representing the short angle
                    relative_quaternion = - relative_quaternion  # The quaternion representing the short angle
                rot = quaternion.rotation_angle(relative_quaternion)
                print("Rotation from origin", round(math.degrees(rot)))
                if quaternion.rotation_axis(relative_quaternion)[2] > 0:  # Positive z axis rotation
                    if rot < math.pi/3:
                        print("OUTCOME Left of origin")
                        outcome = OUTCOME_LEFT
                    elif rot < math.pi:
                        print("OUTCOME Far Left of origin")
                        outcome = OUTCOME_FAR_LEFT
                else:
                    if rot < math.pi/3:
                        print("OUTCOME Right of origin")
                        outcome = OUTCOME_RIGHT
                    elif rot < math.pi:
                        print("OUTCOME Far Right of origin")
                        outcome = OUTCOME_FAR_RIGHT
        return outcome

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Tracing the last interaction
        if self.action is not None:
            print("Action: " + str(self.action) + ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome))

        # Compute the next prompt point

        # If time to go home
        if TER in self.workspace.memory.phenomenon_memory.phenomena and \
           self.workspace.memory.phenomenon_memory.phenomena[TER].absolute_affordance() is not None and \
           self.workspace.clock - self.workspace.memory.phenomenon_memory.phenomena[TER].last_origin_clock > CLOCK_TO_GO_HOME:
            # If right or left then swipe to home
            if outcome in [OUTCOME_LEFT, OUTCOME_RIGHT]:
                if outcome == OUTCOME_RIGHT:
                    ego_confirmation = np.array([0, 280, 0], dtype=int)
                    # self.exploration_step = EXPLORATION_STEP_SWIPE_LEFT
                else:
                    ego_confirmation = np.array([0, -280, 0], dtype=int)
                    # self.exploration_step = EXPLORATION_STEP_SWIPE_RIGHT
                print("Swiping to confirmation by:", ego_confirmation)
                self.action = self.workspace.actions[ACTION_SWIPE]
                self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
                self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock,
                                                                          self.workspace.memory)
                playsound('autocat/Assets/R5.wav', False)
            # If not left or right we need to manoeuvre
            else:
                # If near home then go to confirmation prompt
                if self.workspace.memory.is_near_terrain_origin() or outcome == OUTCOME_COLOR:
                    allo_confirmation = self.workspace.memory.phenomenon_memory.phenomena[TER].confirmation_prompt()
                    print("Enacting confirmation affordance to", allo_confirmation)
                    ego_confirmation = self.workspace.memory.allocentric_to_egocentric(allo_confirmation)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
                    playsound('autocat/Assets/R4.wav', False)
                else:
                    # If not near home then go to origin prompt
                    allo_origin = self.workspace.memory.phenomenon_memory.phenomena[TER].origin_point()
                    print("Going from", self.workspace.memory.allocentric_memory.robot_point, "to origin sensor point", allo_origin)
                    ego_origin = self.workspace.memory.allocentric_to_egocentric(allo_origin)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_origin
                    playsound('autocat/Assets/R3.wav', False)
                self.action = self.workspace.actions[ACTION_TURN]
                self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock,
                                                                          self.workspace.memory)
                self.workspace.enactions[self.workspace.clock + 1] = Enaction(
                    self.workspace.actions[ACTION_FORWARD], self.workspace.clock + 1, self.workspace.memory)
                # self.exploration_step = EXPLORATION_STEP_ROTATE
        else:
            # Go to the most interesting pool point
            # mip = self.workspace.memory.allocentric_memory.most_interesting_pool(self.workspace.clock)
            # self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(mip)
            # Go successively to the predefined prompt points
            allo_prompt = self.prompt_points[self.prompt_index]
            ego_prompt = self.workspace.memory.allocentric_to_egocentric(allo_prompt)
            self.workspace.memory.egocentric_memory.prompt_point = ego_prompt
            self.prompt_index += 1
            if self.prompt_index >= self.nb_points:
                self.prompt_index = 0
            self.action = self.workspace.actions[ACTION_TURN]
            self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock,
                                                                      self.workspace.memory)
            self.workspace.enactions[self.workspace.clock + 1] = Enaction(self.workspace.actions[ACTION_FORWARD],
                                                                 self.workspace.clock + 1, self.workspace.memory)
            # self.exploration_step = EXPLORATION_STEP_ROTATE

        # If the robot is on a color patch and must enact confirmation affordance
        # (If already on a color then go to confirmation prompt rather than origin prompt)
        # This is used if the robot arrives on a color after turning to go directly to confirmation
        if TER in self.workspace.memory.phenomenon_memory.phenomena and \
            self.workspace.memory.phenomenon_memory.phenomena[TER].absolute_affordance() is not None and \
            self.workspace.clock - self.workspace.memory.phenomenon_memory.phenomena[TER].last_origin_clock \
                > CLOCK_TO_GO_HOME and outcome == OUTCOME_COLOR:
            allo_confirmation = self.workspace.memory.phenomenon_memory.phenomena[TER].confirmation_prompt()
            print("Enacting confirmation affordance to", allo_confirmation)
            ego_confirmation = self.workspace.memory.allocentric_to_egocentric(allo_confirmation)
            self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
            playsound('autocat/Assets/R4.wav', False)
