import pyglet
from pyglet.gl import *
from pyglet.window import key
import math
import numpy
from pyrr import matrix44
from . OsoyooCar import OsoyooCar
from . PointOfInterest import PointOfInterest, POINT_PHENOMENON
from .. Model.Memories.MemoryV1 import MemoryV1
from .. Misc.Utils import interactionList_to_pyglet

import time
ZOOM_IN_FACTOR = 1.2


class EgocentricView(pyglet.window.Window):
    def __init__(self, width=400, height=400, shapesList = None, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)  # Will be used to manage the overlapping of shapes
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.zoom_level = 1

        self.robot = OsoyooCar(self.batch, self.background)

        self.total_displacement_matrix = matrix44.create_identity()
        self.azimuth = 0
        self.shapesList = shapesList
        self.points_of_interest = []

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.window = None

        # Room to write some text
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)
        self.label.color = (0, 0, 0, 255)

    def set_ShapesList(self, s):
        # Not used
        self.shapesList = s

    def extract_and_convert_interactions(self, memory):
        """ Retrieve the interactions from memory and create the shapes in the batch """
        self.shapesList = interactionList_to_pyglet(memory.interactions, self.batch)

    def on_draw(self):
        """ Drawing the window """
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
        """ Adjusting the viewport when resizing the window """
        # Always display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def on_mouse_press(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        window_press_x = (x - self.width / 2) * self.zoom_level * 2
        window_press_y = (y - self.height / 2) * self.zoom_level * 2
        # Polar coordinates from the window center
        r = numpy.hypot(window_press_x, window_press_y)
        theta_window = math.atan2(window_press_y, window_press_x)
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
        # Mark any nearby point of interest
        for p in self.points_of_interest:
            if p.is_near(self.mouse_press_x, self.mouse_press_y):
                p.set_color("red")
            else:
                p.set_color()
        # return mouse_press_x, mouse_press_y, mouse_press_angle

    def on_key_press(self, symbol, modifiers):
        """ Deleting points of interest, inserting a phenomenon"""
        if symbol == key.DELETE:
            for p in self.points_of_interest:
                if p.is_selected:
                    p.delete()
                    self.points_of_interest.remove(p)
        if symbol == key.INSERT:
            print("insert phenomenon")
            self.add_point_of_interest(self.mouse_press_x, self.mouse_press_y, POINT_PHENOMENON)

    def add_point_of_interest(self, x, y, point_type):
        """ Adding a point of interest to the view """
        point_of_interest = PointOfInterest(x, y, self.batch, self.foreground, point_type)
        self.points_of_interest.append(point_of_interest)

    def displace(self, displacement_matrix):
        """ Moving all the points of interest by the displacement matrix """
        for p in self.points_of_interest:
            p.displace(displacement_matrix)


# Displaying EgoMemoryWindowNew with phenomena in MemoryV1
# py -m stage_titouan.Views.EgoMemoryWindowNew
if __name__ == "__main__":
    emw = EgocentricView()
    emw.robot.rotate_head(-45)

    # Add interactions to memory
    mem = MemoryV1()
    mem.add((3, 0, 0, 0, 0, 0))  # Line
    mem.add((0, 0, 0, 1, 300, -300))  # Echo

    # Retrieve interactions from memory and construct the shapes in the window
    emw.extract_and_convert_interactions(mem)

    pyglet.app.run()