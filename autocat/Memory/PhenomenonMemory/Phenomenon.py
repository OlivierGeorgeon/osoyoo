import math
import numpy as np
from scipy.spatial import ConvexHull, QhullError, Delaunay
from scipy.interpolate import splprep, splev

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0  # 0.2 Initial confidence in the phenomenon
PHENOMENON_CONFIDENCE_PRUNE = 30  # Confidence threshold above which prune


class Phenomenon:
    """The parent class of all phenomena types"""
    def __init__(self, affordance):
        """Constructor
        Parameters:
            affordance: the first affordance that serves as the origin of the phenomenon
            """
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE

        # Record the first affordance of the phenomenon
        self.point = affordance.point.copy().astype(int)  # The position of the phenomenon relative to allocentric memo
        affordance.point = np.array([0, 0, 0], dtype=int)  # Position of the first affordance is reset
        self.affordances = {0: affordance}
        self.affordance_id = 0
        self.absolute_affordance_key = None

        self.nb_tour = 0
        self.tour_started = False
        # The hull is used to display the phenomenon's contour
        self.hull_points = None
        self.delaunay = None
        self.interpolation_types = None
        self.interpolation_points = None

        # Last time the origin affordance was enacted. Used to compute the return to origin.
        self.last_origin_clock = affordance.experience.clock

    def absolute_affordance(self):
        """Return a reference to the absolute origin affordance or None"""
        if self.absolute_affordance_key is None:
            return None
        return self.affordances[self.absolute_affordance_key]

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
            self.delaunay = Delaunay(hull_array)
            self.hull_points = hull_array.flatten().astype("int").tolist()
        except QhullError:
            print("Error computing the convex hull: probably not enough points.")
        except IndexError as e:
            print("Error computing the convex hull: probably not enough points.", e)
        return self.hull_points

    def interpolate(self):
        self.interpolation_points = None
        points = np.array(
            [a.point[0:2] for a in self.affordances.values() if a.experience.type in self.interpolation_types])
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
                tck, u = splprep(sorted_points.T, s=50000, per=True)  # s=0.2
                # Evaluate the B-spline on a finer grid
                u_new = np.linspace(0, 1, 100)
                interp = splev(u_new, tck)
                self.delaunay = Delaunay(np.array(interp).T)
                self.interpolation_points = np.array(interp).T.flatten().astype("int").tolist()
            except IndexError as e:
                print("Interpolation failed. No points.", e)
            except TypeError as e:
                print("Interpolation failed. Not enough points.", e)
            except ValueError as e:
                print("Interpolation failed.", e)
            except QhullError:
                print("The points do not form a valid convex polygon.")

    def is_inside(self, p):
        """True if p is inside the convex hull or there is no convex hull"""
        # https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl
        is_inside = False  # True for marking the outside cells in black (in AllocentricMemory.update_affordances)
        if self.delaunay is not None and p is not None:
            try:
                # Must reduce to 2 dimensions otherwise the point is not found inside
                is_inside = (self.delaunay.find_simplex((p - self.point)[0:2]) >= 0)
            except IndexError as e:
                print("Error testing inside:", e)
            except TypeError as e:
                print("Error testing inside:", e)
        else:
            print("Delaunay or p is None")
        return is_inside

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin direction: " + \
            str(round(math.degrees(self.affordances[0].experience.absolute_direction_rad))) + \
            "°. Nb tours:" + str(self.nb_tour)
        return label

    def save(self, saved_phenomenon, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon.point = self.point.copy()
        saved_phenomenon.confidence = self.confidence
        saved_phenomenon.nb_tour = self.nb_tour
        saved_phenomenon.tour_started = self.tour_started
        saved_phenomenon.affordances = {key: a.save(experiences) for key, a in self.affordances.items()}
        saved_phenomenon.affordance_id = self.affordance_id
        saved_phenomenon.absolute_affordance_key = self.absolute_affordance_key
        saved_phenomenon.last_origin_clock = self.last_origin_clock
        saved_phenomenon.delaunay = self.delaunay
        return
