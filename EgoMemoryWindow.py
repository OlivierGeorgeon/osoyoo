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
        self.wifiInterface = WifiInterface()

        self.phenomena = []
        # self.origin = shapes.Circle(0, 0, 20, color=(150, 150, 225))
        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20


        self.environment_matrix = (GLfloat * 16)(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)
        #glLoadIdentity()
        #glTranslatef(150, 0, 0)
        #glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)  # The only way i found to set envMat to identity

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        # glRotatef(90, 0.0, 0.0, 1.0)

        # Draw the robot
        self.robot_batch.draw()
        # Draw the phenomena
        self.phenomena_batch.draw()

        # Stack the environment's displacement and draw the origin just to check
        glMultMatrixf(self.environment_matrix)
        self.origin.draw()  # Draw the origin of the robot

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
        outcome = json.loads(outcome_string)

        # Update the model from the outcome
        glLoadIdentity()
        if text == "8":
            glTranslatef(-200, 0, 0)
        if text == "2":
            glTranslatef(200, 0, 0)

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
            glRotatef(-outcome['yaw'], 0, 0, 1.0)

        glMultMatrixf(self.environment_matrix)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.environment_matrix)


if __name__ == "__main__":
    em_window = EgoMemoryWindow()
    pyglet.app.run()
