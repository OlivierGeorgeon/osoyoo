import math
import numpy as np
from pyrr import Quaternion
from . import PHENOMENON_INITIAL_CONFIDENCE, PHENOMENON_ENCLOSED_CONFIDENCE, PHENOMENON_RECOGNIZABLE_CONFIDENCE
from ...Utils import short_angle


class PhenomenonDot:
    """A point that affords the same type of affordance from any direction"""
    def __init__(self, affordance):
        """Initialize the phenomenon using the first affordance"""
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE
        self.phenomenon_type = affordance.type
        self.category = None  # Required because tested for push
        self.affordance_id = 0
        self.point = affordance.point.copy()
        affordance.point[:] = 0  # Reset in place
        self.affordances = {0: affordance}

    def update(self, affordance):
        """Add a new affordance to this phenomenon and move the phenomenon to the position of this affordance"""
        self.point[:] = affordance.point  # Copy in place
        affordance.point[:] = 0
        self.affordance_id += 1
        self.affordances[self.affordance_id] = affordance
        return 0

    def check(self):
        """If an affordances in every pi/2 then increase confidence to PHENOMENON_ENCLOSED_CONFIDENCE"""
        n = 4  # Number of quadrants
        affordances = {}
        for theta in np.linspace(0, 2 * math.pi, n):
            q = Quaternion.from_z_rotation(theta)
            for k, a in self.affordances.items():
                if abs(short_angle(Quaternion.from_z_rotation(math.atan2(a.point[1], a.point[0])), q)) < math.pi/n:
                    affordances[k] = a
                    # Keep only one affordance per quadrant
                    break
        if len(affordances) >= n:
            self.confidence = min(self.confidence, PHENOMENON_ENCLOSED_CONFIDENCE)
            self.affordances = affordances

    def category_clue(self):
        """If RECOGNIZABLE confidence then return the phenomenon type else return None"""
        if self.confidence >= PHENOMENON_RECOGNIZABLE_CONFIDENCE:
            return self.phenomenon_type
        else:
            return None

    def outline(self):
        return None

    def save(self):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonDot(self.affordances[min(self.affordances)].save())
        saved_phenomenon.confidence = self.confidence
        saved_phenomenon.phenomenon_type = self.phenomenon_type
        saved_phenomenon.point[:] = self.point
        saved_phenomenon.affordances = {key: a.save() for key, a in self.affordances.items()}
        saved_phenomenon.affordance_id = self.affordance_id
        return saved_phenomenon
