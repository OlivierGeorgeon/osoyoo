# A place cell is defined by a point and contains the cues to recognize it
import math
import numpy as np
import time
from pyrr import Matrix44
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_LOCAL_ECHO
from ...Utils import cartesian_to_polar, assert_almost_equal_angles

ANGULAR_RESOLUTION = 10  # Degree


class PlaceCell:
    def __init__(self, point, cues):
        """initialize the place cell from its point and list of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues  # List of cues

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
        for new_cue in [cue for cue in cues if cue.type == EXPERIENCE_FLOOR]:
            for previous_cue in [cue for cue in self.cues if cue.type == EXPERIENCE_FLOOR]:
                vector = previous_cue.point() - new_cue.point()
        return vector

    def polar_echo_curve(self):
        """Return the curve of echoes in polar coordinates"""
        start_time = time.time()
        # Takes almost 300ms to compute 360 points
        curve = np.empty((360 // ANGULAR_RESOLUTION, 2), dtype=float)
        echo_cues = [cartesian_to_polar(cue.point()) for cue in self.cues if cue.type
                     in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO]]
        for i in range(0, 360 // ANGULAR_RESOLUTION):
            r, theta = 0, math.radians(i * ANGULAR_RESOLUTION)
            for r_cue, t_cue in echo_cues:
                if r_cue > r and assert_almost_equal_angles(t_cue, theta, 35):
                    r = r_cue
            curve[i, :] = [r, theta]
        print(f"Cue curve time: {time.time() - start_time:.3f}")
        return curve

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        return PlaceCell(self.point, [cue.save() for cue in self.cues])
