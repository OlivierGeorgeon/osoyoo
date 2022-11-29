import numpy
from pyrr import matrix44
from scipy.spatial import ConvexHull, QhullError, Delaunay

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0.2  # Initial confidence in the phenomenon


class Phenomenon:
    """A hypothetical phenomenon"""
    def __init__(self, affordance):
        """Constructor
        Parameters:
            affordance: the first affordance that serves as the origin of the phenomenon
            """
        self.point = affordance.point  # The position of the phenomenon = position of the first affordance
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE

        # Record the first affordance of the phenomenon
        affordance.point = numpy.array([0, 0, 0], dtype=numpy.int16)  # Position of the first affordance is reset
        self.affordances = [affordance]
        self.origin_absolute_direction = affordance.experience.absolute_direction_rad

        self.nb_tour = 0
        self.tour_started = False
        # The hull is used to display the phenomenon's contour
        self.hull_array = None

    def compute_center(self):
        """Recompute the center of the phenomenon as the mean of the affordance position"""
        # https://stackoverflow.com/questions/4355894/how-to-get-center-of-set-of-points-using-python
        # points = numpy.array([a.position_matrix[3, 0:2] for a in self.affordances])
        points = numpy.array([a.point for a in self.affordances])
        centroid = points.mean(axis=0)
        return centroid

    def try_and_add(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position adjustment."""

        # The affordance repositioned in reference to the phenomenon
        affordance.point -= self.point

        # Find the previous affordance nearest to the head
        head_point = numpy.array(matrix44.apply_to_vector(affordance.experience.sensor_matrix, [0, 0, 0]))
        phenomenon_points = numpy.array([a.point for a in self.affordances])
        dist2 = numpy.sum((phenomenon_points - head_point)**2, axis=1)
        nearest_affordance_point = phenomenon_points[dist2.argmin()]

        # The delta of position from the previous affordance nearest to the head
        delta = nearest_affordance_point - affordance.point

        # If the new affordance is attributed to this phenomenon
        if numpy.linalg.norm(delta) < PHENOMENON_DELTA:
            # If the affordance is similar to the origin affordance (near position and direction)
            if affordance.similar_to(self.affordances[0]):
                position_correction = -affordance.point

                if self.tour_started:
                    # If a new tour has been completed then increase confidence
                    self.tour_started = False
                    self.nb_tour += 1
                    self.confidence = min(self.confidence + 0.2, 1.)
            else:
                position_correction = numpy.array(self.confidence * delta, dtype=numpy.int16)
                affordance.point += position_correction

                # Check if a new tour
                if affordance.opposite_to(self.affordances[0]):
                    self.tour_started = True

            # Prune: remove the affordances that are nearer or equal from the head
            if self.confidence > 0.5:
                nb_affordance = len(self.affordances)
                self.affordances = [a for a in self.affordances if
                                    numpy.linalg.norm(a.point - head_point) >
                                    numpy.linalg.norm(affordance.point - head_point - 2)]
                print("Prune: ", nb_affordance - len(self.affordances), "affordances removed.")

            self.affordances.append(affordance)

            # Return the correction to apply to the robot's position
            return position_correction
        else:
            # This affordance does not belong to this phenomenon
            return None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.affordances) >= number_of_echos_needed:
            return True
        return False

    def convex_hull(self):
        """Return the points of the convex hull containing the phenomenon as a flat list"""
        hull_points = None
        # ConvexHull triggers errors if points are aligned
        try:
            points = numpy.array([a.point[0:2] for a in self.affordances])
            hull = ConvexHull(points)
            self.hull_array = numpy.array([points[vertex] for vertex in hull.vertices])
            hull_points = self.hull_array.flatten().astype("int").tolist()
        except QhullError as e:
            print("Error computing the convex hull: probably not enough points.")
        except IndexError as e:
            print("Error computing the convex hull: probably not enough points.", e)
        return hull_points

    def is_inside(self, p):
        """True if p is inside the convex hull"""
        # https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl
        is_inside = False
        try:
            # Must reduce to 2 dimensions otherwise the point is not found inside
            d = Delaunay(self.hull_array)  # The hull array is computed at the end of the previous cycle
            is_inside = (d.find_simplex(p[0:2]) >= 0)
        except IndexError as e:
            print("Error computing the Delaunay: ", e)
        return is_inside

    def increase_confidence(self, affordance):
        """Manage the increase of confidence in this phenomenon"""


