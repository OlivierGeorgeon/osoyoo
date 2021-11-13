import pyglet
from pyglet import shapes


class OsoyooCar:
    def __init__(self, batch):
        self.batch = batch

        # The robot is drawn along the X axis (horizontal)
        self.robotBody = shapes.Rectangle(0, 0, 200, 160, color=(0, 0, 0), batch=self.batch)
        self.robotBody.anchor_position = self.robotBody.width / 2, self.robotBody.height / 2
        self.FLWheel = shapes.Rectangle(50, 100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.FLWheel.anchor_position = 40, 18
        self.FRWheel = shapes.Rectangle(50, -100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.FRWheel.anchor_position = 40, 18
        self.RLWheel = shapes.Rectangle(-50, 100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.RLWheel.anchor_position = 40, 18
        self.RRWheel = shapes.Rectangle(-50, -100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.RRWheel.anchor_position = 40, 18
        self.robotHead = shapes.Rectangle(80, 0, 20, 50, color=(150, 150, 150), batch=self.batch)
        self.robotHead.anchor_position = 0, 25

        self.azimuth = 0
        self.head_angle = 0

    def rotate_head(self, head_angle):
        self.head_angle = head_angle
        self.robotHead.rotation = -self.head_angle
