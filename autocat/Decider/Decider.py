from . Interaction import OUTCOME_DEFAULT


class Decider:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT
        self.previous_interaction = None
        self.last_interaction = None

    def propose_intended_enaction(self):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(self.workspace.enaction)
        # Compute the intended enaction
        self.intended_enaction(outcome)
