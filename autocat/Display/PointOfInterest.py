import math
import numpy as np
from pyrr import matrix44
from pyglet import shapes, gl
from webcolors import name_to_rgb
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO,  EXPERIENCE_PLACE, \
    EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT, EXPERIENCE_BLOCK, FLOOR_COLORS, EXPERIENCE_FOCUS, \
    EXPERIENCE_ROBOT


# Points of interest that only exist in Body Display
# (points of interest attached to an interaction have the same type as their interactions)
POINT_COMPASS = 'Compass'
POINT_AZIMUTH = 'Azimuth'
POINT_PROMPT = 'Prompt'


class PointOfInterest:
    def __init__(self, x, y, batch, group, point_type, clock, color_index=None, durability=10):
        self.point = np.array([0, 0, 0], dtype=int)  # Will be moved to its position
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
            # self.points = [0, 0, 30, -30, 30, 30]
            self.points = [-20, 0, 0, 20, 20, 0, 0, -20]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3], ('v2i', self.points),
                                                ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_BLOCK:
            self.color = name_to_rgb("salmon")
            self.points = [0, 0, 30, -30, 30, 30]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c4B', 3 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_FOCUS:
            self.color = name_to_rgb("fireBrick")
            self.points = [40, 0, 20, 34, -20, 34, -40, 0, -20, -34, 20, -34]
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                ('v2i', self.points), ('c4B', 6 * (*self.color, self.opacity)))
        if self.type == POINT_COMPASS:
            self.color = name_to_rgb("RoyalBlue")
            self.points = [10, 0, 0, -10, 0, 10, -10, 0]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 1, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == POINT_AZIMUTH:
            self.color = name_to_rgb("SteelBlue")
            self.points = [20, 0, 0, -20, 0, 20, -20, 0]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 1, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))
        if self.type == POINT_PROMPT:
            self.color = name_to_rgb("MediumOrchid")
            self.points = [40, 0, 20, 34, -20, 34, -40, 0, -20, -34, 20, -34]
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                ('v2i', self.points), ('c4B', 6 * (*self.color, self.opacity)))
        if self.type == EXPERIENCE_ROBOT:
            self.color = name_to_rgb("darkslateBlue")
            self.points = [20, -16, 20, 16, -20, 16, -20, -16]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c4B', 4 * (*self.color, self.opacity)))

        # Move the point of interest to its position
        position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')
        self.displace(position_matrix)

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
        #  Rotate and translate the position
        self.point = matrix44.apply_to_vector(displacement_matrix, self.point)

        # If the shape has a list of vertices
        # then apply the displacement matrix to each point. This will rotate the shape
        if hasattr(self.shape, 'vertices'):
            for i in range(0, len(self.shape.vertices)-1, 2):
                v = matrix44.apply_to_vector(displacement_matrix, [self.shape.vertices[i], self.shape.vertices[i+1], 0])
                self.shape.vertices[i], self.shape.vertices[i+1] = int(v[0]), int(v[1])
            return

        # Points of interest that use pyglet shapes have x and y (Circles)
        self.shape.x, self.shape.y = self.point[0], self.point[1]

    def delete(self):
        """ Delete the shape to remove it from the batch. Return True when deleted """
        self.shape.delete()
        return True

    def is_expired(self, clock):
        """Return True if the age has exceeded the durability"""
        return self.clock + self.durability < clock

    def select_if_near(self, point):
        """ If the point is near the x y coordinate, select this point and return True """
        if math.dist(point, self.point) < 15:
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

    def __str__(self):
        return "POI of type " + self.type + " at x=" + str(int(self.point[0])) + ", y=" + str(int(self.point[1]))
