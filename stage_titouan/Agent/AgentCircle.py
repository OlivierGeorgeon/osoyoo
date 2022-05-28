import math

from . Interaction import Interaction
from . CompositeInteraction import CompositeInteraction
from . PredefinedInteractions import *


class AgentCircle:
    def __init__(self):
        """ Creating our agent """
        self._action = 0
        self.anticipated_outcome = None
        self.previous_interaction = None
        self.last_interaction = None

        self.echo_xy = None
        self.focus = False

        # Load the predefined behavior
        self.memory: list[CompositeInteraction] = CompositeInteraction.composite_interaction_list

    def action(self, _outcome):
        """ learning from the previous outcome and selecting the next action """

        # Recording previous experience
        self.previous_interaction = self.last_interaction
        self.last_interaction = Interaction.create_or_retrieve(self._action, _outcome)

        # Tracing the last interaction
        if self._action is not None:
            print("Action: " + str(self._action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(_outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == _outcome) +
                  ", valence: " + str(self.last_interaction.valence) + ")")

        # Learning or reinforcing the last composite interaction
        if self.previous_interaction is not None:
            composite_interaction = CompositeInteraction.create_or_reinforce(self.previous_interaction,
                                                                             self.last_interaction)
            self.memory.append(composite_interaction)

        # Selecting the next action to enact
        self._action = ACTION_SCAN  # Good for circling around object behavior
        proclivity_dict = {}  # dict.fromkeys(ACTION_LIST, 0)
        # proclivity_dict = {ACTION_FORWARD: 0, ACTION_TURN_LEFT: 0, ACTION_TURN_RIGHT: 0} good for exploring terrain
        proclivity_dict = {ACTION_FORWARD: 0}  # Good for touring terrain
        if self.memory:
            activated_interactions = [ci for ci in self.memory if ci.pre_interaction == self.last_interaction]
            for ai in activated_interactions:
                if ai.post_interaction.action in proclivity_dict:
                    proclivity_dict[ai.post_interaction.action] += ai.weight * ai.post_interaction.valence
                else:
                    proclivity_dict[ai.post_interaction.action] = ai.weight * ai.post_interaction.valence

        print("Proclivity dictionary:", proclivity_dict)
        # Select the action that has the highest proclivity value
        if proclivity_dict:
            # See https://pythonguides.com/python-find-max-value-in-a-dictionary/
            self._action = max(proclivity_dict, key=proclivity_dict.get)

        """ Computing the anticipation """
        self.anticipated_outcome = None

        return self._action

    def result(self, enacted_interaction):
        """ Convert the enacted interaction into outcome adapted to the circle behavior """
        outcome = 'U'  # Outcome unknown

        # If there is an echo
        if 'echo_xy' in enacted_interaction:
            self.echo_xy = enacted_interaction['echo_xy']
            if self.echo_xy[0] < 10:
                outcome = OUTCOME_CLOSE_FRONT
            elif self.echo_xy[0] > 300:
                outcome = OUTCOME_FAR_FRONT
            elif self.echo_xy[1] > 150:
                outcome = OUTCOME_FAR_LEFT
            elif self.echo_xy[1] > 0:
                outcome = OUTCOME_LEFT
            elif self.echo_xy[1] > -150:
                outcome = OUTCOME_RIGHT
            else:
                outcome = OUTCOME_FAR_RIGHT

        # Check if the agent lost the focus
        if self.focus:
            if 'focus' not in enacted_interaction:
                # The focus was lost
                self.focus = False
                outcome = OUTCOME_LOST_FOCUS

        # Catch focus
        if self._action in [ACTION_SCAN, ACTION_FORWARD]:
            if outcome in [OUTCOME_LEFT, OUTCOME_FAR_LEFT, OUTCOME_RIGHT, OUTCOME_FAR_RIGHT]:
                # Found focus
                self.focus = True

        # If not focus then no circle behavior outcome
        if not self.focus and outcome != OUTCOME_LOST_FOCUS:
            outcome = OUTCOME_DEFAULT

        # Floor outcome
        if 'floor' in enacted_interaction:
            if enacted_interaction['floor'] == 0b10:
                outcome = OUTCOME_FLOOR_LEFT
            if enacted_interaction['floor'] == 0b11:
                outcome = OUTCOME_FLOOR_FRONT
            if enacted_interaction['floor'] == 0b01:
                outcome = OUTCOME_FLOOR_RIGHT

        return outcome

    def intended_interaction(self, _action):
        """ Construct the intended interaction from the circle behavior action """
        intended_interaction = {'action': _action, 'speed': 180}
        if self.focus:
            intended_interaction['focus_x'] = self.echo_xy[0]
            intended_interaction['focus_y'] = self.echo_xy[1]

        return intended_interaction


# Testing AgentCircle
# py -m stage_titouan.Agent.AgentCircle
if __name__ == "__main__":
    a = AgentCircle()
    _outcome = OUTCOME_LOST_FOCUS

    for i in range(20):
        _action = a.action(_outcome)
        print("Action: ", _action)
        _outcome = input("Enter outcome: ").upper()
        print(" Outcome: ", _outcome)
