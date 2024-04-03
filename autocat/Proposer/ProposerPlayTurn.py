########################################################################################
# This proposer makes the robot play by turning in place
# Activation: 5
# EMOTION_CONTENT (Serotonin)
########################################################################################

import math
import numpy as np
from pyrr import Quaternion, quaternion, Matrix44
from . Action import ACTION_TURN
from ..Robot.Enaction import Enaction
from ..Enaction.CompositeEnaction import CompositeEnaction
from . Proposer import Proposer
from ..Memory import EMOTION_CONTENT
from ..Memory.BodyMemory import EXCITATION_LOW
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_AZIMUTH, EXPERIENCE_COMPASS
from . Interaction import OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR
from ..Integrator.Calibrator import compass_calibration

STEP_INIT = 0
STEP_CALIBRATE = 1
NB_TURN = 4


class ProposerPlayTurn(Proposer):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.step = STEP_INIT
        self.rotate_quaternion = Quaternion.from_z_rotation(math.pi * 2 / NB_TURN)

    def activation_level(self):
        """The level of activation of this decider: 0: default, 5 if excited and object to play with """
        if self.workspace.memory.clock < 4:
            #  Turn around to calibrate the compass
            return 6
        # if self.workspace.memory.body_memory.excitation > EXCITATION_LOW and self.is_to_play():
        #     return 5
        return 0

    def select_enaction(self, enaction):
        """Add the next enaction to the stack based on sequence learning and spatial modifiers"""
        # Calibrate the compass
        if self.step == STEP_CALIBRATE:
            self.step = STEP_INIT
            self.workspace.calibrator.calibrate_compass()
            # points = np.array([e.point()[0: 2] for e in self.workspace.memory.egocentric_memory.experiences.values()
            #                    if e.clock >= enaction.clock - NB_TURN and e.type == EXPERIENCE_AZIMUTH])
            # offset_2d = compass_calibration(points)
            # print("Calibrate", offset_2d)
            # if offset_2d is not None:
            #     offset_point = np.array([offset_2d[0], offset_2d[1], 0], dtype=int)
            #     self.workspace.memory.body_memory.compass_offset += offset_point
            #     offset_matrix = Matrix44.from_translation(-offset_point).astype('float64')
            #     for e in self.workspace.memory.egocentric_memory.experiences.values():
            #         if e.type in [EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH]:
            #             e.displace(offset_matrix)

        # If there is an object to play with
        if self.is_to_play() and enaction.outcome_code not in [OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR]:
            # self.step = STEP_CALIBRATE  Needed if automatic calibration is off
            e_memory = self.workspace.memory.save()
            e_memory.emotion_code = EMOTION_CONTENT
            e_memory.egocentric_memory.prompt_point = np.array([100, 0, 0])
            enactions = []
            # create the sequence of turn
            for i in range(0, NB_TURN):
                e_memory.egocentric_memory.prompt_point = \
                    quaternion.apply_to_vector(self.rotate_quaternion, e_memory.egocentric_memory.prompt_point)
                e = Enaction(self.workspace.actions[ACTION_TURN], e_memory)
                e_memory = e.predicted_memory.save()
                enactions.append(e)
            return CompositeEnaction(enactions)
        # Otherwise don't propose an enaction (OUTCOME_FLOOR)
        else:
            return None

    def is_to_play(self):
        """Return True if the focus is not None and not too far"""
        if self.workspace.memory.egocentric_memory.focus_point is None:
            return False

        if np.linalg.norm(self.workspace.memory.egocentric_memory.focus_point) > 800:  # FOCUS_TOO_FAR_DISTANCE:
            return False
        return True
