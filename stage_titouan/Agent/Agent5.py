from . Interaction import Interaction
from . CompositeInteraction import CompositeInteraction
# from EgoMemoryWindow import EgoMemoryWindow
# from OsoyooCar import OsoyooCar
import pyglet


class Agent5:
    def __init__(self, valences=[[4, -2, -2, -2], [-1, -1, -1, -1], [-2, -2, -2, -2]]):
        """ Creating our agent """
        # These values give a nice demo with osoyoo car
        self.valences = valences
        self._action = 0
        self.anticipated_outcome = None

        self.memory: list[CompositeInteraction] = []
        self.previous_interaction = None
        self.last_interaction = None

    def action(self, _outcome):
        """ tracing the previous cycle """
        if self._action is not None:
            print("Action: " + str(self._action) +
                  ", Anticipation: " + str(self.anticipated_outcome) +
                  ", Outcome: " + str(_outcome) +
                  ", Satisfaction: (anticipation: " + str(self.anticipated_outcome == _outcome) +
                  ", valence: " + str(self.valences[self._action][_outcome]) + ")")

        """ Recording previous experience """
        self.previous_interaction = self.last_interaction
        valence = self.valences[self._action][_outcome]  # stock la satisfaction obtenue à la dernière interaction
        self.last_interaction = Interaction.create_or_retrieve(self._action, _outcome, valence)
        # print("Enacted interaction ", end="")
        # print(self.last_interaction)
        if self.previous_interaction is not None:
            composite_interaction = CompositeInteraction.create_or_retrieve(self.previous_interaction,
                                                                            self.last_interaction)
            if composite_interaction not in self.memory:
                self.memory.append(composite_interaction)
                print("Learning " + composite_interaction.__str__())
            else:
                i = self.memory.index(composite_interaction)
                self.memory[i].increment_weight()
                print("Reinforcing " + self.memory[i].__str__())

        """ Selecting the next action to enact """
        self._action = 0
        self.anticipated_outcome = None
        proclivity_list = [0, 0, 0]
        # print(self.memory)
        if self.memory:
            activated_interactions = [ci for ci in self.memory if ci.pre_interaction == self.last_interaction]
            for ai in activated_interactions:
                proclivity_list[ai.post_interaction.action] += ai.weight * ai.post_interaction.valence

        print("Proclivity list: ", end="")
        print(proclivity_list)
        max_proclivity = max(proclivity_list)
        self._action = proclivity_list.index(max_proclivity)

        """ Computing the anticipation """  # TODO:improve this
        if Interaction.interaction_list:
            for ai in Interaction.interaction_list:
                if ai.action == self._action:
                    if max_proclivity > 0 and ai.valence > 0:
                        self.anticipated_outcome = ai.outcome
                    if max_proclivity < 0 and ai.valence < 0:
                        self.anticipated_outcome = ai.outcome

        return self._action

    def result(self, enacted_interaction):
        _outcome = 0
        if 'floor' in enacted_interaction:
            _outcome = int(enacted_interaction['floor'])
        if 'shock' in enacted_interaction:
            if enacted_interaction['shock'] > 0:
                _outcome = enacted_interaction['shock']
        return _outcome

    def intended_interaction(self, _action):
        return {'action': ['8', '1', '3'][_action]}


# Testing Agent5 by updating the window and expecting outcome from user keypress
# py -m stage_titouan.Agent.Agent5
if __name__ == "__main__":
    agent = Agent5()
    outcome = 0

    for i in range(20):
        action = agent.action(outcome)
        outcome = 0
