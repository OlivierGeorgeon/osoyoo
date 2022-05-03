import pyglet
from pyglet.gl import *
import math
import numpy
from ..Display.OsoyooCar import OsoyooCar

ZOOM_IN_FACTOR = 1.2
IS_NORTH_UP = True  # Set to False to display the robot on the X axis


class EgocentricView(pyglet.window.Window):
    #  to draw a main window
    # set_caption: Set the window's caption, param: string(str)
    # set_minimum_size: resize window
    def __init__(self, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)

        # Initialize OpenGL parameters
        glClearColor(1.0, 1.0, 1.0, 1.0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)  # Allow Graphics transparency
        # pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.zoom_level = 1

        # Define the robot
        self.robot = OsoyooCar(self.batch, self.background)
        self.azimuth = 0

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

        # Stack the azimuth so the north is up
        if IS_NORTH_UP:
            glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)

        # Draw the robot and the points of interest
        self.batch.draw()

        # Draw the text in the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label.draw()

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired from https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def set_mouse_press_coordinate(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        window_press_x = (x - self.width / 2) * self.zoom_level * 2
        window_press_y = (y - self.height / 2) * self.zoom_level * 2
        # Polar coordinates from the window center
        r = numpy.hypot(window_press_x, window_press_y)
        theta_window = math.atan2(window_press_y, window_press_x)

        theta_robot = theta_window
        # If display north up then compute the polar angle from the robot axis
        if IS_NORTH_UP:
            theta_robot += math.radians(self.azimuth - 90) + 2 * math.pi
            theta_robot %= 2 * math.pi
            if theta_robot > math.pi:
                theta_robot -= 2 * math.pi
        # Cartesian coordinates from the robot axis
        z = r * numpy.exp(1j * theta_robot)
        mouse_press_x, mouse_press_y = int(z.real), int(z.imag)
        mouse_press_angle = int(math.degrees(theta_robot))
        self.label.text = "Click: x:" + str(mouse_press_x) + ", y:" + str(mouse_press_y) \
                          + ", angle:" + str(mouse_press_angle) + "°"
        return mouse_press_x, mouse_press_y, mouse_press_angle


# Showing the EgocentricView
# py -m Python.OsoyooControllerBSN.Display.EgocentricView
if __name__ == "__main__":
    view = EgocentricView()
    view.robot.rotate_head(-45)  # Turn head 45° to the right
    view.azimuth = 350           # Turn robot 10° to the left

    @view.event
    def on_mouse_press(x, y, button, modifiers):
        view.set_mouse_press_coordinate(x, y, button, modifiers)  # Display mouse click coordinates

    pyglet.app.run()
