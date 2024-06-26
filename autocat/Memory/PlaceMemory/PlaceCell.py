# A place cell is defined by a point and contains the cues to recognize it
import math
import numpy as np
import time
from pyrr import Matrix44
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_LOCAL_ECHO
from ...Utils import cartesian_to_polar, assert_almost_equal_angles, polar_to_cartesian
from .PlaceGeometry import transform_estimation_cue_to_cue

ANGULAR_RESOLUTION = 10  # Degree


class PlaceCell:
    def __init__(self, point, cues):
        """initialize the place cell from its point and list of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues  # List of cues
        self.polar_echo_curve = np.empty((360 // ANGULAR_RESOLUTION, 2), dtype=float)
        self.cartesian_echo_curve = np.empty((360 // ANGULAR_RESOLUTION, 3), dtype=float)

    def __str__(self):
        """Return the string of the tuple of the place cell coordinates"""
        return self.key.__str__()

    def __hash__(self):
        """Return the hash to use place cells as nodes in networkx"""
        return hash(self.key)

    def translation_estimation(self, cues):
        """Return the vector of the position defined by previous cues minus the position by the new cues"""
        translation = np.array([0, 0, 0])

        # Translation estimation based on echoes
        place_echo_cues = [c.point() for c in self.cues if c.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]]
        new_echo_cues = [c.point() for c in cues if c.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]]
        if len(place_echo_cues) > 0 and len(new_echo_cues) > 0:
            translation = -transform_estimation_cue_to_cue(place_echo_cues, new_echo_cues)[:3, 3]
            print("Echo translation", translation)

        # Assume FLOOR experiences come from a single point
        for new_cue in [cue for cue in cues if cue.type == EXPERIENCE_FLOOR]:
            for previous_cue in [cue for cue in self.cues if cue.type == EXPERIENCE_FLOOR]:
                translation = previous_cue.point() - new_cue.point()
        return translation

    def compute_echo_curve(self):
        """Compute the curve of echoes in polar coordinates"""
        start_time = time.time()
        # Takes almost 300ms to compute 360 points
        # curve = np.empty((360 // ANGULAR_RESOLUTION, 2), dtype=float)
        echo_cues = [cartesian_to_polar(cue.point()) for cue in self.cues if cue.type
                     in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO]]
        for i in range(0, 360 // ANGULAR_RESOLUTION):
            r, theta = 0, math.radians(i * ANGULAR_RESOLUTION)
            for r_cue, t_cue in echo_cues:
                if r_cue > r and assert_almost_equal_angles(t_cue, theta, 35):
                    r = r_cue
            self.polar_echo_curve[i, :] = [r, theta]
        print(f"Cue curve time: {time.time() - start_time:.3f}")
        self.cartesian_echo_curve[:] = polar_to_cartesian(self.polar_echo_curve)
        # return curve

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        saved_place_cell = PlaceCell(self.point, [cue.save() for cue in self.cues])
        saved_place_cell.polar_echo_curve[:] = self.polar_echo_curve
        saved_place_cell.cartesian_echo_curve[:] = self.cartesian_echo_curve
        return saved_place_cell
