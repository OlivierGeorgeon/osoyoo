########################################################################################
# This agent makes the robot circle around an echo object or a territory delimited by a line
########################################################################################

from . PredefinedInteractions import *


class AgentCircle:
    def __init__(self):
        """ Creating our agent """
        self._action = 0
        self.anticipated_outcome = None
        self.previous_interaction = None
        self.last_interaction = None

        self.focus_xy = None
        self.focus = False

        # Load the predefined behavior
        self.memory: list[CompositeInteraction] = CompositeInteraction.composite_interaction_list

    def propose_intended_interaction(self, enacted_interaction):
        """Propose the next intended interaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(enacted_interaction)
        # Compute the intended interaction possibly including the focus
        return self.intended_interaction(outcome)

    def intended_interaction(self, outcome):
        """ learning from the previous outcome and selecting the next action """

        # Recording previous experience
        self.previous_interaction = self.last_interaction
        self.last_interaction = Interaction.create_or_retrieve(self._action, outcome)

        # Tracing the last interaction
        if self._action is not None:
            print("Action: " + str(self._action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == outcome) +
                  ", valence: " + str(self.last_interaction.valence) + ")")

        # Learning or reinforcing the last composite interaction
        if self.previous_interaction is not None:
            composite_interaction = CompositeInteraction.create_or_reinforce(self.previous_interaction,
                                                                             self.last_interaction)
            self.memory.append(composite_interaction)

        # Selecting the next action to enact
        self._action = ACTION_SCAN  # Good for circling around object behavior
        # proclivity_dict = {}  # dict.fromkeys(ACTION_LIST, 0)
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

        intended_interaction = {'action': self._action}  # , 'speed': FORWARD_SPEED}
        if self.focus:
            intended_interaction['focus_x'] = self.focus_xy[0]
            intended_interaction['focus_y'] = self.focus_xy[1]

        return intended_interaction

    def outcome(self, enacted_interaction):
        """ Convert the enacted interaction into an outcome adapted to the circle behavior """
        outcome = OUTCOME_DEFAULT

        # If there is an echo, compute the echo outcome
        if 'echo_xy' in enacted_interaction:
            # The focus point is set to the aligned echo
            self.focus_xy = enacted_interaction['echo_xy']
            if self.focus_xy[0] < 50:
                outcome = OUTCOME_CLOSE_FRONT
            elif self.focus_xy[0] > 400:     # Must be farther than the forward speed m
                outcome = OUTCOME_FAR_FRONT
            elif self.focus_xy[1] > 150:
                outcome = OUTCOME_FAR_LEFT  # More that 150 to the left
            elif self.focus_xy[1] > 0:
                outcome = OUTCOME_LEFT      # between 0 and 150 to the left
            elif self.focus_xy[1] > -150:
                outcome = OUTCOME_RIGHT     # Between 0 and -150 to the right
            else:
                outcome = OUTCOME_FAR_RIGHT  # More that -150 to the right

        # Manage focus catch and lost
        if self.focus:
            # Check if the agent lost the focus
            if 'focus' not in enacted_interaction:
                # The focus was lost, override the echo outcome
                self.focus = False
                outcome = OUTCOME_LOST_FOCUS
                print("LOST FOCUS")
        else:
            if self._action in [ACTION_SCAN, ACTION_FORWARD]:
                # Catch focus
                if outcome in [OUTCOME_LEFT, OUTCOME_FAR_LEFT, OUTCOME_RIGHT, OUTCOME_FAR_RIGHT, OUTCOME_FAR_FRONT,
                               OUTCOME_CLOSE_FRONT]:
                    print("CATCH FOCUS")
                    self.focus = True

        # If not focus then no circle behavior outcome
        # if not self.focus and outcome != OUTCOME_LOST_FOCUS:
        #     outcome = OUTCOME_DEFAULT

        # If floor then override the echo and focus outcome
        if 'floor' in enacted_interaction:
            if enacted_interaction['floor'] == 0b10:
                outcome = OUTCOME_FLOOR_LEFT
            if enacted_interaction['floor'] == 0b11:
                outcome = OUTCOME_FLOOR_FRONT
            if enacted_interaction['floor'] == 0b01:
                outcome = OUTCOME_FLOOR_RIGHT

        return outcome


# Testing AgentCircle
# py -m stage_titouan.Agent.AgentCircle
if __name__ == "__main__":
    a = AgentCircle()
    _outcome = OUTCOME_LOST_FOCUS

    for i in range(20):
        _intended_interaction = a.intended_interaction(_outcome)
        print("Action: ", _intended_interaction)
        _outcome = input("Enter outcome: ").upper()
        print(" Outcome: ", _outcome)
