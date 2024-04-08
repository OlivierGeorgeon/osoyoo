import numpy as np
import pyglet
from pyglet.gl import *
from webcolors import name_to_rgb
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from ..InteractiveDisplay import InteractiveDisplay


class PhenomenonView(InteractiveDisplay):
    """Display a phenomenon"""
    def __init__(self, width=350, height=350, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Terrain Phenomenon View")
        self.set_minimum_size(150, 150)

        # # Initialize OpenGL parameters
        # # https://www.w3schools.com/cssref/css_colors.asp
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.zoom_level = 6

        # Define the robot
        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.background)
        self.robot_translate = np.array([0, 0, 0], dtype=float)
        self.robot_rotate = 0
        self.phenomenon_point = np.array([0, 0, 0], dtype=float)

        self.hull_line = None

        # Define the text area at the bottom of the view
        self.label_batch = pyglet.graphics.Batch()
        self.label1 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=50)
        self.label1.color = (0, 0, 0, 255)
        self.label1.batch = self.label_batch
        self.label2 = pyglet.text.Label('Confidence: None', font_name='Verdana', font_size=10, x=10, y=30)
        self.label2.color = (0, 0, 0, 255)
        self.label2.batch = self.label_batch
        self.label3 = pyglet.text.Label('Origin direction: None', font_name='Verdana', font_size=10, x=10, y=10)
        self.label3.color = (0, 0, 0, 255)
        self.label3.batch = self.label_batch

    def on_draw(self):
        """ Drawing the view """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        # glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
        #         self.height * self.zoom_level, 1, -1)
        glOrtho(self.left, self.right, self.bottom, self.top, 1, -1)


        # Draw the phenomenon
        self.batch.draw()

        # Stack the rotation and translation of the robot body
        glTranslatef(*self.robot_translate)
        glRotatef(self.robot_rotate, 0.0, 0.0, 1.0)
        # Draw the robot
        self.robot_batch.draw()

        # Reset the projection to Identity to cancel the projection of the text
        glLoadIdentity()
        # Stack the projection of the text
        glOrtho(0, self.width, 0, self.height, -1, 1)
        # Draw the text in the bottom left corner
        self.label_batch.draw()

    def add_lines(self, points, color_string):
        """Update the hull at the forefront of the view"""
        if self.hull_line is not None:
            self.hull_line.delete()
            self.hull_line = None

        if points is not None:
            # points += points[0:2]  # Loop back to the last point
            nb_points = int(len(points) / 2)
            if nb_points >= 2:
                index = []  # The initial point
                for i in range(0, nb_points - 1):
                    index.extend([i, i + 1])
                # v_index += [nb_points]  # Close the loop
                self.hull_line = self.batch.add_indexed(nb_points, gl.GL_LINES, self.forefront, index, ('v2i', points),
                                                        ('c4B', nb_points * (*name_to_rgb(color_string), 255)))
