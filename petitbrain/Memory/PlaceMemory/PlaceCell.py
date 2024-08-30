# A place cell is defined by a point and contains the cues to recognize it
import math
import numpy as np
import time
import threading
from pyrr import Quaternion
from . import ANGULAR_RESOLUTION, CONE_HALF_ANGLE, MIN_PLACE_CELL_DISTANCE
from ..EgocentricMemory.EgocentricMemory import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO
from ...Utils import polar_to_cartesian, quaternion_to_direction_rad, translation_quaternion_to_matrix
from .PlaceGeometry import transform_estimation_cue_to_cue, point_to_polar_array, resample_by_diff, plot_compare
from .Cue import Cue


class PlaceCell:
    def __init__(self, place_cell_id, point, cues, confidence):
        """initialize the place cell from its point and list of cues"""
        self.key = place_cell_id
        self.point = point.copy()
        self.cues = cues  # List of cues
        self.polar_echo_curve = np.linspace([0, 0], [0, 2 * math.pi], 360 // ANGULAR_RESOLUTION, dtype=float)
        self.cartesian_echo_curve = np.zeros((360 // ANGULAR_RESOLUTION, 3), dtype=float)
        self.last_visited_clock = cues[0].clock
        self.last_position_clock = cues[0].clock
        self.position_confidence = confidence

    def __str__(self):
        """Return the string of the tuple of the place cell coordinates"""
        return tuple(self.point[0:2].astype(int)).__str__()

    def place_centric_to_allocentric(self, point):
        """Return the point in place-cell coordinates from the point in allocentric coordinates"""
        if point is not None:
            return point + self.point

    def translation_estimation_echo(self, points, robot_point):
        """Return the vector of the position defined by previous cues minus the position by the new cues"""
        # Translation estimation based on echoes
        place_echo_points = np.array([c.point() for c in self.cues if c.type == EXPERIENCE_LOCAL_ECHO])
        translation_init = robot_point - self.point
        reg_p2p = transform_estimation_cue_to_cue(points, place_echo_points, MIN_PLACE_CELL_DISTANCE, translation_init)

        # Move the robot in the same direction as moving the new local echoes to the place cell
        translation = np.array(reg_p2p.transformation[0:3, 3])
        rotation_deg = math.degrees(quaternion_to_direction_rad(Quaternion.from_matrix(reg_p2p.transformation[:3, :3])))
        # print(f"Estimation echo rotation: {rotation_deg:.0f}°")
        # Save the plot in an asynchronous thread
        thread = threading.Thread(target=plot_compare, args=(points, place_echo_points, reg_p2p, "Scan", self.key))
        thread.start()
        # plot_compare(points, place_echo_points, reg_p2p, "Scan", self.key)
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

    def translation_estimate_aligned_echo(self, allo_point):
        """Return the translation to this place cell estimate by adjusting the point to the polar echo curve"""
        # Propose a correction to match the point to the nearest central echo
        central_cues = [c for c in self.cues if c.type == EXPERIENCE_ALIGNED_ECHO]
        if len(central_cues) > 0:
            nearest_central_cue = min(central_cues, key=lambda c: np.linalg.norm(c.point() - allo_point))
            proposed_correction = nearest_central_cue.point() + self.point - allo_point
            print(f"Aligned echo: {tuple(allo_point[:2].astype(int))}, "
                  f"nearest place's aligned echo: {tuple(nearest_central_cue.point()[:2].astype(int))}")
            return proposed_correction
        else:
            return np.array([0, 0, 0])

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        saved_place_cell = PlaceCell(self.key, self.point, [cue.save() for cue in self.cues], 100)
        saved_place_cell.polar_echo_curve[:] = self.polar_echo_curve
        saved_place_cell.cartesian_echo_curve[:] = self.cartesian_echo_curve
        saved_place_cell.last_visited_clock = self.last_visited_clock
        saved_place_cell.last_position_clock = self.last_position_clock
        saved_place_cell.position_confidence = self.position_confidence
        return saved_place_cell
