import math
from pyrr import matrix44
from pyglet import shapes, gl
from webcolors import name_to_rgb
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO,  EXPERIENCE_PLACE, \
    EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT, EXPERIENCE_BLOCK, FLOOR_COLORS, EXPERIENCE_FOCUS, \
    EXPERIENCE_ROBOT, EXPERIENCE_TOUCH, EXPERIENCE_AZIMUTH, EXPERIENCE_COMPASS
from .EgocentricDisplay.OsoyooCar import EMOTION_COLORS


# Points of interest that only exist in Body Display
# (points of interest attached to an interaction have the same type as their interactions)
# POINT_COMPASS = 'Compass'
# POINT_AZIMUTH = 'Azimuth'
POINT_PROMPT = 'Prompt'
POINT_CONE = 'Cone'
POINT_ROBOT = 'PRobot'  # To draw the body of the other robot


class PointOfInterest:
    def __init__(self, pose_matrix, batch, group, point_type, clock, color_index=None, durability=10, size=0):
        self.pose_matrix = matrix44.create_identity()  # The shape will be displaced to the pose_matrix
        self.batch = batch
        self.group = group
        self.type = point_type
        self.points = []
        self.opacity = 255
        if color_index is None:
            self.color = name_to_rgb(FLOOR_COLORS[0])
        else:
            self.color = name_to_rgb(FLOOR_COLORS[color_index])
        self.is_selected = False
        self.clock = clock
        self.durability = durability

        if self.type == EXPERIENCE_PLACE:
            self.points = [30, 0, -20, -20, -20, 20]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c4B', 3 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_ALIGNED_ECHO:
            self.color = name_to_rgb("orange")
            self.points = [-20, 0, -11, 20, 1, 27, 1, -27, -11, -20]
            self.shape = self.batch.add_indexed(5, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3, 0, 3, 4],
                                                ('v2i', self.points), ('c4B', 5 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_LOCAL_ECHO:
            self.color = name_to_rgb("sienna")
            self.shape = shapes.Circle(0, 0, 7, color=self.color, batch=self.batch)

        if self.type == EXPERIENCE_CENTRAL_ECHO:
            self.color = name_to_rgb("sienna")
            self.points = [-20, 0, -11, 20, 1, 27, 1, -27, -11, -20]
            self.shape = self.batch.add_indexed(5, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3, 0, 3, 4],
                                                ('v2i', self.points), ('c4B', 5 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_FLOOR:
            if color_index == 0:
                self.color = name_to_rgb("black")
            self.points = [-5, -30, -5, 30, 5, 30, 5, -30]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_IMPACT:
            self.color = name_to_rgb("salmon")
            self.points = [-20, 0, 0, 20, 20, 0, 0, -20]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_BLOCK:
            self.color = name_to_rgb("salmon")
            self.points = [0, 0, 30, -30, 30, 30]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c4B', 3 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_TOUCH:
            self.color = name_to_rgb("IndianRed")
            self.points = [-20, 0, 0, 40, 20, 0, 0, -40]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_FOCUS:
            self.color = name_to_rgb("fireBrick")
            # self.points = [40, 0, 20, 34, -20, 34, -40, 0, -20, -34, 20, -34]
            self.points = [20, 0, 10, 17, -10, 17, -20, 0, -10, -17, 10, -17]
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                ('v2i', self.points), ('c4B', 6 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_COMPASS:
            self.color = name_to_rgb("RoyalBlue")
            self.points = [10, 0, 0, -15, 0, 15, -10, 0]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 1, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_AZIMUTH:
            self.color = name_to_rgb("SteelBlue")
            self.points = [20, 0, 0, -30, 0, 30, -20, 0]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 1, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == POINT_PROMPT:
            self.color = name_to_rgb("MediumOrchid")
            self.points = [40, 0, 20, 34, -20, 34, -40, 0, -20, -34, 20, -34]
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                ('v2i', self.points), ('c4B', 6 * (*self.color, self.opacity)))
        if self.type == POINT_ROBOT:  # The body of the other robot
            self.color = name_to_rgb("lightSteelBlue")
            self.points = [110, 0, 100, 80, -100, 80, -100, -80, 100, -80]
            self.shape = self.batch.add_indexed(5, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3, 0, 3, 4],
                                                ('v2i', self.points), ('c4B', 5 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_ROBOT:  # The emotion of the other robot
            self.color = name_to_rgb(EMOTION_COLORS[color_index])
            # self.shape = shapes.Circle(-30, 0, 10, color=self.color, batch=self.batch)
            self.points = [-40, -10, -20, -10, -20, 10, -40, 10]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == POINT_CONE:  # The cone of ECHO affordances
            self.color = name_to_rgb("CadetBlue")
            self.opacity = 64
            self.points = [round(-size), 0, 0, round(0.4 * size), 0, round(-0.4 * size)]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c4B', 3 * (*self.color, self.opacity)))
        # Move the point of interest to its position
        self.displace(pose_matrix)

    def set_color(self, color_name=None):
        """ Set the color or reset it to its default value. Also reset the opacity. """
        if color_name is None:
            if hasattr(self.shape, 'vertices'):
                nb_points = int(len(self.shape.vertices) / 2)
                self.shape.colors[0: nb_points*4] = nb_points * (*self.color, self.opacity)
            else:
                self.shape.opacity = self.opacity
                self.shape.color_index = self.color
        else:
            if hasattr(self.shape, 'vertices'):
                nb_points = int(len(self.shape.vertices) / 2)
                self.shape.colors[0: nb_points*4] = nb_points * (*name_to_rgb(color_name), self.opacity)
            else:
                self.shape.opacity = self.opacity
                self.shape.color_index = name_to_rgb(color_name)

    def displace(self, displacement_matrix):
        """ Applying the displacement matrix to the point of interest """

        # Update the position matrix
        self.pose_matrix = matrix44.multiply(self.pose_matrix, displacement_matrix)

        # If the shape has a list of vertices then apply the displacement matrix to each point.
        if hasattr(self.shape, 'vertices'):
            for i in range(0, len(self.shape.vertices)-1, 2):
                v = matrix44.apply_to_vector(displacement_matrix,
                                             [self.shape.vertices[i], self.shape.vertices[i + 1], 0])
                self.shape.vertices[i], self.shape.vertices[i+1] = int(v[0]), int(v[1])
        # Points of interest that use pyglet shapes have x and y (Circles)
        else:
            self.shape.x, self.shape.y, _ = matrix44.apply_to_vector(displacement_matrix,
                                                                     [self.shape.x, self.shape.y, 0])

    def delete(self):
        """ Delete the shape to remove it from the batch. Return True when deleted """
        self.shape.delete()
        return True

    def is_expired(self, clock):
        """Return True if the age has exceeded the durability"""
        return self.clock + self.durability < clock

    def select_if_near(self, point):
        """ If the point is near the x y coordinate, select this point and return True """
        if math.dist(point, self.point()) < 15:
            self.set_color('red')
            self.is_selected = True
            return True
        else:
            self.set_color()
            self.is_selected = False
            return False

    def fade(self, clock):
        """Decrease the opacity of this point of interest as it gets older, and then delete it"""
        # Opacity: 0 is transparent, 255 is opaque
        self.opacity = int(max(255 * (self.durability - clock + self.clock) / self.durability, 0))
        # Reset the opacity of the shape
        self.set_color(None)

    def point(self):
        """Return the point of reference of this point of interest. Used for compass calibration"""
        # Translate the origin point by the pose
        return matrix44.apply_to_vector(self.pose_matrix, [0, 0, 0])
