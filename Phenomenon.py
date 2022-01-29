from pyglet import shapes
import math
from pyrr import matrix44, Vector4


class Phenomenon:
    def __init__(self, x, y, batch, shape=0):
        self.batch = batch
        self.type = shape
        # self.x = x
        # self.y = y
        self.angle = 0

        if shape == 0:
            # Green circle: Echo
            self.shape = shapes.Circle(x, y, 20, color=(50, 225, 30), batch=self.batch)
        elif shape == 1:
            # Line
            self.shape = shapes.Rectangle(x, y, 20, 40, color=(200, 0, 0), batch=self.batch)
            #  self.shape.position = x, y
            self.shape.anchor_position = 10, 20
        else:
            # Block
            self.shape = shapes.Triangle(0, 0, x+40, y-30, x+40, y+30, color=(255, 165, 0), batch=self.batch)
            self.shape.x = x
            self.shape.y = y
            # self.shape = shapes.Circle(self.x, self.y, 20, color=(255, 0, 0), batch=self.batch)

    def rotate(self, angle):
        theta = -math.radians(angle)
        self.shape.x = math.cos(theta) * self.shape.x - math.sin(theta) * self.shape.y
        self.shape.y = math.sin(theta) * self.shape.x + math.cos(theta) * self.shape.y
        self.angle += angle
        theta2 = -math.radians(angle)
        if self.type == 1:
            self.shape.rotation = angle
        if self.type == 2:
            self.shape.x2 = self.shape.x + math.cos(theta2) * 40 - math.sin(theta2) * -30
            self.shape.y2 = self.shape.y + math.sin(theta2) * 40 + math.cos(theta2) * -30
            self.shape.x3 = self.shape.x + math.cos(theta2) * 40 - math.sin(theta2) * 30
            self.shape.y3 = self.shape.y + math.sin(theta2) * 40 + math.cos(theta2) * 30

    def translate(self, translation):
        # self.x -= translation[0]
        # self.y -= translation[1]
        self.shape.x -= translation[0]
        self.shape.y -= translation[1]
        if self.type == 2:
            self.shape.x2 -= translation[0]
            self.shape.y2 -= translation[1]
            self.shape.x3 -= translation[0]
            self.shape.y3 -= translation[1]

    def displace(self, displacement_matrix):  # not working yet
        v = Vector4([self.shape.x, self.shape.y, 0, 0])
        v = displacement_matrix * v
        self.shape.x = v[0]
        self.shape.y = v[1]
