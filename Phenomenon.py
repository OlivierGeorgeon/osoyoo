from pyglet import shapes
import math
from pyrr import matrix33, matrix44, Vector3


class Phenomenon:
    def __init__(self, x, y, batch, shape=0):
        self.batch = batch
        self.type = shape
        self.angle = 0

        if shape == 0:
            # Green circle: Echo
            self.shape = shapes.Circle(x, y, 20, color=(50, 225, 30), batch=self.batch)
        elif shape == 1:
            # Red dash: black line
            self.shape = shapes.Rectangle(x, y, 20, 40, color=(200, 0, 0), batch=self.batch)
            # self.shape.position = x, y
            self.shape.anchor_position = 10, 20
        else:
            # Orange triangle: Block
            self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=(255, 165, 0), batch=self.batch)
            # self.shape.x = x
            # self.shape.y = y

    def rotate(self, angle):
        """ Rotating the phenomenon """
        theta = -math.radians(angle)
        x = math.cos(theta) * self.shape.x - math.sin(theta) * self.shape.y
        y = math.sin(theta) * self.shape.x + math.cos(theta) * self.shape.y
        self.shape.x = x
        self.shape.y = y
        self.angle += angle
        self.shape.rotation = self.angle
        if self.type == 1:  # Rotate the rectangle
            pass

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

    def displace(self, displacement_matrix):  #TODO make it work
        """ Applying the displacement matrix to the phenomenon position """
        v = Vector3([self.shape.x, self.shape.y, 0])
        m = matrix33.create_from_matrix44(displacement_matrix)
        v2 = matrix33.apply_to_vector(m, v)
        self.shape.x = v2[0]
        self.shape.y = v2[1]
