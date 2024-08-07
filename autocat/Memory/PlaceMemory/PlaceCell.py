# A place cell is defined by a point and contains the cues to recognize it
import math
import numpy as np
import time
from pyrr import Quaternion, Matrix44
from . import ANGULAR_RESOLUTION, CONE_HALF_ANGLE, MIN_PLACE_CELL_DISTANCE
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_LOCAL_ECHO
from ...Utils import polar_to_cartesian, quaternion_to_direction_rad, translation_quaternion_to_matrix
from .PlaceGeometry import transform_estimation_cue_to_cue, point_to_polar_array, resample_by_diff, plot_correspondences
from .Cue import Cue


class PlaceCell:
    def __init__(self, point, cues):
        """initialize the place cell from its point and list of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues  # List of cues
        self.polar_echo_curve = np.linspace([0, 0], [0, 2 * math.pi], 360 // ANGULAR_RESOLUTION, dtype=float)
        self.cartesian_echo_curve = np.zeros((360 // ANGULAR_RESOLUTION, 3), dtype=float)

    def __str__(self):
        """Return the string of the tuple of the place cell coordinates"""
        return self.key.__str__()

    def __hash__(self):
        """Return the hash to use place cells as nodes in networkx"""
        return hash(self.key)

    def translation_estimation_echo(self, points, experience_type=EXPERIENCE_LOCAL_ECHO):
        """Return the vector of the position defined by previous cues minus the position by the new cues"""
        # Translation estimation based on echoes
        place_echo_points = np.array([c.point() for c in self.cues if c.type == experience_type])
        reg_p2p, residual_distance, points_transformed = transform_estimation_cue_to_cue(
            points, place_echo_points, MIN_PLACE_CELL_DISTANCE)

        # Move the robot in the same direction as moving the new local echoes to the place cell
        translation = np.array(reg_p2p.transformation[0:3, 3])
        rotation_deg = math.degrees(quaternion_to_direction_rad(Quaternion.from_matrix(reg_p2p.transformation[:3, :3])))
        print(f"Estimation echo rotation: {rotation_deg:.0f} degree")
        # Plot
        plot_correspondences(points, place_echo_points, points_transformed, reg_p2p, residual_distance, "-", self.key)
        # If rotation too high then cancel the position correction
        if abs(rotation_deg) > 10:
            translation[:] = 0

        return translation


        # # Assume FLOOR experiences come from a single point
        # for new_cue in [cue for cue in cues if cue.type == EXPERIENCE_FLOOR]:
        #     for previous_cue in [cue for cue in self.cues if cue.type == EXPERIENCE_FLOOR]:
        #         translation = previous_cue.point() - new_cue.point()
        return translation

    def compute_echo_curve(self):
        """Compute the curve of echoes in polar coordinates"""
        start_time = time.time()
        echo_cues = [cue for cue in self.cues if cue.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_LOCAL_ECHO]]
        if len(echo_cues) > 0:
            a = np.empty((360 // ANGULAR_RESOLUTION, len(echo_cues)), dtype=float)
            for i, c in enumerate(echo_cues):
                a[:, i] = point_to_polar_array(c.point())
            self.polar_echo_curve[:, 0] = a.max(axis=1)
            # print(f"Cue curve time: {time.time() - start_time:.3f}")

            # Recompute the central echoes
            self.cues = [c for c in self.cues if c.type != EXPERIENCE_CENTRAL_ECHO]
            diff_points = resample_by_diff(self.polar_echo_curve, math.radians(2 * CONE_HALF_ANGLE))
            for r, theta in diff_points:
                pose_matrix = translation_quaternion_to_matrix([r, 0, 0], Quaternion.from_z_rotation(theta))
                cue = Cue(0, pose_matrix, EXPERIENCE_CENTRAL_ECHO, 0, 0, [0, 0, 0])
                self.cues.append(cue)
            # Recompute the cartesian coordinates
            self.cartesian_echo_curve[:] = polar_to_cartesian(self.polar_echo_curve)

    def is_fully_observed(self):
        """Return True if the echo curve's radius is never zero"""
        return min(self.polar_echo_curve[:, 0]) > 0

    def translation_estimate_aligned_echo(self, point):
        """Return the translation to this place cell estimate by adjusting the point to the polar echo curve"""
        cue_direction_rad = math.atan2(point[1], point[0])
        cue_direction_deg = round(math.degrees(cue_direction_rad))
        r = self.polar_echo_curve[cue_direction_deg // ANGULAR_RESOLUTION, 0]
        distance = r - np.linalg.norm(point)
        translation = np.array([distance * math.cos(cue_direction_rad), distance * math.sin(cue_direction_rad), 0])
        print(f"Translation estimate from echo at ({r:.0f} mm, {cue_direction_deg}°): "
              f"{tuple(translation[:2].astype(int))}")
        return translation

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        saved_place_cell = PlaceCell(self.point, [cue.save() for cue in self.cues])
        saved_place_cell.polar_echo_curve[:] = self.polar_echo_curve
        saved_place_cell.cartesian_echo_curve[:] = self.cartesian_echo_curve
        return saved_place_cell
