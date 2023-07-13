import math
import numpy as np
from . Action import ACTION_FORWARD, ACTION_SCAN
from . PredefinedInteractions import create_or_retrieve_primitive, create_primitive_interactions, \
    create_composite_interactions, create_or_reinforce_composite
from . Interaction import Interaction, OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE, \
    OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE,  OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR, OUTCOME_LIST

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
        self.primitive_interactions = create_primitive_interactions(self.workspace.actions)
        self.composite_interactions = create_composite_interactions(self.workspace.actions, self.primitive_interactions)

    def stack_enaction(self):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(self.workspace.enaction)
        # Compute the intended enaction
        self.select_enaction(outcome)

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the circle behavior """
        outcome = OUTCOME_NO_FOCUS

        # On startup return DEFAULT
        if enaction is None:
            return outcome

        # If there is a focus point, compute the echo outcome (focus may come from echo or from impact)
        if enaction.focus_point is not None:
            focus_radius = np.linalg.norm(enaction.focus_point)  # From the center of the robot
            if focus_radius < FOCUS_TOO_CLOSE_DISTANCE:
                outcome = OUTCOME_FOCUS_TOO_CLOSE
            elif focus_radius > FOCUS_TOO_FAR_DISTANCE:
                outcome = OUTCOME_FOCUS_TOO_FAR
            elif focus_radius > FOCUS_FAR_DISTANCE:
                outcome = OUTCOME_FOCUS_FAR
            else:
                focus_theta = math.atan2(enaction.focus_point[1], enaction.focus_point[0])
                if math.fabs(focus_theta) < FOCUS_SIDE_ANGLE:
                    outcome = OUTCOME_FOCUS_FRONT
                else:
                    outcome = OUTCOME_FOCUS_SIDE

        if enaction.lost_focus:
            outcome = OUTCOME_LOST_FOCUS

        # If floor then override the focus outcome
        if enaction.outcome.floor > 0:
            outcome = OUTCOME_FLOOR

        return outcome

    def select_action(self, outcome):
        """The sequence learning mechanism that proposes the next action"""
        # Recording previous interaction
        self.previous_interaction = self.last_interaction
        self.last_interaction = create_or_retrieve_primitive(self.primitive_interactions, self.action, outcome)

        # Tracing the last interaction
        if self.action is not None:
            print("Action: " + str(self.action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == outcome) +
                  ", valence: " + str(self.last_interaction.valence) + ")")

        # Learning or reinforcing the last composite interaction
        if self.previous_interaction is not None:
            composite_interaction = create_or_reinforce_composite(self.composite_interactions, self.previous_interaction,
                                                                             self.last_interaction)
            self.composite_interactions.append(composite_interaction)

        # Selecting the next action to enact
        # Initialize with the first action to select by default
        proclivity_dict = {self.workspace.actions[ACTION_SCAN]: 0}
        if self.composite_interactions:
            activated_interactions = [ci for ci in self.composite_interactions if ci.pre_interaction == self.last_interaction]
            for ai in activated_interactions:
                # print("activated interaction", ai)
                if ai.post_interaction.action in proclivity_dict:
                    proclivity_dict[ai.post_interaction.action] += ai.weight * ai.post_interaction.valence
                else:
                    proclivity_dict[ai.post_interaction.action] = ai.weight * ai.post_interaction.valence
        # for k, v in proclivity_dict.items():
        #     print(k.__str__(), "proclivity", v)

        # Select the action that has the highest proclivity value
        if proclivity_dict:
            # See https://pythonguides.com/python-find-max-value-in-a-dictionary/
            self.action = max(proclivity_dict, key=proclivity_dict.get)

