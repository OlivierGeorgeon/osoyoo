from pyglet import shapes
import math
from pyrr import matrix44, Quaternion
from webcolors import name_to_rgb

POINT_ECHO = 0
POINT_TRESPASS = 1
POINT_SHOCK = 2
POINT_PUSH = 3
POINT_PLACE = 4


class Phenomenon:
    def __init__(self, x, y, batch, point_type):
        self.batch = batch
        self.type = point_type

        if self.type == POINT_PLACE:
            # Place: Blue circle
            self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("LightGreen"), batch=self.batch)
        if self.type == POINT_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("orange"), batch=self.batch)
        if self.type == POINT_TRESPASS:
            # Trespassing: black dash
            self.shape = shapes.Rectangle(x, y, 10, 60, color=name_to_rgb("black"), batch=self.batch)
            self.shape.anchor_position = 5, 30
        if self.type == POINT_SHOCK:
            # Chock interaction: red triangle
            self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("red"), batch=self.batch)
        if self.type == POINT_PUSH:
            # Pushing: yellow triangle
            self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("yellow"), batch=self.batch)

    def set_color(self, color_name=None):

        if color_name is None:
            if self.type == POINT_PLACE:
                # Place: Blue circle
                self.shape.color = name_to_rgb("LightGreen")
            if self.type == POINT_ECHO:
                # Echo: Orange circle
                self.shape.color = name_to_rgb("orange")
            if self.type == POINT_TRESPASS:
                # Trespassing: black dash
                self.shape.color = name_to_rgb("black")
            if self.type == POINT_SHOCK:
                # Chock interaction: red triangle
                self.shape.color = name_to_rgb("red")
            if self.type == POINT_PUSH:
                # Pushing: yellow triangle
                self.shape.color = name_to_rgb("yellow")
        else:
            self.shape.color = name_to_rgb(color_name)

    def displace(self, displacement_matrix):
        """ Applying the displacement matrix to the phenomenon """
        #  Rotate and translate the position
        v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x, self.shape.y, 0])
        self.shape.x, self.shape.y = v[0], v[1]

        # Rotate the shapes
        if self.type == 1:  # Rotate the rectangle
            q = Quaternion(displacement_matrix)
            if q.axis[2] > 0:  # Rotate around z axis upwards
                self.shape.rotation += math.degrees(q.angle)
            else:  # Rotate around z axis downward
                self.shape.rotation += math.degrees(-q.angle)
        if self.type == 2:  # Rotate and translate the other points of the triangle
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x2, self.shape.y2, 0])
            self.shape.x2, self.shape.y2 = v[0], v[1]
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x3, self.shape.y3, 0])
            self.shape.x3, self.shape.y3 = v[0], v[1]

    def delete(self):
        """ Delete the shape to remove it from the batch """
        self.shape.delete()

    def is_near(self, x, y):
        """ Return true if the point is near the x y coordinate """
        return math.dist([x, y], [self.shape.x, self.shape.y]) < 50
