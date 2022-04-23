from pyglet import shapes
import math
from pyrr import matrix44, Quaternion
from webcolors import name_to_rgb

SHAPE_CIRCLE = 0
SHAPE_LINE = 1

class Phenomenon:
    def __init__(self, x, y, batch, shape=0, color=0):
        self.batch = batch
        self.type = shape
        # self.angle = 0

        if shape == SHAPE_CIRCLE:
            if color == 1:
                # Blue circle: Place
                self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("LightGreen"), batch=self.batch)
            else:
                # Orange circle: Echo
                self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("orange"), batch=self.batch)
        elif shape == SHAPE_LINE:
            # Red dash: black line
            self.shape = shapes.Rectangle(x, y, 10, 60, color=name_to_rgb("black"), batch=self.batch)
            self.shape.anchor_position = 5, 30
        else:
            # Triangle: collision
            if color == 1:
                # Pressing interaction: yellow triangle
                self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("yellow"), batch=self.batch)
            else:
                # Chock interaction: red triangle
                self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("red"), batch=self.batch)

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