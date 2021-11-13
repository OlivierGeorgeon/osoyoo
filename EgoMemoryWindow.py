import pyglet
from pyglet.gl import *
from OsoyooCar import OsoyooCar
from WifiInterface import WifiInterface
import json
from Phenomenon import Phenomenon
import math
from pyglet import shapes

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


class EgoMemoryWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.robot_batch = pyglet.graphics.Batch()
        self.phenomena_batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.robot = OsoyooCar(self.robot_batch)
        self.origin = shapes.Circle(0, 0, 20, color=(150, 150, 225))
        self.robot.rotate_head(20)

        self.wifiInterface = WifiInterface()

        self.phenomena = []

        self.dx = 0
        self.dy = 0
        self.dangle = 0

        self.envMat = (GLfloat * 16)(1, 0, 0, 0,
                                     0, 1, 0, 0,
                                     0, 0, 1, 0,
                                     0, 0, 0, 1)
        #glLoadIdentity()
        #glTranslatef(150, 0, 0)
        #glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)  # The only way i found to set envMat to identity

    def on_draw(self):
        # Clear window with ClearColor
        glClear(GL_COLOR_BUFFER_BIT)

        glLoadIdentity()
        # Save the default model view matrix
        # glPushMatrix()
        # Set orthographic projection matrix. Centered on (0,0)
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Draw the robot
        # glRotatef(90, 0.0, 0.0, 1.0)  # Rotate upwards
        self.robot_batch.draw()

        # glTranslatef(150, 0, 0)
        glMultMatrixf(self.envMat)  # Apply the cumulative displacement to the environment
        # Draw the phenomena
        self.phenomena_batch.draw()
        self.origin.draw()  # The origin of the robot

    def on_resize(self, width, height):
        # Display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired from https://www.py4u.net/discuss/148957
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def on_text(self, text):
        print("Send action: ", text)
        outcome_string = self.wifiInterface.enact(text)
        print(outcome_string)

        if text == "8":
            glLoadMatrixf(self.envMat)
            glTranslatef(-200, 0, 0)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)
        if text == "2":
            glLoadMatrixf(self.envMat)
            glTranslatef(200, 0, 0)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)

        outcome = json.loads(outcome_string)
        if 'head_angle' in outcome:
            head_angle = outcome['head_angle']
            print("Head angle %i" % head_angle)
            self.robot.rotate_head(head_angle)
        if 'echo_distance' in outcome:
            echo_distance = outcome['echo_distance']
            print("Echo distance %i" % echo_distance)
            x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
            y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
            obstacle = Phenomenon(x, y, self.phenomena_batch)
            self.phenomena.append(obstacle)
        if 'yaw' in outcome:
            self.dangle = outcome['yaw']


if __name__ == "__main__":
    em_window = EgoMemoryWindow()
    pyglet.app.run()
