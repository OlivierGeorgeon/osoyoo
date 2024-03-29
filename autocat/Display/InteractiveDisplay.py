import numpy as np
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
        super().__init__(width, height, *args, **kwargs)
        self.zoom_level = 1.0
        self.left = 0
        self.right = width
        self.bottom = 0
        self.top = height
        self.zoomed_width = width
        self.zoomed_height = height
        self.total_dx = 0
        self.total_dy = 0

        # Initialize OpenGL parameters
        # https://www.w3schools.com/cssref/css_colors.asp
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.forefront = pyglet.graphics.OrderedGroup(5)
        self.screen_scale = screen_scale()

    def init_gl(self, width, height):
        # Set antialiasing
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Set alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set viewport
        glViewport(0, 0, width, height)


    def mouse_coordinates_to_point(self, x, y):
        """ Return the point in world scale from mouse x and y """
        adjusted_x = x - self.total_dx
        adjusted_y = y - self.total_dy

        point_x = (adjusted_x - self.width / 2) * self.zoom_level * 2
        point_y = (adjusted_y - self.height / 2) * self.zoom_level * 2

        return Vector3([point_x, point_y, 0], dtype=int)

    def on_resize(self, width, height):
        self.width = width
        self.height = height

             # prise en compte du drag dx/dy
        adjusted_width = width + self.total_dx
        adjusted_height = height + self.total_dy

            # nouveau calcul coins de fenetre
        self.left = (-adjusted_width / 2 - self.total_dx) * self.zoom_level
        self.right = (adjusted_width / 2 - self.total_dx) * self.zoom_level
        self.bottom = (-adjusted_height / 2 - self.total_dy) * self.zoom_level
        self.top = (adjusted_height / 2 - self.total_dy) * self.zoom_level

        # Initialize OpenGL context
        self.init_gl(adjusted_width, adjusted_height)


        #variable pour le centre de l'ecran, 0.5 pour chaque moitié d'axe
        mouse_x = 0.5
        mouse_y = 0.5

        #calcul des coordonnées
        mouse_x_in_world = self.left + mouse_x * self.zoomed_width
        mouse_y_in_world = self.bottom + mouse_y * self.zoomed_height

        #nouvelles dimensions de la fenetre en fonction du zoom
        self.zoomed_width = width * self.zoom_level
        self.zoomed_height = height * self.zoom_level

        #recalcul de LRBT
        self.left = mouse_x_in_world - mouse_x * self.zoomed_width
        self.right = mouse_x_in_world + (1 - mouse_x) * self.zoomed_width
        self.bottom = mouse_y_in_world - mouse_y * self.zoomed_height
        self.top = mouse_y_in_world + (1 - mouse_y) * self.zoomed_height

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.total_dx += dx
        self.total_dy += dy

        self.left = (-self.width / 2 - self.total_dx) * self.zoom_level
        self.right = (self.width / 2 - self.total_dx) * self.zoom_level
        self.bottom = (-self.height / 2 - self.total_dy) * self.zoom_level
        self.top = (self.height / 2 - self.total_dy) * self.zoom_level


            #scroll based on mouse position
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


            #scroll based on center of window
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


        #scroll based on center of robot
    def on_mouse_scroll(self, x, y, dx, dy):
        # Get scale factor
        f = ZOOM_OUT_FACTOR if dy > 0 else ZOOM_IN_FACTOR if dy < 0 else 1

        if .2 < self.zoom_level * f < 5:
            self.zoom_level *= f

            self.zoomed_width *= f
            self.zoomed_height *= f

            self.left *= f
            self.right *= f
            self.bottom *= f
            self.top *= f


