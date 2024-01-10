import numpy as np
from pyrr import Vector3
import platform
import subprocess
import pyglet
from pyglet.gl import *

ZOOM_IN_FACTOR = 1.2


def screen_scale():
    """Return 1 on normal screens, and 2 on mac for retina displays """
    # Not sure how to deal with a Mac that has a non-retina additional screen
    # TODO test with a Mac
    if platform.system() != 'Darwin':
        # This is not a Mac
        return 1
    output = subprocess.check_output('/usr/sbin/system_profiler SPDisplaysDataType', shell=True)
    output = output.decode('utf-8')
    for line in output.splitlines():
        if 'Retina' in line:
            return 2
    return 1


class InteractiveDisplay(pyglet.window.Window):
    """The parent class of interactive views"""
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, *args, **kwargs)
        self.zoom_level = 1.0

        # Initialize OpenGL parameters
        # https://www.w3schools.com/cssref/css_colors.asp
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.forefront = pyglet.graphics.OrderedGroup(5)
        self.screen_scale = screen_scale()

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        # Always display in the whole window. Scale for Mac.
        glViewport(0, 0, width * self.screen_scale, height * self.screen_scale)
        # glViewport(0, 0, width*2, height*2)  # For retina display on Mac

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy < 0 else 1/ZOOM_IN_FACTOR if dy > 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def mouse_coordinates_to_point(self, x, y):
        """ Return the point in world scale from mouse x and y """
        point_x = (x - self.width / 2) * self.zoom_level * 2
        point_y = (y - self.height / 2) * self.zoom_level * 2
        return Vector3([point_x, point_y, 0], dtype=int)
