import math
import numpy as np
from ..Proposer.Interaction import OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FAR, \
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


def outcome_code(memory, trajectory, outcome):
    """ Return the outcome code from the trajectory and the outcome in memory"""
    code = OUTCOME_NO_FOCUS

    # On startup return NO_FOCUS
    if trajectory is None:
        return code

    # If there is a focus point, compute the focus outcome (focus may come from echo or from impact)
    if trajectory.focus_point is not None:
        focus_radius = np.linalg.norm(trajectory.focus_point)  # From the center of the robot
        # If focus is TOO FAR then DeciderCircle won't go after it
        if focus_radius > FOCUS_TOO_FAR_DISTANCE:  # self.too_far:  # Different for DeciderCircle or DeciderWatch
            code = OUTCOME_FOCUS_TOO_FAR
        # If the terrain is confident and the focus is outside then it is considered TOO FAR
        elif memory.is_outside_terrain(trajectory.focus_point):
            code = OUTCOME_FOCUS_TOO_FAR
        # Focus FAR: DeciderCircle will move closer
        elif focus_radius > FOCUS_FAR_DISTANCE:
            code = OUTCOME_FOCUS_FAR
        # Not TOO CLOSE and not TOO FAR: check if its on the SIDE
        elif focus_radius > FOCUS_TOO_CLOSE_DISTANCE:
            focus_theta = math.atan2(trajectory.focus_point[1], trajectory.focus_point[0])
            if math.fabs(focus_theta) < FOCUS_SIDE_ANGLE:
                code = OUTCOME_FOCUS_FRONT
            else:
                code = OUTCOME_FOCUS_SIDE
        # Focus TOO CLOSE: DeciderCircle and DeciderWatch will move backward
        else:
            code = OUTCOME_FOCUS_TOO_CLOSE

    # LOST FOCUS: DeciderCircle and DeciderArrange will scan again
    if trajectory.focus_confidence == CONFIDENCE_NO_FOCUS:
        code = OUTCOME_NO_FOCUS
    elif trajectory.focus_confidence <= CONFIDENCE_NEW_FOCUS:  # enaction.lost_focus:
        code = OUTCOME_LOST_FOCUS

    # If TOUCH then override the focus outcome
    if outcome.touch:
        code = OUTCOME_TOUCH

    # If FLOOR then override other outcome
    if outcome.floor > 0 or outcome.impact > 0:  # TODO Test impact
        code = OUTCOME_FLOOR

    return code
