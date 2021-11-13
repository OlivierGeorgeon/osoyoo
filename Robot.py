import pyglet
from pyglet import shapes


class Robot:
    def __init__(self, batch):
        self.batch = batch

        self.robotBody = shapes.Rectangle(0, 0, 160, 200, color=(0, 0, 0), batch=self.batch)
        self.robotBody.anchor_position = 80, 100
        self.FLWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=self.batch)
        self.FLWheel.anchor_position = 120, -10
        self.FRWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=self.batch)
        self.FRWheel.anchor_position = -85, -10
        self.RLWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=self.batch)
        self.RLWheel.anchor_position = 120, 90
        self.RRWheel = shapes.Rectangle(0, 0, 36, 80, color=(0, 0, 0), batch=self.batch)
        self.RRWheel.anchor_position = -85, 90
        self.robotHead = shapes.Rectangle(0, 80, 50, 20, color=(150, 150, 150), batch=self.batch)
        self.robotHead.anchor_position = 25, 0

        self.azimuth = 20
        self.head_angle = 0

    def rotate_head(self, head_angle):
        self.head_angle = head_angle
        self.robotHead.rotation = -self.head_angle
