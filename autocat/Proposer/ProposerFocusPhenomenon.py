########################################################################################
# This proposer selects the behavior associated with the phenomenon that has the focus
########################################################################################

import numpy as np
from . Proposer import Proposer
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Enaction.CompositeEnaction import CompositeEnaction


class ProposerFocusPhenomenon(Proposer):

    def propose_enaction(self):
        """Propose an enaction based on the phenomenon that has the focus"""
        enaction = self.workspace.enaction
        if enaction is None:
            return None

        # If no focus phenomenon then no proposition
        p_id = self.workspace.memory.phenomenon_memory.focus_phenomenon_id
        if p_id is None:
            return None

        e_memory = self.workspace.memory.save()
        # If focus at a dot phenomenon
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type == EXPERIENCE_FLOOR:
            # Get the interaction and the updated e_memory
            interaction_code = p.propose_interaction_code(e_memory)
            # Return the proposed composite enaction
            if interaction_code in self.workspace.primitive_interactions:
                return CompositeEnaction(None, "Focus", np.array([0, 1, 0]),
                                         [self.workspace.primitive_interactions[interaction_code]], e_memory)
            elif interaction_code in self.workspace.sequence_interactions:
                return CompositeEnaction(None, "Focus", np.array([0, 1, 0]),
                                         self.workspace.sequence_interactions[interaction_code], e_memory)
