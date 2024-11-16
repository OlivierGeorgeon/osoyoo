########################################################################################
# This proposer generates the construction of the place cell graph
########################################################################################
import math

import numpy as np
from pyrr import Quaternion
from . Proposer import Proposer
from ..Memory.PlaceMemory.PlaceGeometry import unscanned_direction, open_direction
from ..Utils import assert_almost_equal_angles, short_angle
from . Action import ACTION_TURN, ACTION_FORWARD, ACTION_SCAN
from ..Enaction.CompositeEnaction import Enaction, CompositeEnaction
from .Interaction import OUTCOME_PROMPT, OUTCOME_FLOOR
from ..Memory.EgocentricMemory.EgocentricMemory import EXPERIENCE_LOCAL_ECHO


class ProposerPlaceCell(Proposer):

    def propose_enaction(self):
        """Propose enaction to generate the place cell graph"""

        e_memory = self.workspace.memory.save()

        # If outcome floor then turn around (for Bordeaux)
        if self.workspace.enaction is not None and self.workspace.enaction.outcome_code == OUTCOME_FLOOR:
            ego_prompt = np.array([-200, 0, 0])
            e_memory.egocentric_memory.prompt_point = ego_prompt
            i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
            e0 = Enaction(i0, e_memory)
            return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))

        # If no place or observe better cell then scan
        if self.workspace.memory.place_memory.current_cell_id == 0 or self.workspace.memory.place_memory.observe_better:
            e_memory.body_memory.neurotransmitters[:] = [50, 50, 60]  # Noradrenaline
            i0 = self.workspace.primitive_interactions[(ACTION_SCAN, OUTCOME_PROMPT)]
            e0 = Enaction(i0, e_memory, span=10)
            self.workspace.memory.place_memory.observe_better = False
            return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))

        place_cell = self.workspace.memory.place_memory.current_place_cell()
        # If the current place cell is not fully observed
        if not place_cell.is_fully_observed():
            e_memory.body_memory.neurotransmitters[:] = [50, 60, 50]  # Serotonin
            theta_unscanned, span_unscanned = unscanned_direction(place_cell.polar_echo_curve)
            print(f"Unscanned direction {math.degrees(theta_unscanned):.0f}, "
                  f"body direction {math.degrees(self.workspace.memory.body_memory.get_body_direction_rad()):.0f}")
            # If not scanned in front then scan
            if assert_almost_equal_angles(
                    theta_unscanned, self.workspace.memory.body_memory.get_body_direction_rad(), 90) \
                    or span_unscanned > math.pi:
                i0 = self.workspace.primitive_interactions[(ACTION_SCAN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory, span=10)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
            # If scanned in front then turn to the unscanned angle
            else:
                ego_prompt = self.workspace.memory.polar_egocentric_to_egocentric(
                    np.array([200 * np.cos(theta_unscanned), 200 * np.sin(theta_unscanned), 0]))
                e_memory.egocentric_memory.prompt_point = ego_prompt
                i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
        # If the current place cell is fully observed
        else:
            e_memory.body_memory.neurotransmitters[:] = [60, 50, 50]  # Dopamine
            theta_open, min_theta_open, max_theta_open = open_direction(place_cell.polar_echo_curve)
            short_to_theta_open = self.short_body_to_angle(theta_open)
            # theta_q = Quaternion.from_z_rotation(theta_open)
            # short_to_theta_open = short_angle(self.workspace.memory.body_memory.body_quaternion, theta_q)
            safe_span = theta_open - min_theta_open - 50/180 * math.pi  # Decrease the span of openness by 50°
            # safe_min_theta = min_theta_open + 50/180 * math.pi
            # safe_max_theta = max_theta_open - 50/180 * math.pi
            print(f"Open direction {math.degrees(theta_open):.0f}°, min {math.degrees(min_theta_open)}"
                  f", max {math.degrees(max_theta_open)}, safe span {math.degrees(safe_span):.0f}°, "
                  f"body direction {math.degrees(self.workspace.memory.body_memory.get_body_direction_rad()):.0f}")

            # If open in front then forward
            if self.open_in_front(theta_open, safe_span):
            # if abs(short_to_theta_open) < theta_open - safe_min_theta:
                e_memory.egocentric_memory.prompt_point = None
                i0 = self.workspace.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
                e0 = Enaction(i0, e_memory)
                return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
            # If not open in front then turn
            else:
                # If too close to the nearest echo then go to theta_open
                echoes = [p.point() for p in place_cell.cues if p.type == EXPERIENCE_LOCAL_ECHO]
                allo_nearest_echo = min(echoes, key=lambda x: np.linalg.norm(x)) + place_cell.point
                distance_to_nearest_echo = allo_nearest_echo - self.workspace.memory.allocentric_memory.robot_point
                if np.linalg.norm(distance_to_nearest_echo) < 200:
                    ego_prompt = np.array([200 * np.cos(short_to_theta_open), 200 * np.sin(short_to_theta_open), 0])
                    print(f"Turn to theta open {round(math.degrees(math.atan2(ego_prompt[1], ego_prompt[0])))}")
                    e_memory.egocentric_memory.prompt_point = ego_prompt
                    i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                    e0 = Enaction(i0, e_memory)
                    return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))
                else:
                    # very_safe_min_q = Quaternion.from_z_rotation(safe_min_theta + 15/180 * math.pi)
                    very_safe_min = min_theta_open + 65/180 * math.pi
                    # short_to_min = short_angle(self.workspace.memory.body_memory.body_quaternion, very_safe_min_q)
                    short_to_min = self.short_body_to_angle(very_safe_min)
                    very_safe_max = max_theta_open - 65/180 * math.pi
                    # short_to_max = short_angle(self.workspace.memory.body_memory.body_quaternion, very_safe_max_q)
                    short_to_max = self.short_body_to_angle(very_safe_max)
                    # Turn by the nearest limit angle
                    if abs(short_to_min) < abs(short_to_max):
                        ego_prompt = np.array([200 * np.cos(short_to_min), 200 * np.sin(short_to_min), 0])
                        print(f"Turn to short min {round(math.degrees(math.atan2(ego_prompt[1], ego_prompt[0])))}")
                    else:
                        ego_prompt = np.array([200 * np.cos(short_to_max), 200 * np.sin(short_to_max), 0])
                        print(f"Turn to short max {round(math.degrees(math.atan2(ego_prompt[1], ego_prompt[0])))}")
                    e_memory.egocentric_memory.prompt_point = ego_prompt
                    i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                    e0 = Enaction(i0, e_memory)
                    return CompositeEnaction([e0], 'place_cell', np.array([1, 1, 1]))

    def short_body_to_angle(self, polar_angle):
        """Return the short angle in radian for the robot to turn to a polar angle in radian"""
        theta_q = Quaternion.from_z_rotation(polar_angle)
        return short_angle(self.workspace.memory.body_memory.body_quaternion, theta_q)

    def open_in_front(self, theta_open, span_rad):
        """Return True if the the body is in the direction of theta_open modulo the span_rad"""
        theta_open_q = Quaternion.from_z_rotation(theta_open)
        return abs(short_angle(self.workspace.memory.body_memory.body_quaternion, theta_open_q)) < span_rad
