from pyrr import Vector3
import platform
import subprocess
import pyglet
from pyglet.gl import *

ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


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
        conf = Config(sample_buffers=1, samples=4, depth_size=0, double_buffer=True)
        super().__init__(width, height, config=conf, *args, **kwargs)
        self.zoom_level = 1.0
        self.left = -width / 2
        self.right = width / 2
        self.bottom = -height / 2
        self.top = height / 2
        self.drag_x = 0
        self.drag_y = 0

        # Initialize OpenGL parameters
        # https://www.w3schools.com/cssref/css_colors.asp
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        # Set alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.forefront = pyglet.graphics.OrderedGroup(5)
        self.screen_scale = screen_scale()

    def mouse_coordinates_to_point(self, x, y):
        """ Return the point in world reference frame from mouse x and y """
        point_x = (x - self.drag_x - self.width / 2) * self.zoom_level
        point_y = (y - self.drag_y - self.height / 2) * self.zoom_level
        return Vector3([point_x, point_y, 0], dtype=int)

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        # Recompute the corners of the world window
        self.left = (-width / 2 - self.drag_x) * self.zoom_level
        self.right = (width / 2 - self.drag_x) * self.zoom_level
        self.bottom = (-height / 2 - self.drag_y) * self.zoom_level
        self.top = (height / 2 - self.drag_y) * self.zoom_level
        # Always display in the whole window. Scale for Mac.
        glViewport(0, 0, width * self.screen_scale, height * self.screen_scale)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Drag the world within the window"""
        # The total amount of drag
        self.drag_x += dx
        self.drag_y += dy
        # Recompute the corners of the world window
        self.left = (-self.width / 2 - self.drag_x) * self.zoom_level
        self.right = (self.width / 2 - self.drag_x) * self.zoom_level
        self.bottom = (-self.height / 2 - self.drag_y) * self.zoom_level
        self.top = (self.height / 2 - self.drag_y) * self.zoom_level

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zoom the window from the center of the world"""
        f = ZOOM_OUT_FACTOR if dy > 0 else ZOOM_IN_FACTOR if dy < 0 else 1
        if .6 < self.zoom_level * f < 8:
            self.zoom_level *= f
            self.left *= f
            self.right *= f
            self.bottom *= f
            self.top *= f

    # Zoom based on mouse position
    # def on_mouse_scroll(self, x, y, dx, dy):
    #     # Get scale factor
    #     f = ZOOM_OUT_FACTOR if dy > 0 else ZOOM_IN_FACTOR if dy < 0 else 1
    #     # If zoom_level is in the proper range
    #     if .2 < self.zoom_level * f < 5:
    #         self.zoom_level *= f
    #
    #         mouse_x = x / self.width
    #         mouse_y = y / self.height
    #
    #         mouse_x_in_world = self.left + mouse_x * self.zoomed_width
    #         mouse_y_in_world = self.bottom + mouse_y * self.zoomed_height
    #
    #         self.zoomed_width *= f
    #         self.zoomed_height *= f
    #
    #         self.left = mouse_x_in_world - mouse_x * self.zoomed_width
    #         self.right = mouse_x_in_world + (1 - mouse_x) * self.zoomed_width
    #         self.bottom = mouse_y_in_world - mouse_y * self.zoomed_height
    #         self.top = mouse_y_in_world + (1 - mouse_y) * self.zoomed_height

    # Zoom based on center of window
    # def on_mouse_scroll(self, x, y, dx, dy):
    #     # Get scale factor
    #     f = ZOOM_OUT_FACTOR if dy > 0 else ZOOM_IN_FACTOR if dy < 0 else 1
    #     # If zoom_level is in the proper range
    #     if .2 < self.zoom_level * f < 5:
    #         self.zoom_level *= f
    #
    #         center_x = self.width / 2
    #         center_y = self.height / 2
    #
    #         mouse_x_in_world = self.left + center_x * self.zoomed_width / self.width
    #         mouse_y_in_world = self.bottom + center_y * self.zoomed_height / self.height
    #
    #         self.zoomed_width *= f
    #         self.zoomed_height *= f
    #
    #         self.left = mouse_x_in_world - center_x * self.zoomed_width / self.width
    #         self.right = mouse_x_in_world + (self.width - center_x) * self.zoomed_width / self.width
    #         self.bottom = mouse_y_in_world - center_y * self.zoomed_height / self.height
    #         self.top = mouse_y_in_world + (self.height - center_y) * self.zoomed_height / self.height
