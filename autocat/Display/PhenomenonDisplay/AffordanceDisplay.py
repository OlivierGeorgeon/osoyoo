import numpy as np
import pyglet
from ..EgocentricDisplay.PointOfInterest import PointOfInterest
from webcolors import name_to_rgb


class AffordanceDisplay(PointOfInterest):
    """Display an affordance: the experience plus the cone"""
    def __init__(self, x, y, batch, group, background_group, point_type, clock, durability=10):
        super().__init__(x, y, batch, group, point_type, clock, durability)
        self.background_group = background_group
        self.cone = None

    def add_cone(self, points, color_string):
        """Add a plain polygon to the background of the view"""
        nb_points = int(len(points))
        # Convert the numpy array of points into a 2D flat list of integers
        points = np.array([p[0:2] for p in points]).flatten().astype("int").tolist()
        if 3 <= nb_points <= 6:
            nb_index = (nb_points - 2) * 3
            v_index = [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5, 0, 6, 7, 0, 7, 8][0:nb_index]
            color = name_to_rgb(color_string)
            opacity = 64
            self.cone = self.batch.add_indexed(nb_points, pyglet.gl.GL_TRIANGLES, self.background_group, v_index,
                                               ('v2i', points), ('c4B', nb_points * (*color, opacity)))

    def delete(self):
        """Delete the shapes of this affordance display"""
        super().delete()
        if self.cone is not None:
            self.cone.delete()
