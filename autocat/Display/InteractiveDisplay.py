import numpy
import math
import pyglet
from pyglet.gl import *

ZOOM_IN_FACTOR = 1.2


class InteractiveDisplay(pyglet.window.Window):
    """The parent class of interactive views"""
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, *args, **kwargs)
        self.zoom_level = 1.0

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        # Always display in the whole window
        glViewport(0, 0, width, height)      # For standard display
        # glViewport(0, 0, width*2, height*2)  # For retina display on Mac

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def get_allocentric_coordinates(self, x, y):
        """ Computing the position of the mouse click in allocentric coordinates from the window center"""
        window_press_x = (x - self.width / 2) * self.zoom_level * 2
        window_press_y = (y - self.height / 2) * self.zoom_level * 2
        # Polar coordinates from the window center
        theta_window = math.atan2(window_press_y, window_press_x)
        radius = numpy.hypot(window_press_x, window_press_y)
        return window_press_x, window_press_y, theta_window, radius