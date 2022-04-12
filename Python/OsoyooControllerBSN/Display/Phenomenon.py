from pyglet import shapes
import math
from pyrr import matrix44, Quaternion


class Phenomenon:
    def __init__(self, x, y, batch, shape=0, color=0):
        self.batch = batch
        self.type = shape
        # self.angle = 0

        if shape == 0:
            # Green circle: Echo
            self.shape = shapes.Circle(x, y, 20, color=(50, 225, 30), batch=self.batch)
        elif shape == 1:
            # Red dash: black line
            self.shape = shapes.Rectangle(x, y, 20, 60, color=(200, 0, 0), batch=self.batch)
            self.shape.anchor_position = 10, 30
        else:
            # Triangle: collision
            if color == 1:
                # Pressing interaction: orange triangle
                self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=(255, 165, 0), batch=self.batch)
            else:
                # Chock interaction: red triangle
                self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=(255, 0, 0), batch=self.batch)

    def rotate(self, angle):
        """ Rotating the phenomenon """
        theta = -math.radians(angle)
        x = math.cos(theta) * self.shape.x - math.sin(theta) * self.shape.y
        y = math.sin(theta) * self.shape.x + math.cos(theta) * self.shape.y
        self.shape.x = x
        self.shape.y = y
        # self.angle += angle
        if self.type == 1:  # Rotate the rectangle
            self.shape.rotation += angle

        theta2 = -math.radians(angle)
        if self.type == 2:  # Rotate the triangle
            self.shape.x2 = self.shape.x + math.cos(theta2) * 40 - math.sin(theta2) * -30
            self.shape.y2 = self.shape.y + math.sin(theta2) * 40 + math.cos(theta2) * -30
            self.shape.x3 = self.shape.x + math.cos(theta2) * 40 - math.sin(theta2) * 30
            self.shape.y3 = self.shape.y + math.sin(theta2) * 40 + math.cos(theta2) * 30

    def translate(self, translation):
        """ Translating the phenomenon """
        self.shape.x -= translation[0]
        self.shape.y -= translation[1]
        if self.type == 2:  # Translate the triangle
            self.shape.x2 -= translation[0]
            self.shape.y2 -= translation[1]
            self.shape.x3 -= translation[0]
            self.shape.y3 -= translation[1]

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
