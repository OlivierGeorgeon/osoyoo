import pyglet
from pyglet.gl import *
import math
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from ..InteractiveDisplay import InteractiveDisplay


class BodyView(InteractiveDisplay):
    """Display the information in body memory"""
    def __init__(self, workspace, width=350, height=350, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Body Memory")
        self.set_minimum_size(150, 150)

        self.workspace = workspace

        # Initialize OpenGL parameters
        glClearColor(1.0, 235.0/256., 205.0/256., 1.0)
        self.zoom_level = 1.3

        # Define the robot
        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.background)

        # Define the text area at the bottom of the view
        self.label_batch = pyglet.graphics.Batch()
        self.label_clock = pyglet.text.Label('Clock: ', font_name='Verdana', font_size=10, x=10, y=50)
        self.label_clock.color = (0, 0, 0, 255)
        self.label_clock.batch = self.label_batch
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=30)
        self.label.color = (0, 0, 0, 255)
        self.label.batch = self.label_batch
        self.label_enaction = pyglet.text.Label('Speed: ', font_name='Verdana', font_size=10, x=10, y=10)
        self.label_enaction.color = (0, 0, 0, 255)
        self.label_enaction.batch = self.label_batch

    def on_draw(self):
        """ Drawing the view """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied in reversed order to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the robot body
        glRotatef(90 - self.workspace.memory.body_memory.body_azimuth(), 0.0, 0.0, 1.0)
        # Draw compass points
        self.batch.draw()
        # Draw the robot
        self.robot_batch.draw()

        # Reset the projection to Identity to cancel the projection of the text
        glLoadIdentity()
        # Stack the projection of the text
        glOrtho(0, self.width, 0, self.height, -1, 1)
        # Draw the text in the bottom left corner
        self.label_batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        # Rotate the click point by the inverse rotation of the robot
        v = self.workspace.memory.body_memory.body_quaternion.inverse * self.mouse_coordinates_to_point(x, y)
        t = round(math.degrees(math.atan2(v[1], v[0])))
        self.label.text = "Click: x:" + str(round(v[0])) + ", y:" + str(round(v[1])) + ", angle:" + str(t) + "°"


# Testing the EgocentricView by displaying the robot in a pretty position, and the mouse click coordinates
# py -m autocat.Display.BodyDisplay.BodyView
# if __name__ == "__main__":
#     view = BodyView()
#     view.robot.rotate_head(-45)  # Turn head 45° to the right
#     view.azimuth = 350           # Turn robot 10° to the left
#
#     pyglet.app.run()
