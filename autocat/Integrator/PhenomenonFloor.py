import numpy as np
from pyrr import matrix44
from .Phenomenon import Phenomenon, PHENOMENON_DELTA, PHENOMENON_CONFIDENCE_PRUNE


class PhenomenonFloor(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position adjustment."""

        position_correction = np.array([0, 0, 0], dtype=int)
        return position_correction

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon = PhenomenonFloor(self.origin_affordance)
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon

