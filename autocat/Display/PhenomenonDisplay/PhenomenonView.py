import numpy as np
from pyglet.gl import *
from webcolors import name_to_rgb
from ..InteractiveDisplay import InteractiveDisplay


class PhenomenonView(InteractiveDisplay):
    """Display a phenomenon"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hull_line = None
        self.label3.text = 'Type: None'

    def add_lines(self, points, color_string):
        """Update the hull at the forefront of the view"""
        if self.hull_line is not None:
            self.hull_line.delete()
            self.hull_line = None

        if points is not None:
            # points += points[0:2]  # Loop back to the last point
            nb_points = int(len(points) / 2)
            if nb_points >= 2:
                index = []
                for i in range(0, nb_points - 1):
                    index.extend([i, i + 1])
                # v_index += [nb_points]  # Close the loop
                self.hull_line = self.batch.add_indexed(nb_points, gl.GL_LINES, self.forefront, index, ('v2i', points),
                                                        ('c4B', nb_points * (*name_to_rgb(color_string), 255)))

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window if the mouse is above the text"""
        if y >= 50:
            super().on_mouse_scroll(x, y, dx, dy)
