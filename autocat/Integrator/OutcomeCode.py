import math
import numpy as np
from ..Decider.Interaction import OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FAR, \
    OUTCOME_FOCUS_SIDE,  OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR, OUTCOME_TOUCH

FOCUS_TOO_CLOSE_DISTANCE = 200   # (mm) Distance below which OUTCOME_FOCUS_TOO_CLOSE. From robot center
FOCUS_FAR_DISTANCE = 400         # (mm) Distance beyond which OUTCOME_FOCUS_FAR. Must be farther than forward speed
FOCUS_TOO_FAR_DISTANCE = 600     # (mm) Distance beyond which OUTCOME_FOCUS_TOO_FAR (The robot will get closer
FOCUS_SIDE_ANGLE = 3.14159 / 6.  # (rad) Angle beyond which OUTCOME_SIDE
CONFIDENCE_NO_FOCUS = 0
CONFIDENCE_NEW_FOCUS = 1
CONFIDENCE_TOUCHED_FOCUS = 2
CONFIDENCE_CAREFUL_SCAN = 3
CONFIDENCE_CONFIRMED_FOCUS = 4


def outcome_code(memory, enaction):
    """ Return the outcome code from the enaction in memory"""
    outcome = OUTCOME_NO_FOCUS

    # On startup return NO_FOCUS
    if enaction is None:
        return outcome

    # If there is a focus point, compute the focus outcome (focus may come from echo or from impact)
    if enaction.trajectory.focus_point is not None:
        focus_radius = np.linalg.norm(enaction.trajectory.focus_point)  # From the center of the robot
        # If focus is TOO FAR then DeciderCircle won't go after it
        if focus_radius > FOCUS_TOO_FAR_DISTANCE:  # self.too_far:  # Different for DeciderCircle or DeciderWatch
            outcome = OUTCOME_FOCUS_TOO_FAR
        # If the terrain is confident and the focus is outside then it is considered TOO FAR
        elif memory.is_outside_terrain(enaction.trajectory.focus_point):
            outcome = OUTCOME_FOCUS_TOO_FAR
        # Focus FAR: DeciderCircle will move closer
        elif focus_radius > FOCUS_FAR_DISTANCE:
            outcome = OUTCOME_FOCUS_FAR
        # Not TOO CLOSE and not TOO FAR: check if its on the SIDE
        elif focus_radius > FOCUS_TOO_CLOSE_DISTANCE:
            focus_theta = math.atan2(enaction.trajectory.focus_point[1], enaction.trajectory.focus_point[0])
            if math.fabs(focus_theta) < FOCUS_SIDE_ANGLE:
                outcome = OUTCOME_FOCUS_FRONT
            else:
                outcome = OUTCOME_FOCUS_SIDE
        # Focus TOO CLOSE: DeciderCircle and DeciderWatch will move backward
        else:
            outcome = OUTCOME_FOCUS_TOO_CLOSE

    # LOST FOCUS: DeciderCircle and DeciderArrange will scan again
    if enaction.trajectory.focus_confidence <= CONFIDENCE_NEW_FOCUS:  # enaction.lost_focus:
        outcome = OUTCOME_LOST_FOCUS

    # If TOUCH then override the focus outcome
    if enaction.outcome.touch:
        outcome = OUTCOME_TOUCH

    # If FLOOR then override other outcome
    if enaction.outcome.floor > 0 or enaction.outcome.impact > 0:  # TODO Test impact
        outcome = OUTCOME_FLOOR

    print("OUTCOME", outcome)
    return outcome
