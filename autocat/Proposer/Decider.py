from ..Proposer.Proposer import Proposer
from ..Proposer.ProposerFocusPhenomenon import ProposerFocusPhenomenon
from ..Enaction import KEY_CONTROL_DECIDER


class Decider:

    def __init__(self, workspace):
        self.workspace = workspace

        self.proposers = {'Default': Proposer(self.workspace)
                          # , 'Play Turn': ProposerPlayTurn(self)
                          # , 'Explore': ProposerExplore(self)
                          # , 'Watch': ProposerWatch(self.workspace)
                          # , 'Watch C': ProposerWatchCenter(self),  'Arrange': ProposerArrange(self)
                          # , 'Push': ProposerPush(self.workspace)
                          # , 'Play': ProposerPlayForward(self)
                          # , "Play terrain": ProposerPlayTerrain(self)
                          , "Point": ProposerFocusPhenomenon(self.workspace)
                          }

    def main(self, dt):
        """The main loop of the decider"""
        if self.workspace.composite_enaction is None:
            if self.workspace.control_mode == KEY_CONTROL_DECIDER:
                # All deciders propose an enaction with an activation value
                self.workspace.composite_enaction = self.decide()
            else:
                self.workspace.decider_id = "Manual"

    def decide(self):
        """Return the selected composite enaction"""
        # Update the focus is the dot was lost
        # self.attention_mechanism.update_focus()

        # Each proposer adds a proposition to the list
        propositions = []
        for proposer in self.proposers.values():
            # activation = proposer.activation_level()  # Must compute before proposing
            enaction = proposer.propose_enaction()
            if enaction is not None:
                print("Proposition", enaction, "with focus", self.workspace.memory.egocentric_memory.focus_point)
                activation = enaction.emotion_mask * self.workspace.memory.body_memory.neurotransmitters
                propositions.append([enaction, activation.sum()])
        print("Proposed enactions:")
        for p in propositions:
            print(" ", p[0].decider_id, ":", p[0], p[1])
            # print(" ", p[0], ":", p[1], p[2])

        # Select the enaction that has the highest activation value
        most_activated_index = propositions.index(max(propositions, key=lambda p: p[1]))
        self.workspace.decider_id = propositions[most_activated_index][0].decider_id
        print("Decider:", self.workspace.decider_id)
        return propositions[most_activated_index][0]
