import pyglet
from pyglet.gl import *
from pyglet.math import Mat4
from webcolors import name_to_rgb
import math
from pyrr import matrix44
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from ..InteractiveDisplay import InteractiveDisplay

ZOOM_IN_FACTOR = 1.2


class PhenomenonView(InteractiveDisplay):
    """Display a phenomenon"""
    def __init__(self, width=350, height=350, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Phenomenon View")
        self.set_minimum_size(150, 150)

        # Initialize OpenGL parameters
        # https://www.w3schools.com/cssref/css_colors.asp
        glClearColor(1.0, 1.0, 1.0, 1.0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.zoom_level = 1.3

        # Define the robot
        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.background)
        self.azimuth = 0  # Degree from north [0, 360]
        self.robot_pos_x = 0
        self.robot_pos_y = 0

        # Define the text area at the bottom of the view
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)
        self.label.color = (0, 0, 0, 255)

    def on_draw(self):
        """ Drawing the view """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Draw the phenomenon
        self.batch.draw()

        # Stack the rotation of the robot body
        # glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)

        # Draw the robot
        glTranslatef(self.robot_pos_x, self.robot_pos_y, 0)
        glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)
        self.robot_batch.draw()

        # Reset the projection to Identity to cancel the projection of the text
        glLoadIdentity()
        # Stack the projection of the text
        glOrtho(0, self.width, 0, self.height, -1, 1)
        # Draw the text in the bottom left corner
        self.label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        window_press_x = (x - self.width / 2) * self.zoom_level * 2
        window_press_y = (y - self.height / 2) * self.zoom_level * 2

        self.label.text = "Click: x:" + str(int(window_press_x)) + ", y:" + str(int(window_press_y))

    def add_polygon(self, points, color_string):
        """Add a polygon to the background of the view"""
        nb_points = int(len(points) / 2)
        nb_index = (nb_points-2) * 3
        v_index = [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5][0:nb_index]
        color = name_to_rgb(color_string)
        opacity = 255
        self.batch.add_indexed(3, gl.GL_TRIANGLES, self.background, v_index, ('v2i', points),
                               ('c4B', nb_points * (*color, opacity)))


# Testing the Phenomenon View by displaying the robot in a pretty position
# py -m autocat.Display.PhenomenonDisplay.PhenomenonView
if __name__ == "__main__":
    view = PhenomenonView()
    view.azimuth = 45
    view.robot_pos_x = -150
    view.robot_pos_y = -150

    pyglet.app.run()
