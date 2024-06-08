# A place cell is defined by a point and contains the affordances experienced from this place
# A place cell can be recognized from its cues

import numpy as np
from pyrr import Matrix44
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_FLOOR


class PlaceCell:
    def __init__(self, point, cues):
        """initialize the place cell from the point and a list of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues  # Dictionary of cues

    def __str__(self):
        return self.key.__str__()

    def add_cues(self, cues):
        """Compute a position correction, add the cues, and return the position correction"""
        position_correction = np.array([0, 0, 0])
        # Assume FLOOR experiences come from a single point
        for new_cue in [cue for cue in cues.values() if cue.type == EXPERIENCE_FLOOR]:
            for old_cue in [cue for cue in self.cues.values() if cue.type == EXPERIENCE_FLOOR]:
                position_correction = -new_cue.point() + old_cue.point()
        position_correction_matrix = Matrix44.from_translation(position_correction)
        # shift the new cues
        for cue in cues.values():
            cue.pose_matrix *= position_correction_matrix
        self.cues.update(cues)
        return position_correction

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        return PlaceCell(self.point, {key: c.save() for key, c in self.cues.items()})
