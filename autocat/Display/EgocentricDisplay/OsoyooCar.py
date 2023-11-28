from pyglet import shapes
from webcolors import name_to_rgb


ROBOT_BODY_COLOR = name_to_rgb("darkSlateBlue")
ROBOT_HEAD_COLOR = name_to_rgb("lightSteelBlue")
ROBOT_WHEEL_COLOR = name_to_rgb("darkBlue")
EMOTION_COLORS = ["black", "LavenderBlush", "LimeGreen", "DodgerBlue", "red", "DarkOrange"]


class OsoyooCar:
    def __init__(self, batch, group):
        self.batch = batch
        self.group = group

        # Create the body along the X axis (horizontal)
        self.robotBody = shapes.Rectangle(0, 0, 200, 160, color=ROBOT_BODY_COLOR, batch=self.batch, group=self.group)
        self.robotBody.anchor_position = 100, 80
        self.FLWheel = shapes.Rectangle(50, 100, 80, 36, color=ROBOT_WHEEL_COLOR, batch=self.batch, group=self.group)
        self.FLWheel.anchor_position = 40, 18
        self.FRWheel = shapes.Rectangle(50, -100, 80, 36, color=ROBOT_WHEEL_COLOR, batch=self.batch, group=self.group)
        self.FRWheel.anchor_position = 40, 18
        self.RLWheel = shapes.Rectangle(-50, 100, 80, 36, color=ROBOT_WHEEL_COLOR, batch=self.batch, group=self.group)
        self.RLWheel.anchor_position = 40, 18
        self.RRWheel = shapes.Rectangle(-50, -100, 80, 36, color=ROBOT_WHEEL_COLOR, batch=self.batch, group=self.group)
        self.RRWheel.anchor_position = 40, 18

        # The emotion led
        #  (circle end-up below the robot)
        # self.robot_emotion = shapes.Circle(-30, 0, 10, color=name_to_rgb("green"), batch=self.batch)
        self.robot_emotion = shapes.Rectangle(-30, 0, 20, 20, color=name_to_rgb(EMOTION_COLORS[2]), batch=self.batch,
                                              group=self.group)
        self.robot_emotion.anchor_position = 10, 10

        # Create the head
        self.head_x, self.head_y = 80, 0
        self.head_angle = 0
        self.robotHead = shapes.Rectangle(self.head_x, self.head_y, 20, 50, color=ROBOT_HEAD_COLOR, batch=self.batch,
                                          group=self.group)
        self.robotHead.anchor_position = 0, 25

    def rotate_head(self, head_angle):
        self.head_angle = head_angle
        self.robotHead.rotation = -self.head_angle  # head_angle is trigonometric while rotation is clockwise

    def emotion_color(self, emotion_code):
        """Colorize the emotion led from the emotion_code"""
        self.robot_emotion.color = name_to_rgb(EMOTION_COLORS[emotion_code])
