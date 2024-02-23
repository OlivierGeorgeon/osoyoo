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
        #Karim:
        self.dragging = False
        self.start_drag_x = 0
        self.start_drag_y = 0

        # Karim:
        # self.window_x = 0
        # self.window_y = 0
        # self.window_width = width
        # self.window_height = height

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

        # Karim:
        # glViewport(0, 0, int(width * self.screen_scale * self.zoom_level),int(height * self.screen_scale * self.zoom_level))

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy < 0 else 1/ZOOM_IN_FACTOR if dy > 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

        # Karim:
        # Get the cursor position relative to the window
        # cursor_x = (x - self.window_x) / (self.window_width * self.zoom_level)
        # cursor_y = (y - self.window_y) / (self.window_height * self.zoom_level)
        #
        # # Calculate the new zoom level based on the mouse wheel direction
        # zoom_factor = ZOOM_IN_FACTOR if dy < 0 else 1 / ZOOM_IN_FACTOR if dy > 0 else 1
        # new_zoom_level = self.zoom_level * zoom_factor
        #
        # # Ensure the zoom level is within the specified range
        # if .4 < new_zoom_level < 5:
        #     # Calculate the shift in the zoomed position based on the cursor position
        #     shift_x = cursor_x * (self.zoom_level - new_zoom_level)
        #     shift_y = cursor_y * (self.zoom_level - new_zoom_level)
        #
        #     # Update the zoom level
        #     self.zoom_level = new_zoom_level
        #
        #     # Update the position of the window based on the cursor position
        #     self.window_x += shift_x * self.window_width
        #     self.window_y += shift_y * self.window_height
        #
        #     # Update the size of the window based on the zoom level
        #     self.window_width *= self.zoom_level
        #     self.window_height *= self.zoom_level
        #
        # self.on_draw()

    def mouse_coordinates_to_point(self, x, y):
        """ Return the point in world scale from mouse x and y """
        point_x = (x - self.width / 2) * self.zoom_level * 2
        point_y = (y - self.height / 2) * self.zoom_level * 2
        return Vector3([point_x, point_y, 0], dtype=int)

        # Karim:
        # point_x = (x - self.window_x - self.width / 2) * self.zoom_level * 2
        # point_y = (y - self.window_y - self.height / 2) * self.zoom_level * 2
        # return Vector3([point_x, point_y, 0], dtype=int)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.dragging = True
            self.start_drag_x = x
            self.start_drag_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            # Calculate the new window position
            new_x = self.x + dx
            new_y = self.y + dy

            # Update the window position
            self.set_location(new_x, new_y)
            #self.start_drag_x = x
            #self.start_drag_y = y
            self.on_draw()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.dragging = False
            # self.start_drag_x = 0
            # self.start_drag_y = 0
