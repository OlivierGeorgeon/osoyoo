import math
import numpy as np
from . Action import ACTION_FORWARD, ACTION_SCAN
from . Interaction import Interaction, OUTCOME_NO_FOCUS
from . CompositeInteraction import CompositeInteraction
from . PredefinedInteractions import create_interactions
from . PredefinedInteractions import OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE,  OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE, \
    OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR

FOCUS_TOO_CLOSE_DISTANCE = 200   # (mm) Distance below which OUTCOME_FOCUS_TOO_CLOSE. From robot center
FOCUS_FAR_DISTANCE = 400         # (mm) Distance beyond which OUTCOME_FOCUS_FAR. Must be farther than forward speed
FOCUS_TOO_FAR_DISTANCE = 600     # (mm) Distance beyond which OUTCOME_FOCUS_TOO_FAR
FOCUS_SIDE_ANGLE = 3.14159 / 6.  # (rad) Angle beyond which OUTCOME_SIDE


class Decider:
    def __init__(self, workspace):
        self.workspace = workspace
        self.action = self.workspace.actions[ACTION_FORWARD]
        self.anticipated_outcome = OUTCOME_NO_FOCUS
        self.previous_interaction = None
        self.last_interaction = None

        # Load the predefined behavior
        self.procedural_memory = create_interactions(self.workspace.actions)

    def stack_enaction(self):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(self.workspace.enaction)
        # Compute the intended enaction
        self.select_enaction(outcome)

    def outcome(self, enacted_enaction):
        """ Convert the enacted interaction into an outcome adapted to the circle behavior """
        outcome = OUTCOME_NO_FOCUS

        # On startup return DEFAULT
        if enacted_enaction is None:
            return outcome

        # If there is a focus point, compute the echo outcome (focus may come from echo or from impact)
        if enacted_enaction.focus_point is not None:
            focus_radius = np.linalg.norm(enacted_enaction.focus_point)  # From the center of the robot
            if focus_radius < FOCUS_TOO_CLOSE_DISTANCE:
                outcome = OUTCOME_FOCUS_TOO_CLOSE
            elif focus_radius > FOCUS_TOO_FAR_DISTANCE:
                outcome = OUTCOME_FOCUS_TOO_FAR
            elif focus_radius > FOCUS_FAR_DISTANCE:
                outcome = OUTCOME_FOCUS_FAR
            else:
                focus_theta = math.atan2(enacted_enaction.focus_point[1], enacted_enaction.focus_point[0])
                if math.fabs(focus_theta) < FOCUS_SIDE_ANGLE:
                    outcome = OUTCOME_FOCUS_FRONT
                else:
                    outcome = OUTCOME_FOCUS_SIDE

        if enacted_enaction.lost_focus:
            outcome = OUTCOME_LOST_FOCUS

        # If floor then override the focus outcome
        if enacted_enaction.outcome.floor > 0:
            outcome = OUTCOME_FLOOR

        return outcome

    def select_action(self, outcome):
        """The sequence learning mechanism that proposes the next action"""
        # Recording previous interaction
        self.previous_interaction = self.last_interaction
        self.last_interaction = Interaction.create_or_retrieve(self.action, outcome)

        # Tracing the last interaction
        if self.action is not None:
            print("Action: " + str(self.action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == outcome) +
                  ", valence: " + str(self.last_interaction.valence) + ")")

        # Learning or reinforcing the last composite interaction
        if self.previous_interaction is not None:
            composite_interaction = CompositeInteraction.create_or_reinforce(self.previous_interaction,
                                                                             self.last_interaction)
            self.procedural_memory.append(composite_interaction)

        # Selecting the next action to enact
        self.action = self.workspace.actions[ACTION_SCAN]  # Good for circling around object behavior
        # proclivity_dict = {}  # dict.fromkeys(ACTION_LIST, 0)
        # proclivity_dict = {ACTION_FORWARD: 0, ACTION_TURN_LEFT: 0, ACTION_TURN_RIGHT: 0} good for exploring terrain
        proclivity_dict = {self.workspace.actions[ACTION_FORWARD]: 0}  # Good for touring terrain
        if self.procedural_memory:
            activated_interactions = [ci for ci in self.procedural_memory if ci.pre_interaction == self.last_interaction]
            for ai in activated_interactions:
                if ai.post_interaction.action in proclivity_dict:
                    proclivity_dict[ai.post_interaction.action] += ai.weight * ai.post_interaction.valence
                else:
                    proclivity_dict[ai.post_interaction.action] = ai.weight * ai.post_interaction.valence
        # print("Proclivity dictionary:", proclivity_dict)

        # Select the action that has the highest proclivity value
        if proclivity_dict:
            # See https://pythonguides.com/python-find-max-value-in-a-dictionary/
            self.action = max(proclivity_dict, key=proclivity_dict.get)
