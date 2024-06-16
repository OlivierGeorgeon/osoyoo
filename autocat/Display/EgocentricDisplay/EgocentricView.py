from pyglet.gl import *
import math
from pyrr import matrix44
from ..InteractiveDisplay import InteractiveDisplay


class EgocentricView(InteractiveDisplay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.zoom_level = 2
        self.robot_rotate = 90  # Show the robot head up

    # def on_draw(self):
    #     """ Drawing the view """
    #     glClear(GL_COLOR_BUFFER_BIT)
    #     glLoadIdentity()
    #
    #     # The transformations are stacked, and applied backward to the vertices
    #
    #     # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
    #     glOrtho(self.left, self.right, self.bottom, self.top, 1, -1)
    #
    #     # Stack the rotation of the world so the robot's front is up
    #     # glRotatef(90, 0.0, 0.0, 1.0)
    #     glRotatef(self.robot_rotate, 0.0, 0.0, 1.0)
    #
    #     # Draw the points of interest
    #     # self.batch.draw()
    #     # Draw the robot
    #     self.egocentric_batch.draw()
    #
    #     # Draw the text at the bottom left corner
    #     glLoadIdentity()
    #     glOrtho(0, self.width, 0, self.height, -1, 1)
    #     self.label_batch.draw()

    # def mouse_to_ego_point(self, x, y, button, modifiers):
    #     """ Computing the position of the mouse click relative to the robot in mm and degrees """
    #     ego_point = self.mouse_coordinates_to_point(x, y)
    #     rotation_matrix = matrix44.create_from_z_rotation(math.radians(self.robot_rotate))
    #     ego_point = matrix44.apply_to_vector(rotation_matrix, ego_point).astype(int)
    #     ego_angle = math.degrees(math.atan2(ego_point[1], ego_point[0]))
    #     # Display the mouse click coordinates at the bottom of the view
    #     self.label3.text = f"Click: ({ego_point[0]:.0f}, {ego_point[1]:.0f}), angle: {ego_angle:.0f}°"
    #     # Return the click position to the controller
    #     return ego_point
