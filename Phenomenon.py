from pyglet import shapes
import math


class Phenomenon:
    def __init__(self, x, y, batch):
        self.batch = batch
        self.x = x
        self.y = y

        self.circle = shapes.Circle(self.x, self.y, 20, color=(50, 225, 30), batch=self.batch)
        #self.line = shapes.Line(100, 100, 100, 200, color=(0, 0, 0), width=19, batch=self.batch)

    def rotate(self, angle):
        theta = math.radians(angle)
        x = math.cos(theta)*self.x - math.sin(theta)*self.y
        y = math.sin(theta)*self.x + math.cos(theta)*self.y
        self.x = x
        self.y = y
        self.circle.x = self.x
        self.circle.y = self.y

    def translate(self, translation):
        self.x += translation[0]
        self.y += translation[1]
        self.circle.x = self.x
        self.circle.y = self.y
