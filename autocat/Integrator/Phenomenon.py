import math
import numpy
from pyrr import matrix44
from scipy.spatial import ConvexHull, QhullError
from .Affordance import Affordance

PHENOMENON_DELTA = 300  # (mm) distance between experiences to be considered the same phenomenon


# https://stackoverflow.com/questions/61341712/calculate-projected-point-location-x-y-on-given-line-startx-y-endx-y
# def point_on_line(a, b, p):
#     ap = p - a
#     ab = b - a
#     result = a + numpy.dot(ap, ab) / numpy.dot(ab, ab) * ab
#     return result


class Phenomenon:
    """A hypothetical phenomenon"""
    def __init__(self, echo_experience, position_matrix):
        """Constructor
        Parameters:
            echo_experience: the first echo interaction of the object phenomenon
            position_matrix: the matrix to place the phenomenon in allocentric memory
            acceptable_delta: the acceptable delta between the allocentric coordinates of a new echo interaction
            and the center of the object phenomenon"""
        self.position_matrix = position_matrix

        # Record the first affordance of the phenomenon
        self.affordances = [Affordance(0, 0, echo_experience)]

        # The coordinates of this phenomenon in allocentric memory
        self.x, self.y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])

        self.has_been_validated = False
        # self.printed = False

    def add_affordance(self, x, y, experience):
        """Add an affordance made from this experience at this position"""
        self.affordances.append(Affordance(x, y, experience))

        # TODO: Adjust the center of the phenomenon when we can move it in phenomenon view
        self.compute_center()

    def compute_center(self):
        """Recompute the center of the phenomenon as the mean of the affordance position"""
        # https://stackoverflow.com/questions/4355894/how-to-get-center-of-set-of-points-using-python
        points = numpy.array([a.position_matrix[3, 0:2] for a in self.affordances])
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

    def try_and_add(self, experience, position_matrix, trust_robot_proportion):
        """Test if the experience is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position adjustment."""
        # TODO check the position relative to the border of the phenomenon rather than its center
        phenomenon_point = numpy.array([self.x, self.y])
        experience_point = numpy.array(matrix44.apply_to_vector(position_matrix, [0, 0, 0])[0:2])

        if math.dist(experience_point, phenomenon_point) < PHENOMENON_DELTA:
            delta = experience_point - phenomenon_point
            # The more we trust the robot's position the more we allocate the delta to the affordance's position
            delta_affordance = trust_robot_proportion * delta
            self.add_affordance(*delta_affordance, experience)
            # The more we trust the robot's position, the less we adjust the robot's position
            delta_robot = (1 - trust_robot_proportion) * delta
            return True, -delta_robot
        else:
            return False, None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.affordances) >= number_of_echos_needed:
            self.has_been_validated = True
        return self.has_been_validated

    def points(self):
        """Return the list of points to display in phenomenon view."""
        points = []
        for a in self.affordances:
            x, y, _ = matrix44.apply_to_vector(a.position_matrix, [0, 0, 0])
            points.append(int(x))
            points.append(int(y))
        return points

    def convex_hull(self):
        """Return the flat array of points of the convex hull containing the phenomenon"""
        hull_points = None
        # ConvexHull triggers errors of points are flat
        try:
            points = numpy.array([a.position_matrix[3, 0:2] for a in self.affordances])
            hull = ConvexHull(points)
            hull_points = numpy.array([points[vertex] for vertex in hull.vertices]).flatten().astype("int").tolist()
        except QhullError:
            print("Error computing the convex hull: probably not enough points.")
        return hull_points


    # def is_inside(self, x, y):
    #     """Return True if the point is inside the phenomenon"""
    # https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl
    # https://stackoverflow.com/questions/23937076/distance-to-convexhull
    #     p = numpy.array([x, y])
    #     is_inside = True
    #     if len(self.affordances) >= 2:
    #         for i in range(0, len(self.affordances)-1):
    #             # Lines must be clockwise
    #             p1 = numpy.array(matrix44.apply_to_vector(self.affordances[i].position_matrix, [0, 0, 0])[0:2])
    #             p2 = numpy.array(matrix44.apply_to_vector(self.affordances[i+1].position_matrix, [0, 0, 0])[0:2])
    #             # Negative distance is on the right of the line, meaning inside the phenomenon assuming it is convex
    #             distance = numpy.cross(p2-p1, p-p1)
    #             is_inside = is_inside and (distance < 0)
    #             projected = point_on_line(p1, p2, p)
    #
    #     print("Is inside: ", is_inside)
    #     return is_inside
