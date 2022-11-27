import math
import numpy
from pyrr import matrix44
from scipy.spatial import ConvexHull, QhullError, Delaunay
from .Affordance import Affordance

PHENOMENON_DELTA = 300  # (mm) Distance between experiences to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0.2  # Initial confidence in the phenomenon


class Phenomenon:
    """A hypothetical phenomenon"""
    def __init__(self, affordance):
        """Constructor
        Parameters:
            echo_experience: the first echo interaction of the object phenomenon
            position_matrix: the matrix to place the phenomenon in allocentric memory
            and the center of the object phenomenon"""
        self.point = affordance.point  # The position of the phenomenon = position of the first affordance

        # Record the first affordance of the phenomenon
        affordance.point = numpy.array([0, 0, 0], dtype=numpy.int16)  # Position of the first affordance is reset
        self.affordances = [affordance]

        # The coordinates of this phenomenon in allocentric memory
        # self.x, self.y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

        self.hull_array = None

        self.confidence = PHENOMENON_INITIAL_CONFIDENCE
        # self.sum_rotation = 0.
        # self.initial_head_direction = head_direction
        # self.passed_reference_point = False
        self.has_been_validated = False

    # def add_affordance(self, x, y, experience):
    #     """Add an affordance made from this experience at this position"""
    #     self.affordances.append(Affordance(x, y, experience))
    #
    #     # TODO: Adjust the center of the phenomenon when we can move it in phenomenon view
    #     # self.compute_center()

    def compute_center(self):
        """Recompute the center of the phenomenon as the mean of the affordance position"""
        # https://stackoverflow.com/questions/4355894/how-to-get-center-of-set-of-points-using-python
        # points = numpy.array([a.position_matrix[3, 0:2] for a in self.affordances])
        points = numpy.array([a.point for a in self.affordances])
        centroid = points.mean(axis=0)
        # print("centroid", centroid)
        return centroid

        # sum_x = 0.
        # sum_y = 0.
        # i = 0.
        # # self.center = np.mean(self.allo_coordinates,axis=0)
        # for affordance in self.affordances:
        #     sum_x += affordance.position_matrix[3, 0]
        #     sum_y += affordance.position_matrix[3, 1]
        #     i += 1
        # # Move the phenomenon's position to the center of the affordances
        # self.position_matrix[3, 0] += int(sum_x/i)
        # self.position_matrix[3, 1] += int(sum_y/i)

        # Adjust the affordances' position
        # for affordance in self.affordances:
        #     affordance.position_matrix[3, 0] -= int(sum_x/i)
        #     affordance.position_matrix[3, 1] -= int(sum_y/i)

    # def try_and_add(self, experience, point):
    def try_and_add(self, affordance):
        """Test if the experience is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position adjustment."""
        # Convert coordinates to phenomenon-allocentric
        # affordance_point = numpy.array(matrix44.apply_to_vector(position_matrix, [0, 0, 0])) - self.point
        # affordance_point = numpy.subtract(point, self.point)
        # affordance_point = point - self.point
        affordance.point -= self.point

        # new_affordance = Affordance(affordance_point, experience)

        # The affordance nearest to the head
        head_point = numpy.array(matrix44.apply_to_vector(affordance.experience.sensor_matrix, [0, 0, 0]))
        phenomenon_points = numpy.array([a.point for a in self.affordances])
        dist2 = numpy.sum((phenomenon_points - head_point)**2, axis=1)
        nearest_affordance_point = phenomenon_points[dist2.argmin()]
        delta = nearest_affordance_point - affordance.point

        # If the new affordance is attributed to this phenomenon
        # if math.dist(affordance_point, nearest_affordance_point) < PHENOMENON_DELTA:
        if numpy.linalg.norm(delta) < PHENOMENON_DELTA:
            # If the affordance is near the origin affordance
            # if abs(head_direction - self.initial_head_direction) < math.radians(15):
            if affordance.similar_to(self.affordances[0]):
                # if math.dist(affordance_point, [0, 0, 0]) < PHENOMENON_DELTA:
                # print("Near origin: new direction: " + str(int(math.degrees(experience.absolute_direction_rad))) +
                #       "° initial: " +
                #       str(int(math.degrees(self.affordances[0].experience.absolute_direction_rad))) + "°")
                # self.add_affordance(new_affordance)
                self.affordances.append(affordance)
                position_correction = -affordance.point
                # return -affordance_point
            else:
                # if math.dist(affordance_point, nearest_affordance_point) < PHENOMENON_DELTA:
                # If low phenomenon confidence:
                # - the affordance is placed where it is measured: affordance_point
                # - The robot is not moved
                # - TODO: The phenomenon's position should be adjusted
                # If high phenomenon confidence :
                # - the affordance is placed at the previous point : nearest_point
                # - the robot is moved by the delta
                position_correction = numpy.array(self.confidence * delta, dtype=numpy.int16)
                affordance.point += position_correction
                # If the new affordance is inside then remove the nearest point. Should prevent from growing indefinitely
                # if self.is_inside(affordance_point):
                #     print("is inside. Delta: ", delta)
                if self.confidence > 0.5:
                    nb_affordance = len(self.affordances)
                    #     # self.affordances = [a for a in self.affordances if
                    #     #             numpy.linalg.norm(a.position_point - nearest_affordance_point) > numpy.linalg.norm(adjustment-2)]
                    self.affordances = [a for a in self.affordances if
                                        numpy.linalg.norm(a.point - head_point) > numpy.linalg.norm(affordance.point - head_point - 2)]
                    print("removed: ", nb_affordance - len(self.affordances), "affordances")

                # new_affordance = Affordance(affordance_point, experience)
                self.affordances.append(affordance)

            return position_correction
        else:
            return None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.affordances) >= number_of_echos_needed:
            self.has_been_validated = True
        return self.has_been_validated

    def convex_hull(self):
        """Return the points of the convex hull containing the phenomenon as a flat list"""
        hull_points = None
        # ConvexHull triggers errors if points are flat
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
