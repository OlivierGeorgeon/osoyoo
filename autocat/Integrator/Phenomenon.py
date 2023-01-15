import numpy
from pyrr import matrix44
from scipy.spatial import ConvexHull, QhullError, Delaunay

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0.2  # 0.2 Initial confidence in the phenomenon
PHENOMENON_CONFIDENCE_PRUNE = 0.3  # Confidence threshold above which prune


class Phenomenon:
    """A hypothetical phenomenon"""
    def __init__(self, affordance):
        """Constructor
        Parameters:
            affordance: the first affordance that serves as the origin of the phenomenon
            """
        self.point = affordance.point.copy()  # The position of the phenomenon = position of the first affordance
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE
        print("Phenomenon:", affordance.experience.type, ", point:", self.point)

        # Record the first affordance of the phenomenon
        affordance.point = numpy.array([0, 0, 0], dtype=numpy.int16)  # Position of the first affordance is reset
        self.affordances = [affordance]
        self.origin_absolute_direction = affordance.experience.absolute_direction_rad
        self.origin_affordance = affordance  # In case affordances[0] is pruned

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

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position adjustment."""

        # The affordance is repositioned in reference to the phenomenon
        # (Do not modify the affordance if it does not belong to this phenomenon)
        relative_affordance_point = numpy.array(affordance.point - self.point, dtype=numpy.int16)

        # Find the reference affordance
        nearest_affordance = self.reference_affordance(affordance)
        reference_affordance_point = nearest_affordance.point
        # Reference point based on similarity of affordances TODO choose between nearest or similar
        similar_affordance_points = numpy.array([a.point for a in self.affordances if a.is_similar_to(affordance)])
        if similar_affordance_points.size > 0:
            print("Correct from similar affordances")
            reference_affordance_point = similar_affordance_points.mean(axis=0)

        # The delta of position from the reference affordance point
        delta = reference_affordance_point - relative_affordance_point

        # If the new affordance is attributed to this phenomenon
        if numpy.linalg.norm(delta) < PHENOMENON_DELTA:
            # If the affordance is similar to the origin affordance (near position and direction)
            if affordance.is_similar_to(self.origin_affordance):
                # The affordance in (0,0) and correct the robot's position
                position_correction = -relative_affordance_point
            else:
                position_correction = numpy.array(self.confidence * delta, dtype=numpy.int16)

            # Check if a new tour has started when reaching opposite direction
            if affordance.is_opposite_to(self.origin_affordance):
                self.tour_started = True
            # If a new tour has been completed then increase confidence
            if self.tour_started and affordance.is_clockwise_from(self.origin_affordance):
                self.tour_started = False
                self.nb_tour += 1
                self.confidence = min(self.confidence + 0.2, 1.)

            # Move the new affordance's position to relative reference
            affordance.point = relative_affordance_point + position_correction

            # Prune: remove the affordances that are nearer or equal to the sensor
            self.prune(affordance)
            # Append the new affordance
            self.affordances.append(affordance)

            # Return the correction to apply to the robot's position
            return position_correction
        else:
            # This affordance does not belong to this phenomenon
            return None

    def reference_affordance(self, affordance):
        """Find the previous affordance that serves as the reference to correct the position"""
        # TODO the reference algorithm must be improved
        # In this implementation the reference affordance is the affordance closest to the head
        phenomenon_points = numpy.array([a.point for a in self.affordances])
        head_point = numpy.array(matrix44.apply_to_vector(affordance.experience.sensor_matrix, [0, 0, 0]))
        dist2 = numpy.sum((phenomenon_points - head_point)**2, axis=1)
        return self.affordances[dist2.argmin()]

    def prune(self, affordance):
        """Remove previous affordances to keep their number under control"""
        # TODO The Prune algorithm must be improved
        if self.confidence > PHENOMENON_CONFIDENCE_PRUNE:
            nb_affordance = len(self.affordances)
            # self.affordances = [a for a in self.affordances if
            #                     numpy.linalg.norm(a.point - head_point) >
            #                     numpy.linalg.norm(affordance.point - head_point)]
            # self.affordances.remove(nearest_affordance)
            for a in self.affordances:
                # if numpy.linalg.norm(a.point - head_point) < numpy.linalg.norm(affordance.point - head_point):
                #     self.affordances.remove(a)
                #     break  # Remove only the first similar affordance found
                if a.is_similar_to(affordance):
                    self.affordances.remove(a)
                    break  # Remove only the first similar affordance found
            print("Prune:", nb_affordance - len(self.affordances), "affordances removed.")

    def convex_hull(self):
        """Return the points of the convex hull containing the phenomenon as a flat list"""
        hull_points = None
        # ConvexHull triggers errors if points are aligned
        try:
            points = numpy.array([a.point[0:2] for a in self.affordances])
            hull = ConvexHull(points)
            self.hull_array = numpy.array([points[vertex] for vertex in hull.vertices])
            hull_points = self.hull_array.flatten().astype("int").tolist()
        except QhullError:
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
