########################################################################################
# This decider makes the robot explore the parts of the terrain that are not yet known
########################################################################################

import math
import numpy as np
from pyrr import quaternion
from playsound import playsound
from . Action import ACTION_ALIGN_ROBOT, ACTION_FORWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD
from . Interaction import Interaction, OUTCOME_DEFAULT
from ..Robot.Enaction import Enaction
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from ..Memory.PhenomenonMemory.PhenomenonTerrain import ABS
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR

EXPLORATION_STEP_INIT = 0
EXPLORATION_STEP_ROTATE = 1
EXPLORATION_STEP_FORWARD = 2
EXPLORATION_STEP_SWIPE_LEFT = 3
EXPLORATION_STEP_SWIPE_RIGHT = 4
OUTCOME_ORIGIN = "O"
OUTCOME_LEFT = "LO"
OUTCOME_RIGHT = "RO"
OUTCOME_FAR_LEFT = "FL"
OUTCOME_FAR_RIGHT = "FR"


class DeciderExplore:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT

        self.exploration_step = EXPLORATION_STEP_INIT
        self.prompt_point = np.array([-2000, 2000, 0])

    def propose_intended_enaction(self, enacted_interaction):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(enacted_interaction)
        # Compute the intended enaction
        return self.intended_enaction(outcome)

    def outcome(self, enacted_interaction):
        """ Convert the enacted interaction into an outcome adapted to the explore behavior """
        outcome = OUTCOME_DEFAULT
        # If the enacted experiences include a floor experience
        for e in [e for e in self.workspace.memory.egocentric_memory.experiences.values() if e.type == EXPERIENCE_FLOOR and e.clock == enacted_interaction["clock"]]:
            if e.color_index > 0:
                # If the floor is color then origin confirmation was enacted
                outcome = OUTCOME_ORIGIN
                self.workspace.memory.phenomenon_memory.phenomena[TER].last_origin_clock = enacted_interaction["clock"]
            else:
                if ABS in self.workspace.memory.phenomenon_memory.phenomena[TER].affordances:
                    relative_quaternion = quaternion.cross(self.workspace.memory.body_memory.body_quaternion(), quaternion.inverse(self.workspace.memory.phenomenon_memory.phenomena[TER].affordances[ABS].experience.body_direction_quaternion()))
                    if quaternion.rotation_angle(relative_quaternion) > math.pi:
                        relative_quaternion = -1 * relative_quaternion  # The quaternion representing the short angle
                    rot = quaternion.rotation_angle(relative_quaternion)
                    print("Rotation from origin", round(math.degrees(rot)))
                    if quaternion.rotation_axis(relative_quaternion)[2] > 0:  # Positive z axis rotation
                        if rot < math.pi/4:
                            print("OUTCOME Left of origin")
                            outcome = OUTCOME_LEFT
                        elif rot < math.pi:
                            print("OUTCOME Far Left of origin")
                            outcome = OUTCOME_FAR_LEFT
                        else:  # Not used
                            print("OUTCOME Far Right of origin")
                            outcome = OUTCOME_FAR_RIGHT
                    else:
                        if rot < math.pi/4:
                            print("OUTCOME Right of origin")
                            outcome = OUTCOME_RIGHT
                        elif rot < math.pi:
                            print("OUTCOME Far Right of origin")
                            outcome = OUTCOME_FAR_RIGHT
                        else:  # Not used
                            print("OUTCOME Far left of origin")
                            outcome = OUTCOME_FAR_LEFT
        return outcome

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Compute the next prompt point
        if self.exploration_step == EXPLORATION_STEP_INIT:
            # If time to go home
            if 0 in self.workspace.memory.phenomenon_memory.phenomena and \
                    ABS in self.workspace.memory.phenomenon_memory.phenomena[0].affordances \
                    and self.workspace.clock - self.workspace.memory.phenomenon_memory.phenomena[0].last_origin_clock > 3:
                # If right or left then swipe to home
                if outcome in [OUTCOME_LEFT, OUTCOME_RIGHT]:
                    if outcome == OUTCOME_RIGHT:
                        ego_confirmation = np.array([0, 500, 0], dtype=int)
                        self.exploration_step = EXPLORATION_STEP_SWIPE_LEFT
                    else:
                        ego_confirmation = np.array([0, -500, 0], dtype=int)
                        self.exploration_step = EXPLORATION_STEP_SWIPE_RIGHT
                    print("Swiping to confirmation by:", ego_confirmation)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
                    playsound('autocat/Assets/R5.wav', False)
                # If not left or write we need to manoeuvre
                else:
                    # If near home then go to confirmation prompt
                    if self.workspace.memory.is_near_terrain_origin():
                        allo_confirmation = self.workspace.memory.phenomenon_memory.phenomena[TER].confirmation_prompt()
                        print("Enacting confirmation affordance to", allo_confirmation)
                        ego_confirmation = self.workspace.memory.allocentric_to_egocentric(allo_confirmation)
                        self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
                        playsound('autocat/Assets/R5.wav', False)
                    else:
                        # If not near home then go home
                        allo_origin = self.workspace.memory.phenomenon_memory.phenomena[TER].origin_prompt()
                        print("Going from", self.workspace.memory.allocentric_memory.robot_point, "to origin sensor point", allo_origin)
                        ego_origin = self.workspace.memory.allocentric_to_egocentric(allo_origin)
                        self.workspace.memory.egocentric_memory.prompt_point = ego_origin
                        playsound('autocat/Assets/R3.wav', False)
                    self.exploration_step = EXPLORATION_STEP_ROTATE
            else:
                # Go to the most interesting pool point
                # mip = self.workspace.memory.allocentric_memory.most_interesting_pool(self.workspace.clock)
                # self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(mip)
                # Go back and forth
                self.workspace.memory.egocentric_memory.prompt_point = self.prompt_point.copy()
                self.exploration_step = EXPLORATION_STEP_ROTATE

        # Compute the next intended interaction
        if self.exploration_step == EXPLORATION_STEP_SWIPE_RIGHT:
            action = self.workspace.actions[ACTION_RIGHTWARD]
            self.exploration_step = EXPLORATION_STEP_INIT
        if self.exploration_step == EXPLORATION_STEP_SWIPE_LEFT:
            action = self.workspace.actions[ACTION_LEFTWARD]
            self.exploration_step = EXPLORATION_STEP_INIT
        if self.exploration_step == EXPLORATION_STEP_FORWARD:
            action = self.workspace.actions[ACTION_FORWARD]
            self.exploration_step = EXPLORATION_STEP_INIT
        if self.exploration_step == EXPLORATION_STEP_ROTATE:
            action = self.workspace.actions[ACTION_ALIGN_ROBOT]
            self.exploration_step = EXPLORATION_STEP_FORWARD
        ii = Interaction.create_or_retrieve(action, self.anticipated_outcome)

        return Enaction(ii, self.workspace.clock, self.workspace.memory.egocentric_memory.focus_point,
                        self.workspace.memory.egocentric_memory.prompt_point)
