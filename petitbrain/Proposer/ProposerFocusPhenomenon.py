########################################################################################
# This proposer selects the behavior associated with the phenomenon that has the focus
########################################################################################

import numpy as np
from . Proposer import Proposer
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ..Enaction.CompositeEnaction import Enaction, CompositeEnaction


class ProposerFocusPhenomenon(Proposer):

    def propose_enaction(self):
        """Propose an enaction based on the phenomenon that has the focus"""
        enaction = self.workspace.enaction
        if enaction is None:
            return None

        # If no focus phenomenon then no proposition
        p_id = self.workspace.memory.phenomenon_memory.focus_phenomenon_id
        if p_id is None:
            print("No focus phenomenon id")
            return None

        e_memory = self.workspace.memory.save()
        # If focus at a dot phenomenon
        p = self.workspace.memory.phenomenon_memory.phenomena[p_id]
        if p.phenomenon_type in [EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO]:
            # Get the interaction and the updated e_memory
            interaction_code = p.propose_interaction_code(e_memory, enaction.outcome_code)
            # Return the proposed composite enaction
            if interaction_code in self.workspace.primitive_interactions:
                print("Prompt", e_memory.egocentric_memory.prompt_point)
                e = Enaction(self.workspace.primitive_interactions[interaction_code], e_memory)
                return CompositeEnaction([e], "Focus", np.array([0, 1, 0]))
                # return CompositeEnaction(None, "Focus", np.array([0, 1, 0]),
                #                          [self.workspace.primitive_interactions[interaction_code]], e_memory)
            elif interaction_code in self.workspace.sequence_interactions:
                return CompositeEnaction(None, "Focus", np.array([0, 1, 0]),
                                         self.workspace.sequence_interactions[interaction_code], e_memory)
            else:
                # Phenomenon proposes no interaction
                return None
