########################################################################################
# This proposer generates the construction of the place cell graph
########################################################################################
import math

import numpy as np
from . Proposer import Proposer
from ..Memory.PlaceMemory.PlaceGeometry import unscanned_direction, open_direction2
from ..Utils import assert_almost_equal_angles
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SCAN
from ..Enaction.CompositeEnaction import Enaction, CompositeEnaction
from .Interaction import OUTCOME_PROMPT


class ProposerPlaceCell(Proposer):

    def propose_enaction(self):
        """Propose enaction to generate the place cell graph"""

        e_memory = self.workspace.memory.save()

        # If no place cell then scan
        if self.workspace.memory.place_memory.current_cell_id == 0:
            i0 = self.workspace.primitive_interactions[(ACTION_SCAN, OUTCOME_PROMPT)]
            e0 = Enaction(i0, e_memory, span=10)
            return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))

        place_cell = self.workspace.memory.place_memory.current_place_cell()
        # If the current place cell is not fully observed
        if not place_cell.is_fully_observed():
            theta_unscanned, span_unscanned = unscanned_direction(place_cell.polar_echo_curve)
            print(f"Unscanned direction {math.degrees(theta_unscanned):.0f}, body direction {math.degrees(self.workspace.memory.body_memory.get_body_direction_rad()):.0f}")
            # If not scanned in front then scan
            if assert_almost_equal_angles(theta_unscanned, self.workspace.memory.body_memory.get_body_direction_rad(), 90) or span_unscanned > math.pi:
                i0 = self.workspace.primitive_interactions[(ACTION_SCAN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory, span=10)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
            # If not scanned not in front then turn to the unscanned angle
            else:
                ego_prompt = self.workspace.memory.polar_egocentric_to_egocentric(np.array([200 * np.cos(theta_unscanned), 200 * np.sin(theta_unscanned), 0]))
                e_memory.egocentric_memory.prompt_point = ego_prompt
                i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
        # If the current place cell is fully observed
        else:
            theta_open = open_direction2(place_cell.polar_echo_curve)
            print(f"Open direction {math.degrees(theta_open):.0f}, body direction {math.degrees(self.workspace.memory.body_memory.get_body_direction_rad()):.0f}")
            # If open in front then forward
            if assert_almost_equal_angles(theta_open, self.workspace.memory.body_memory.get_body_direction_rad(), 30):
                e_memory.egocentric_memory.prompt_point = None
                i0 = self.workspace.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
            # If not open in front then turn
            else:
                ego_prompt = self.workspace.memory.polar_egocentric_to_egocentric(np.array([200 * np.cos(theta_open), 200 * np.sin(theta_open), 0]))
                print(f"Turn to the open {round(math.degrees(math.atan2(ego_prompt[1], ego_prompt[0])))}")
                e_memory.egocentric_memory.prompt_point = ego_prompt
                i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
            # If position not adjusted then scan

            # If the previous place cell has higher confidence then return to it

            # If the previous place cell has lower or equal confidence then go explore
