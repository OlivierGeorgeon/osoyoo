import numpy as np
import pyglet
from pyglet.gl import glClearColor
from ..InteractiveDisplay import InteractiveDisplay
from ...Memory.BodyMemory import DOPAMINE, SEROTONIN, NORADRENALINE


class BodyView(InteractiveDisplay):
    """Display the information in body memory"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.workspace = workspace

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

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window or manually updating the neurotransmitter levels"""
        if y > 90:
            # Zoom the view
            super().on_mouse_scroll(x, y, dx, dy)
        # elif y > 60:
        #     # The neurotransmitter levels
        #     if x < 100:
        #         self.workspace.memory.body_memory.neurotransmitters[DOPAMINE] += int(np.sign(dy))
        #     elif x < 190:
        #         self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] += int(np.sign(dy))
        #     else:
        #         self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] += int(np.sign(dy))
        # else:
        #     # The energy levels
        #     if x < 150:
        #         self.workspace.memory.body_memory.energy += int(np.sign(dy))
        #     else:
        #         self.workspace.memory.body_memory.excitation += int(np.sign(dy))
