import pyglet
from pyglet.gl import *
import math
from pyrr import matrix44
from autocat.Display.RobotDisplay import RobotDisplay
from ..InteractiveDisplay import InteractiveDisplay


class EgocentricView(InteractiveDisplay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.is_north_up = False  # Reset to display the robot on the X axis
        self.set_caption("Egocentric Memory")
        self.zoom_level = 2

    def on_draw(self):
        """ Drawing the view """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(self.left, self.right, self.bottom, self.top, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        # if self.is_north_up:
        #     glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)
        # else:
        glRotatef(90, 0.0, 0.0, 1.0)

        # Draw the points of interest
        self.batch.draw()
        # Draw the robot
        self.egocentric_batch.draw()

        # Draw the text at the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label_batch.draw()

    def get_prompt_point(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        click_point = self.mouse_coordinates_to_point(x, y)
        # if self.is_north_up:
        #     # TODO test this
        #     rotation_matrix = matrix44.create_from_z_rotation(-math.radians(self.azimuth - 90))
        # else:
        rotation_matrix = matrix44.create_from_z_rotation(math.pi/2)
        click_point = matrix44.apply_to_vector(rotation_matrix, click_point).astype(int)
        click_angle = math.degrees(math.atan2(click_point[1], click_point[0]))
        # Display the mouse click coordinates at the bottom of the view
        self.label3.text = f"Click: ({click_point[0]:.0f}, {click_point[1]:.0f}), angle: {click_angle:.0f}°"
        # Return the click position to the controller
        return click_point
