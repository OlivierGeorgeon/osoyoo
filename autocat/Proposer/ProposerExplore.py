########################################################################################
# This decider makes the robot explore the parts of the terrain that are not yet known
# Activation 0: default. 3: the terrain has an absolute reference
########################################################################################

import math
import numpy as np
from pyrr import quaternion, Quaternion, Vector3
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SWIPE
from . Interaction import OUTCOME_NO_FOCUS
from . Proposer import Proposer
from ..Utils import short_angle
from ..Robot.Enaction import Enaction
from ..Robot.RobotDefine import TERRAIN_RADIUS
from ..Memory.BodyMemory import ENERGY_TIRED, EXCITATION_LOW
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE, TERRAIN_ORIGIN_CONFIDENCE
from ..Memory import EMOTION_RELAXED
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Integrator.OutcomeCode import FOCUS_TOO_FAR_DISTANCE
from . GoalGenerator import GoalGenerator


CLOCK_TO_GO_HOME = 8  # Number of interactions before going home
OUTCOME_ORIGIN = "O"
OUTCOME_LEFT = "LO"
OUTCOME_RIGHT = "RO"
OUTCOME_FAR_LEFT = "FL"
OUTCOME_FAR_RIGHT = "FR"
OUTCOME_COLOR = "CL"


class ProposerExplore(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        # The goal generator proposes successive goal points to explore the terrain
        self.goal_generator = GoalGenerator(workspace)

    def activation_level(self):
        """The level of activation is 3 if the terrain has confidence and the robot is excited or low energy"""

        if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and  \
            (self.workspace.memory.body_memory.energy < ENERGY_TIRED or
             self.workspace.memory.body_memory.excitation > EXCITATION_LOW):
            return 3

        # # High energy then must circle, explore, watch or arrange
        # if self.workspace.memory.body_memory.energy >= ENERGY_TIRED:
        #     # High excitation then must circle or explore
        #     if self.workspace.memory.body_memory.excitation > EXCITATION_LOW:
        #         # Focus inside terrain or not too far: HAPPY DeciderCircle
        #         if self.workspace.memory.egocentric_memory.focus_point is None or \
        #                 np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) > FOCUS_TOO_FAR_DISTANCE or \
        #                 self.workspace.memory.is_outside_terrain(self.workspace.memory.egocentric_memory.focus_point):
        #             return 3
        # # Tired: must go home
        # else:
        #     return 3

        return 0

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the explore behavior """
        outcome = OUTCOME_NO_FOCUS

        # On startup return DEFAULT
        if enaction is None or enaction.outcome is None:
            return outcome

        # If color outcome
        if enaction.outcome.color_index > 0:
            outcome = OUTCOME_COLOR
            print("Outcome color")

        # The floor outcome relative to the terrain origin
        if enaction.outcome.floor > 0 and enaction.outcome.color_index == 0 and \
                self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            angle = short_angle(self.workspace.memory.phenomenon_memory.phenomena[TER].origin_direction_quaternion,
                                self.workspace.memory.body_memory.body_quaternion)
            if angle < -math.pi/3:
                # print("OUTCOME Far Right of origin")
                outcome = OUTCOME_FAR_RIGHT
            elif angle < 0:
                # print("OUTCOME Right of origin")
                outcome = OUTCOME_RIGHT
            elif angle < math.pi/3:
                # print("OUTCOME Left of origin")
                outcome = OUTCOME_LEFT
            else:
                # print("OUTCOME Far Left of origin")
                outcome = OUTCOME_FAR_LEFT

        return outcome

    def select_enaction(self, enaction):
        """Propose the next enaction"""

        if self.workspace.memory.phenomenon_memory.terrain_confidence() == 0:
            return None

        outcome_code = self.outcome(enaction)

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_RELAXED
        e1, e2 = None, None

        # If time to go home
        if self.workspace.memory.body_memory.energy < ENERGY_TIRED:
            # If right or left then swipe to home
            if outcome_code in [OUTCOME_LEFT, OUTCOME_RIGHT]:
                if outcome_code == OUTCOME_RIGHT:
                    e_memory.egocentric_memory.prompt_point = np.array([0, 280, 0], dtype=int)  # Swipe to the right
                    e_memory.egocentric_memory.focus_point = np.array([280, 280, 0], dtype=int)
                else:
                    e_memory.egocentric_memory.prompt_point = np.array([0, -280, 0], dtype=int)
                    e_memory.egocentric_memory.focus_point = np.array([280, -280, 0], dtype=int)
                # print("Swiping to confirmation by:", ego_confirmation)
                e1 = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)
                # self.workspace.startup_sound.play()
            # If not left or right we need to manoeuvre
            else:
                # If near home then go to confirmation prompt
                if self.workspace.memory.is_near_terrain_origin() or outcome_code == OUTCOME_COLOR:
                    polar_confirmation = self.workspace.memory.phenomenon_memory.phenomena[TER].confirmation_prompt()
                    # print("Enacting confirmation sequence to", polar_confirmation)
                    ego_confirmation = self.workspace.memory.polar_egocentric_to_egocentric(polar_confirmation)
                    e_memory.egocentric_memory.prompt_point = ego_confirmation
                    # self.workspace.near_home_sound.play()
                else:
                    # If not near home then go to origin prompt
                    allo_origin = self.workspace.memory.phenomenon_memory.phenomena[TER].relative_origin_point + \
                                  self.workspace.memory.phenomenon_memory.phenomena[TER].point
                    # print("Going from", self.workspace.memory.allocentric_memory.robot_point, "to origin sensor point", allo_origin)
                    ego_origin = self.workspace.memory.allocentric_to_egocentric(allo_origin)
                    e_memory.egocentric_memory.prompt_point = ego_origin
                    # self.workspace.clear_sound.play()
                e_memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
                e1 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
                e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.predicted_memory.save())

        # If not time to go home, go to the most interesting pool point
        else:
            ego_prompt = self.workspace.memory.terrain_centric_to_egocentric(self.goal_generator.terrain_goal_point())

            e_memory.egocentric_memory.prompt_point = ego_prompt
            e_memory.egocentric_memory.focus_point = None  # Prevent unnatural head movement
            e1 = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
            e2 = Enaction(self.workspace.actions[ACTION_FORWARD], e1.predicted_memory.save())

        # Return the composite enaction
        enaction_sequence = [e1]
        if e2 is not None:
            enaction_sequence.append(e2)
        return CompositeEnaction(enaction_sequence)
