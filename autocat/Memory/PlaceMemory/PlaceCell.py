# A place cell is defined by a point and contains the cues to recognize it
import math
import numpy as np
from pyrr import Matrix44
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_LOCAL_ECHO
from ...Utils import cartesian_to_polar, assert_almost_equal_angles


class PlaceCell:
    def __init__(self, point, cues):
        """initialize the place cell from its point and its dictionary of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues  # Dictionary of cues

    def __str__(self):
        """Return the string of the tuple of the place cell coordinates"""
        return self.key.__str__()

    def __hash__(self):
        """Return the hash to use place cells as nodes in networkx"""
        return hash(self.key)

    def recognize_vector(self, cues):
        """Return the vector of the position defined by previous cues minus the position by the new cues"""
        vector = np.array([0, 0, 0])

        # Similarity based on echoes

        # Assume FLOOR experiences come from a single point
        for new_cue in [cue for cue in cues.values() if cue.type == EXPERIENCE_FLOOR]:
            for previous_cue in [cue for cue in self.cues.values() if cue.type == EXPERIENCE_FLOOR]:
                vector = previous_cue.point() - new_cue.point()
        return vector

    def polar_echo_curve(self):
        """Return the curve of echoes in polar coordinates"""
        curve = np.empty((360, 2), dtype=float)
        echo_cues = [cartesian_to_polar(cue.point()) for cue in self.cues.values() if cue.type
                     in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO]]
        for theta_deg in range(0, 360, 1):
            r, theta_rad = 0, math.radians(theta_deg)
            for r_cue, t_cue in echo_cues:
                if r_cue > r and assert_almost_equal_angles(t_cue, theta_rad, 35):
                    r = r_cue
            curve[theta_deg, :] = [r, theta_rad]
        return curve

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        return PlaceCell(self.point, {key: c.save() for key, c in self.cues.items()})
