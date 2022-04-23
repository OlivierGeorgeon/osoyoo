import pyglet
from pyglet.gl import *
from ..Display.OsoyooCar import OsoyooCar
import math
import numpy

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR


class EgoMemoryWindow(pyglet.window.Window):
    #  to draw a main window
    # set_caption: Set the window's caption, param: string(str)
    # set_minimum_size: resize window
    def __init__(self, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()  # create a batch
        self.background = pyglet.graphics.OrderedGroup(0)  # Will be used to manage the overlapping of shapes
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.zoom_level = 1

        # draw the robot for display in the window using the batch parameter and used OsoyooCar's file
        self.robot = OsoyooCar(self.batch)
        self.azimuth = 0

        # Room to write some text
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)
        self.label.color = (0, 0, 0, 255)

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0

    def on_draw(self):

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices
        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)
        # Draw the robot and the phenomena
        self.batch.draw()

        # Draw the text in the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label.draw()

    def on_resize(self, width, height):
        # Display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired from https://www.py4u.net/discuss/148957
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f


    def set_mouse_press_coordinate(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        mouse_press_x = (x - self.width / 2) * self.zoom_level * 2
        mouse_press_y = (y - self.height / 2) * self.zoom_level * 2
        # Polar coordinates from the window center
        r = numpy.hypot(mouse_press_x, mouse_press_y)
        theta_window = math.atan2(mouse_press_y, mouse_press_x)
        # Polar angle from the robot axis
        theta_robot = theta_window + math.radians(self.azimuth - 90) + 2 * math.pi
        theta_robot %= 2 * math.pi
        if theta_robot > math.pi:
            theta_robot -= 2 * math.pi
        # Cartesian coordinates from the robot axis
        z = r * numpy.exp(1j * theta_robot)
        self.mouse_press_x, self.mouse_press_y = int(z.real), int(z.imag)
        self.mouse_press_angle = int(math.degrees(theta_robot))

        self.label.text = "Click: x:" + str(self.mouse_press_x) + ", y:" + str(self.mouse_press_y) \
                          + ", angle:" + str(self.mouse_press_angle) + "°"


# Showing the EgoMemoryWindow
# py -m Python.OsoyooControllerBSN.Display.EgoMemoryWindow
if __name__ == "__main__":
    em_window = EgoMemoryWindow()

    pyglet.app.run()
