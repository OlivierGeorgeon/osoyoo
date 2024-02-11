import numpy as np
from . Action import ACTION_FORWARD, ACTION_SCAN
from . PredefinedInteractions import create_or_retrieve_primitive, create_primitive_interactions, \
    create_composite_interactions, create_or_reinforce_composite
from . Interaction import OUTCOME_NO_FOCUS, OUTCOME_FOCUS_TOO_FAR
from ..Integrator.OutcomeCode import outcome_code
from . Action import ACTION_TURN
from ..Robot.Enaction import Enaction
from ..Memory.Memory import EMOTION_HAPPY


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

    def activation_level(self):
        """Return the activation level of this decider/ 1: default; 3 if focus not too far and excited"""
        activation_level = 1  # Is the decider by default
        if self.workspace.memory.emotion_code == EMOTION_HAPPY:
            activation_level = 2
        return activation_level

    def stack_enaction(self):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent from the previous enaction
        # outcome = self.outcome(self.workspace.enaction)
        # outcome = outcome_code(self.workspace.memory, self.workspace.enaction)
        # print("OUTCOME", outcome)
        # Compute the next enaction or composite enaction
        # self.workspace.composite_enaction = self.select_enaction(outcome)
        self.workspace.composite_enaction = self.select_enaction(self.workspace.enaction.outcome_code)

    def propose_enaction(self):
        """Return a proposed interaction"""
        return self.select_enaction(self.workspace.enaction.outcome_code)

    def select_enaction(self, outcome):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            # Turn to the direction of the focus
            if outcome == OUTCOME_FOCUS_TOO_FAR or self.workspace.memory.egocentric_memory.focus_point is None:
                # If focus TOO FAR or None then turn around
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
            else:
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        return Enaction(self.action, self.workspace.memory)

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
            create_or_reinforce_composite(self.composite_interactions, self.previous_interaction, self.last_interaction)

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
