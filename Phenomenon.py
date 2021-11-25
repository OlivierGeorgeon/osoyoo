from pyglet import shapes
import math


class Phenomenon:
    def __init__(self, x, y, batch, shape=0):
        self.batch = batch
        self.x = x
        self.y = y

        if shape == 0:
            self.shape = shapes.Circle(self.x, self.y, 20, color=(50, 225, 30), batch=self.batch)
        else:
            self.shape = shapes.Rectangle(0, 0, 14, 80, color=(200, 0, 0), batch=self.batch)
            self.shape.anchor_position = 7, 40

    def rotate(self, angle):
        theta = math.radians(angle)
        x = math.cos(theta)*self.x - math.sin(theta)*self.y
        y = math.sin(theta)*self.x + math.cos(theta)*self.y
        self.x = x
        self.y = y
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.rotation = -angle

    def translate(self, translation):
        self.x += translation[0]
        self.y += translation[1]
        self.shape.x = self.x
        self.shape.y = self.y
