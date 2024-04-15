import math
import matplotlib.path as mpath
import numpy as np
from pyrr import Quaternion
from scipy.spatial import ConvexHull, QhullError
from scipy.interpolate import splprep, splev
from . import PHENOMENON_INITIAL_CONFIDENCE, PHENOMENON_ENCLOSED_CONFIDENCE, PHENOMENON_RECOGNIZE_CONFIDENCE, \
    PHENOMENON_RECOGNIZED_CONFIDENCE

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon


class Phenomenon:
    """The parent class of all phenomena types"""
    def __init__(self, affordance):
        """A phenomenon is constructed from an initial affordance"""
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE
        self.phenomenon_type = None
        self.category = None
        # Initial shape is unknown
        self.origin_direction_quaternion = Quaternion([0., 0., 0., 1.])
        self.relative_origin_point = np.array([0, 0, 0])
        self.shape = np.empty([3, 3])  # Shape in terrain-centric coordinate used to display the phenomenon

        # Record the first affordance of the phenomenon
        # The phenomenon is placed in allocentric memory at the position of the initial affordance
        self.point = affordance.point.copy().astype(int)
        # The initial affordance is placed at the origin of the phenomenon
        affordance.point = np.array([0, 0, 0], dtype=int)
        self.affordances = {0: affordance}
        self.affordance_id = 0
        self.absolute_affordance_key = None

        self.nb_tour = 0
        self.tour_started = False
        # The hull is used to display the phenomenon's contour
        self.hull_points = None
        self.path = None  # Used to test is_inside in terrain-centric coordinates
        self.interpolation_types = None

        # Last time the origin affordance was enacted. Used to compute the return to origin.
        self.last_origin_clock = affordance.clock

        self.origin_prediction_error = {}  # (mm) The error along the floor color measure

    def absolute_affordance(self):
        """Return a reference to the absolute origin affordance or None"""
        if self.absolute_affordance_key is None:
            return None
        return self.affordances[self.absolute_affordance_key]

    def category_clue(self):
        """If RECOGNITION confidence then return the experience type else return None"""
        if self.confidence >= PHENOMENON_RECOGNIZE_CONFIDENCE:
            return self.phenomenon_type
        else:
            return None

    def try_to_enclose(self):
        """Try to bridge the circumference of the phenomenon"""
        # Only implemented for PhenomenonTerrain yet
        return

    def move_origin(self, offset):
        """Move the phenomenon's origin by the offset. Move the affordance by the opposite"""
        self.point += offset
        for a in self.affordances.values():
            a.point -= offset
        self.shape -= offset

    def recognize(self, category):
        """Update the category, confidence, shape, and path of this phenomenon"""
        # if self.category is None:
        self.category = category
        # The phenomenon's shape is copied from the category's shape
        self.shape = category.shape.copy()
        self.set_path()
        self.confidence = PHENOMENON_RECOGNIZED_CONFIDENCE
        print("Phenomenon recognized:", category.experience_type)
    #
    # def compute_center(self):
    #     """Recompute the center of the phenomenon as the mean of the affordance position"""
    #     points = np.array([a.point for a in self.affordances.values()])
    #     centroid = points.mean(axis=0)
    #     return centroid

    def convex_hull(self):
        """Return the points of the convex hull containing the phenomenon as a flat list"""

        self.hull_points = None
        # ConvexHull triggers errors if points are aligned
        try:
            points = np.array([a.point[0:2] for a in self.affordances.values()])
            hull = ConvexHull(points)
            hull_array = np.array([points[vertex] for vertex in hull.vertices])
            # self.delaunay = Delaunay(hull_array)
            self.hull_points = hull_array.flatten().astype("int").tolist()
        except QhullError:
            print("Error computing the convex hull: probably not enough points.")
        except IndexError as e:
            print("Error computing the convex hull: probably not enough points.", e)
        return self.hull_points

    def interpolate(self, s=5000):
        """Compute the interpolation points between the affordances"""
        # self.interpolation_points = None
        points = np.array([a.point[0:2] for a in self.affordances.values() if a.type in self.interpolation_types])
        points = np.unique(points, axis=0)
        if len(points) > 3:
            try:
                center = points.mean(axis=0)
                # Sort by angle from center of points
                angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
                # angles = np.arctan2(points[:, 1], points[:, 0])
                sorted_points = points[np.argsort(angles)]

                # Close the loop (not necessary)
                # sorted_points = np.append(sorted_points, [sorted_points[0]], axis=0)
                # print(repr(sorted_points))
                # Generate the B-spline representation
                tck_u = splprep(sorted_points.T, s=s, per=1)  # s=5000, per=True)  # s=0.2
                # tck_u = splprep(sorted_points.T, s=10*len(points), per=True)  # s=5000, per=True)  # s=0.2
                # Evaluate the B-spline on a finer grid
                finer_u = np.linspace(0, 1, 100)
                # Computes the interpolation points: Two dimensional [[x0,...,x100][y0,...,y100]]
                interpolated_points = np.array(splev(finer_u, tck_u[0]))
                # Convert into 3D points [[x0, y0, 0]...[x100, y100, 0]]
                self.shape = np.column_stack((interpolated_points[0], interpolated_points[1], np.zeros(100)))
                # Set the path
                self.set_path()
            except IndexError as e:
                print("Interpolation failed. No points.", e)
            except TypeError as e:
                print("Interpolation failed. Not enough points.", e)
            except ValueError as e:
                print("Interpolation failed.", e)
            except QhullError:
                print("The points do not form a valid convex polygon.")

    def outline(self):
        """Return the terrain outline 2D points as list of integers"""
        # Convert into flat list of 2D points [x0, y0, x1, y1, ...,x100, y100]
        if self.confidence < PHENOMENON_ENCLOSED_CONFIDENCE:
            return np.array([a.point[0:2] for a in self.affordances.values() if a.type in
                             self.interpolation_types]).flatten().astype("int").tolist()
        return self.shape[:, 0:2].flatten().astype("int").tolist()

    def set_path(self):
        """Set the path representing the terrain outline used to test is_inside"""
        # Must not be recomputed on each call to is_inside()
        # Need a closed two-dimensional array [[x0, y0],...,[x100, y100], [x0, y0]]
        self.path = mpath.Path(np.concatenate((self.shape[:, 0:2], self.shape[0:1, 0:2])))

    def is_inside(self, terrain_centric_point):
        """True if the point in terrain-centric coordinates is inside the phenomenon"""
        if terrain_centric_point is None or self.path is None:
            return False
        else:
            return self.path.contains_point(terrain_centric_point[0:2])

    def vector_toward_origin(self, affordance):
        """Return the vector computed from the affordance point minus the phenomenon point."""
        # By default the origin is at the center of the phenomenon
        return np.array(affordance.point - self.point, dtype=int)

    def latest_added_affordance(self):
        """Return the latest affordance added to this phenomenon"""
        return self.affordances[self.affordance_id]

    def enclose(self, origin_position_error, clock):
        """Adjust the position of affordances, interpolate the shape, move position to center"""
        # Propagate the origin position error to all the affordances since the last origin affordance
        for a in [a for a in self.affordances.values() if a.clock > self.last_origin_clock]:
            # The older the affordance, the smaller the position correction
            correction_coefficient = (a.clock - self.last_origin_clock) / (clock - self.last_origin_clock)
            ac = np.array(origin_position_error * correction_coefficient, dtype=int)
            a.point += ac
            # print("Affordance clock:", a.clock, "corrected by:", ac, "coef:", correction_coefficient)
        self.last_origin_clock = clock
        # Interpolate the affordance positions
        self.interpolate()
        # Place the origin of the terrain at the center
        self.move_origin(self.shape.mean(axis=0).astype(int))
        self.confidence = max(PHENOMENON_ENCLOSED_CONFIDENCE, self.confidence)

    def save(self, saved_phenomenon):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon.point = self.point.copy()
        saved_phenomenon.confidence = self.confidence
        saved_phenomenon.nb_tour = self.nb_tour
        saved_phenomenon.tour_started = self.tour_started
        saved_phenomenon.affordances = {key: a.save() for key, a in self.affordances.items()}
        saved_phenomenon.affordance_id = self.affordance_id
        saved_phenomenon.absolute_affordance_key = self.absolute_affordance_key
        saved_phenomenon.last_origin_clock = self.last_origin_clock
        saved_phenomenon.category = self.category
        saved_phenomenon.origin_direction_quaternion = self.origin_direction_quaternion.copy()
        saved_phenomenon.relative_origin_point = self.relative_origin_point.copy()
        saved_phenomenon.shape = self.shape.copy()
        saved_phenomenon.set_path()  # recompute the path from the shape. Perhaps we can just copy the path
        saved_phenomenon.origin_prediction_error = {k: v for k, v in self.origin_prediction_error.items()}
        return
