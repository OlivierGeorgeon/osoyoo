from . Proposer import Proposer


class ProposerManual(Proposer):

    def propose_enaction(self):
        """Propose the last enaction selected manually"""
        manual_interaction = self.workspace.manual_composite_interaction
        # Clear the manual interaction because it must be proposed only once
        self.workspace.manual_composite_interaction = None
        return manual_interaction
