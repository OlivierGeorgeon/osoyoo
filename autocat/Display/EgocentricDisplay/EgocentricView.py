import pyglet
from pyglet.gl import *
import math
import numpy
from pyrr import matrix44
from . OsoyooCar import OsoyooCar
from ..InteractiveDisplay import InteractiveDisplay


class EgocentricView(InteractiveDisplay):
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.is_north_up = False  # Reset to display the robot on the X axis
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)

        # Initialize OpenGL parameters
        glClearColor(1.0, 1.0, 1.0, 1.0)
        # pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        # self.batch = pyglet.graphics.Batch()
        # self.background = pyglet.graphics.OrderedGroup(0)
        # self.foreground = pyglet.graphics.OrderedGroup(1)
        # self.zoom_level = 1

        # Define the robot
        self.robot = OsoyooCar(self.batch, self.background)
        self.azimuth = 0  # Degree from north [0, 360]

        # Define the text area at the bottom of the view
        self.label_batch = pyglet.graphics.Batch()
        self.label1 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)
        self.label1.color = (0, 0, 0, 255)
        self.label1.batch = self.label_batch
        self.label2 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=30)
        self.label2.color = (0, 0, 0, 255)
        self.label2.batch = self.label_batch
        # self.label_left_speed = pyglet.text.Label('Leftward speed: ', font_name='Verdana', font_size=10, x=10, y=10)
        # self.label_left_speed.color = (0, 0, 0, 255)
        # self.label_left_speed.batch = self.label_batch

    def on_draw(self):
        """ Drawing the view """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        if self.is_north_up:
            glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)
        else:
            glRotatef(90, 0.0, 0.0, 1.0)

        # Draw the robot and the points of interest
        self.batch.draw()

        # Draw the text at the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label_batch.draw()

    def get_prompt_point(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        prompt_point = self.mouse_coordinates_to_point(x, y)
        if self.is_north_up:
            # TODO test this
            rotation_matrix = matrix44.create_from_z_rotation(-math.radians(self.azimuth - 90))
        else:
            rotation_matrix = matrix44.create_from_z_rotation(math.pi/2)
        prompt_point = matrix44.apply_to_vector(rotation_matrix, prompt_point).astype(int)

        # Cartesian coordinates from the robot axis
        prompt_polar_angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))
        # Display the mouse click coordinates at the bottom of the view
        self.label1.text = "Click: x:" + str(prompt_point[0]) + ", y:" + str(prompt_point[1]) \
                           + ", angle:" + str(prompt_polar_angle) + "°"
        # Return the click position to the controller
        return prompt_point


# Testing the EgocentricView by displaying the robot in a pretty position, and the mouse click coordinates
# py -m autocat.Display.EgocentricDisplay.EgocentricView
if __name__ == "__main__":
    view = EgocentricView()
    view.robot.rotate_head(-45)  # Turn head 45° to the right
    view.azimuth = 350           # Turn robot 10° to the left

    @view.event
    def on_mouse_press(x, y, button, modifiers):
        view.get_prompt_point(x, y, button, modifiers)  # Display mouse click coordinates

    pyglet.app.run()
