from pyglet import shapes


class OsoyooCar:
    def __init__(self, batch):
        self.batch = batch

        # Create the body along the X axis (horizontal)
        self.robotBody = shapes.Rectangle(0, 0, 200, 160, color=(0, 0, 0), batch=self.batch)
        self.robotBody.anchor_position = 100, 80
        self.FLWheel = shapes.Rectangle(50, 100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.FLWheel.anchor_position = 40, 18
        self.FRWheel = shapes.Rectangle(50, -100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.FRWheel.anchor_position = 40, 18
        self.RLWheel = shapes.Rectangle(-50, 100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.RLWheel.anchor_position = 40, 18
        self.RRWheel = shapes.Rectangle(-50, -100, 80, 36, color=(0, 0, 0), batch=self.batch)
        self.RRWheel.anchor_position = 40, 18

        # Create the head
        self.head_x, self.head_y = 80, 0
        self.head_angle = 0
        self.robotHead = shapes.Rectangle(self.head_x, self.head_y, 20, 50, color=(150, 150, 150), batch=self.batch)
        self.robotHead.anchor_position = 0, 25

        self.azimuth = 0

    def rotate_head(self, head_angle):
        self.head_angle = head_angle
        self.robotHead.rotation = -self.head_angle  # head_angle is trigonometric while rotation is clockwise
