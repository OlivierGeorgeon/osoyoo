from pyglet import shapes, gl
import math
from pyrr import matrix44, Quaternion
from webcolors import name_to_rgb
from ... Memory.EgocentricMemory.Interactions.Interaction import *

POINT_ECHO = INTERACTION_ECHO  # 1
POINT_TINY_ECHO = 1  # INTERACTION_ECHO
POINT_TRESPASS = INTERACTION_TRESPASSING
POINT_SHOCK = INTERACTION_SHOCK
POINT_BLOCK = INTERACTION_BLOCK
POINT_PLACE = 4
POINT_PHENOMENON = 5
POINT_COMPASS = 6


class PointOfInterest:
    def __init__(self, x, y, batch, group, point_type, interaction=None):
        self.interaction = interaction
        self.x, self.y = 0, 0  # will be displaced
        self.batch = batch
        self.group = group
        self.type = point_type

        self.is_selected = False

        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')
        self.points = []

        if self.type == POINT_PLACE:
            # Place: LightGreen triangle
            self.points = [20, 0, -20, -20, -20, 20]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c3B', 3 * name_to_rgb("LightGreen")))
        if self.type == POINT_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(0, 0, 20, color=name_to_rgb("orange"), batch=self.batch)
            self.shape.group = group
        if self.type == POINT_TINY_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(0, 0, 7, color=name_to_rgb("orange"), batch=self.batch)
        if self.type == POINT_TRESPASS:
            # Trespassing: black dash
            self.points = [-5, -30, -5, 30, 5, 30, 5, -30]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 0, 2, 3],
                                                ('v2i', self.points), ('c3B', 4 * name_to_rgb("black")))
        if self.type == POINT_SHOCK:
            # Chock interaction: red triangle
            self.points = [0, 0, 40, -30, 40, 30]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c3B', 3 * name_to_rgb("red")))
        if self.type == POINT_BLOCK:
            # Pushing: salmon triangle
            self.points = [0, 0, 40, -30, 40, 30]
            self.shape = self.batch.add_indexed(3, gl.GL_TRIANGLES, self.group, [0, 1, 2], ('v2i', self.points),
                                                ('c3B', 3 * name_to_rgb("salmon")))
        if self.type == POINT_PHENOMENON:
            # Phenomenon: tomato
            self.points = [40, 0, 20, 34, -20, 34, -40, 0, -20, -34, 20, -34]
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                ('v2i', self.points), ('c4B', 6 * (*name_to_rgb("fireBrick"), 128)))
        if self.type == POINT_COMPASS:
            # Compass: RoyalBlue square
            self.points = [10, 0, 0, -10, 0, 10, -10, 0]
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0, 1, 2, 1, 2, 3],
                                                ('v2i', self.points), ('c3B', 4 * name_to_rgb("RoyalBlue")))

        # Move the point of interest to its position
        self.displace(self.position_matrix)

    def set_color(self, color_name=None):
        """ Set the color or reset it to its default value """
        if color_name is None:
            if self.type == POINT_PLACE:
                # Place: Blue circle
                # self.shape.colors[0:9] = [144, 238, 144, 144, 238, 144, 144, 238, 144]
                self.shape.colors[0:9] = 3 * name_to_rgb("LightGreen")
            if self.type == POINT_ECHO:
                # Echo: Orange circle
                self.shape.color = name_to_rgb("orange")
            if self.type == POINT_TINY_ECHO:
                # Echo: Orange circle
                self.shape.color = name_to_rgb("orange")
            if self.type == POINT_TRESPASS:
                # Trespassing: black dash
                self.shape.color = name_to_rgb("black")
            if self.type == POINT_SHOCK:
                # Chock interaction: red triangle
                self.shape.color = name_to_rgb("red")
            if self.type == POINT_BLOCK:
                # Pushing: yellow triangle
                self.shape.color = name_to_rgb("yellow")
            if self.type == POINT_PHENOMENON:
                self.shape.colors[0:24] = 6 * (*name_to_rgb("fireBrick"), 128)
        else:
            if self.type == POINT_PLACE:
                self.shape.colors[0:9] = 3 * name_to_rgb(color_name)
            elif self.type == POINT_PHENOMENON:
                self.shape.colors[0:24] = 6 * (*name_to_rgb(color_name), 200)
            else:
                self.shape.color = name_to_rgb(color_name)

    def reset_position(self):
        """ Reset the position of the point of interest """
        self.x, self.y = 0, 0
        # If the shape has a list of vertices then reset it
        if hasattr(self.shape, 'vertices'):
            self.shape.vertices = self.points
        else:
            self.shape.x, self.shape.y = 0, 0  # Circle

    def displace(self, displacement_matrix):
        """ Applying the displacement matrix to the phenomenon """
        #  Rotate and translate the position
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        self.x, self.y = v[0], v[1]

        # If compass don't displace
        # if self.type == POINT_COMPASS:
        #     return

        # If the shape has a list of vertices (POINT PLACE)
        if hasattr(self.shape, 'vertices'):
            for i in range(0, len(self.shape.vertices)-1, 2):
                v = matrix44.apply_to_vector(displacement_matrix, [self.shape.vertices[i], self.shape.vertices[i+1], 0])
                self.shape.vertices[i], self.shape.vertices[i+1] = int(v[0]), int(v[1])
            return

        # Other points of interest have x and y (Circles)
        self.shape.x, self.shape.y = self.x, self.y

        # Rotate the shapes
        if self.type == POINT_TRESPASS:  # Rotate the rectangle
            q = Quaternion(displacement_matrix)
            if q.axis[2] > 0:  # Rotate around z axis upwards
                self.shape.rotation += math.degrees(q.angle)
            else:  # Rotate around z axis downward
                self.shape.rotation += math.degrees(-q.angle)
        if self.type == POINT_BLOCK or self.type == POINT_SHOCK:
            # Rotate and translate the other points of the triangle
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x2, self.shape.y2, 0])
            self.shape.x2, self.shape.y2 = v[0], v[1]
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x3, self.shape.y3, 0])
            self.shape.x3, self.shape.y3 = v[0], v[1]

    def delete(self):
        """ Delete the shape to remove it from the batch """
        self.shape.delete()  # Not sure whether it is necessary or not

    def select_if_near(self, x, y):
        """ If the point is near the x y coordinate, select this point and return True """
        # is_near = math.dist([x, y], [self.x, self.y]) < 20
        if math.dist([x, y], [self.x, self.y]) < 20:
            self.set_color('red')
            self.is_selected = True
        else:
            self.set_color()
            self.is_selected = False

    def update(self, displacement_matrix):
        """ Displace the point of interest to the position of the interaction """
        if self.interaction is not None:
            # self.x = self.interaction.x
            # self.y = self.interaction.y
            # self.shape.x = self.x
            # self.shape.y = self.y
            # self.shape.rotation = self.interaction.rotation

            # Move the point of interest to the position of the interaction
            self.reset_position()
            translation_matrix = matrix44.create_from_translation([self.interaction.x, self.interaction.y, 0])
            rotation_matrix = matrix44.create_from_z_rotation(math.radians(self.interaction.rotation))
            displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        # else:
        if displacement_matrix is not None:
            self.displace(displacement_matrix)
