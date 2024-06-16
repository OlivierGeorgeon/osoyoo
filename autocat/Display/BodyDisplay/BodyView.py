import numpy as np
import pyglet
from pyglet.gl import *
import math
from ..InteractiveDisplay import InteractiveDisplay
from ...Memory.BodyMemory import DOPAMINE, SEROTONIN, NORADRENALINE


class BodyView(InteractiveDisplay):
    """Display the information in body memory"""
    def __init__(self, workspace, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.set_caption("Body Memory")
        self.set_minimum_size(150, 150)

        self.workspace = workspace

        # Initialize OpenGL parameters
        glClearColor(1.0, 235.0/256., 205.0/256., 1.0)
        self.zoom_level = 2.6

        # Define the text area at the bottom of the view
        self.label_DA = pyglet.text.Label('DA: ', font_name='Verdana', font_size=10, x=10, y=70)
        self.label_DA.color = (0, 0, 0, 255)
        self.label_DA.batch = self.label_batch
        self.label_5HT = pyglet.text.Label('5-HT: ', font_name='Verdana', font_size=10, x=100, y=70)
        self.label_5HT.color = (0, 0, 0, 255)
        self.label_5HT.batch = self.label_batch
        self.label_NA = pyglet.text.Label('NA: ', font_name='Verdana', font_size=10, x=190, y=70)
        self.label_NA.color = (0, 0, 0, 255)
        self.label_NA.batch = self.label_batch

        self.label2.text = 'Azimuth: 90'
        self.label3.text = 'Speed: (0, 0)'

    # def on_draw(self):
    #     """ Drawing the view """
    #     glClear(GL_COLOR_BUFFER_BIT)
    #     glLoadIdentity()
    #
    #     # The transformations are stacked, and applied in reversed order to the vertices
    #
    #     # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
    #     # glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
    #     #         self.height * self.zoom_level, 1, -1)
    #     glTranslatef(*self.robot_translate)
    #     glOrtho(self.left, self.right, self.bottom, self.top, 1, -1)
    #
    #     # Stack the rotation of the robot body
    #     # glRotatef(90 - self.workspace.memory.body_memory.body_azimuth(), 0.0, 0.0, 1.0)
    #     glTranslatef(*self.robot_translate)
    #     glRotatef(self.robot_rotate, 0.0, 0.0, 1.0)
    #     # Draw compass points
    #     # self.batch.draw()
    #     # Draw the robot
    #     self.egocentric_batch.draw()
    #
    #     # Reset the projection to Identity to cancel the projection of the text
    #     glLoadIdentity()
    #     # Stack the projection of the text
    #     glOrtho(0, self.width, 0, self.height, -1, 1)
    #     # Draw the text in the bottom left corner
    #     self.label_batch.draw()

    # def on_mouse_press(self, x, y, button, modifiers):
    #     """ Computing the position of the mouse click relative to the robot in mm and degrees """
    #     # Rotate the click point by the inverse rotation of the robot
    #     v = self.workspace.memory.body_memory.body_quaternion.inverse * self.mouse_coordinates_to_point(x, y)
    #     t = round(math.degrees(math.atan2(v[1], v[0])))
    #     self.label3.text = f"Click: x: {round(v[0])},  y: {round(v[1])}, angle: {t}°"

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        if y > 90:
            # Zoom the view
            super().on_mouse_scroll(x, y, dx, dy)
        elif y > 60:
            # The neurotransmitter levels
            if x < 100:
                self.workspace.memory.body_memory.neurotransmitters[DOPAMINE] += int(np.sign(dy))
            elif x < 190:
                self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] += int(np.sign(dy))
            else:
                self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] += int(np.sign(dy))
        else:
            # The energy levels
            if x < 150:
                self.workspace.memory.body_memory.energy += int(np.sign(dy))
            else:
                self.workspace.memory.body_memory.excitation += int(np.sign(dy))
