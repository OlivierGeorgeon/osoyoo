import math
import matplotlib.path as mpath
import numpy as np
from pyrr import Quaternion, Vector3
from scipy.spatial import ConvexHull, QhullError
from scipy.interpolate import splprep, splev
from ...Robot.RobotDefine import LINE_X, ROBOT_COLOR_SENSOR_X
from . import TERRAIN_RECOGNIZE_CONFIDENCE

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0  # 0.2 Initial confidence in the phenomenon
PHENOMENON_CONFIDENCE_PRUNE = 30  # Confidence threshold above which prune


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
        self.shape = []  # Used to display the shape

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
        self.path = None  # Used to test is_inside
        self.interpolation_types = None
        # self.interpolation_points = None

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
        if self.confidence >= TERRAIN_RECOGNIZE_CONFIDENCE:
            return self.phenomenon_type
        else:
            return None

    def recognize(self, category):
        """Update the quaternion, origin, and shape of this phenomenon from the category"""
        if np.dot(self.absolute_affordance().polar_sensor_point, category.quaternion * Vector3([1., 0., 0.])) < 0:
            # Origin is North-East
            self.origin_direction_quaternion = category.quaternion.copy()
        else:
            # Origin is South-West
            self.origin_direction_quaternion = category.quaternion * Quaternion.from_z_rotation(math.pi)
        # The new relative origin is the position of green patch from the phenomenon center
        new_relative_origin = np.array(self.origin_direction_quaternion *
                                       Vector3([category.long_radius - LINE_X + ROBOT_COLOR_SENSOR_X, 0, 0]), dtype=int)
        self.shape = category.shape.copy()
        # The position of the phenomenon is adjusted by the difference in relative origin
        terrain_offset = new_relative_origin - self.relative_origin_point  # TODO check how it works with colors
        self.point -= terrain_offset
        for a in self.affordances.values():
            a.point += terrain_offset
        self.relative_origin_point = new_relative_origin

    def compute_center(self):
        """Recompute the center of the phenomenon as the mean of the affordance position"""
        points = np.array([a.point for a in self.affordances.values()])
        centroid = points.mean(axis=0)
        return centroid

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
        points = np.array(
            [a.point[0:2] for a in self.affordances.values() if a.type in self.interpolation_types])
        points = np.unique(points, axis=0)
        if len(points) > 3:
            try:
                # center = points.mean(axis=0)
                # angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
                # Sort by angle from center of terrain [0,0,0]
                angles = np.arctan2(points[:, 1], points[:, 0])
                sorted_points = points[np.argsort(angles)]

                # Close the loop
                sorted_points = np.append(sorted_points, [sorted_points[0]], axis=0)
                # print(repr(sorted_points))
                # Generate the B-spline representation
                tck_u = splprep(sorted_points.T, s=s, per=1)  # s=5000, per=True)  # s=0.2
                # tck_u = splprep(sorted_points.T, s=10*len(points), per=True)  # s=5000, per=True)  # s=0.2
                # Evaluate the B-spline on a finer grid
                finer_u = np.linspace(0, 1, 100)
                interpolated_points = np.array(splev(finer_u, tck_u[0]))  # Two dimensional [[x0,...,xn][y0,...,yn]]
                self.shape = np.column_stack((interpolated_points[0], interpolated_points[1], np.zeros(100)))
                # self.interpolation_points = interp.T.flatten().astype("int").tolist()
                self.path = mpath.Path(interpolated_points.T + self.point[0:2])  # Two dimensional [[x0, y0]...[xn, yn]]
            except IndexError as e:
                print("Interpolation failed. No points.", e)
            except TypeError as e:
                print("Interpolation failed. Not enough points.", e)
            except ValueError as e:
                print("Interpolation failed.", e)
            except QhullError:
                print("The points do not form a valid convex polygon.")

    def outline(self):
        """Return the terrain outline points"""
        return np.array([p[0:2] for p in self.shape]).flatten().astype("int").tolist()
        # return self.interpolation_points

    def is_inside(self, p):
        """True if p is inside the terrain"""
        if p is None or self.path is None:
            return False
        else:
            return self.path.contains_point(p[0:2])

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin direction: " + \
            str(round(math.degrees(self.affordances[0].experience.absolute_direction_rad))) + \
            "°. Nb tours:" + str(self.nb_tour)
        return label

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
        saved_phenomenon.path = self.path
        saved_phenomenon.category = self.category
        saved_phenomenon.origin_direction_quaternion = self.origin_direction_quaternion.copy()
        saved_phenomenon.relative_origin_point = self.relative_origin_point.copy()
        saved_phenomenon.shape = self.shape.copy()
        saved_phenomenon.origin_prediction_error = {k: v for k, v in self.origin_prediction_error.items()}
        return
