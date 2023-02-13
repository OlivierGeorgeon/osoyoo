from pyglet import gl
from webcolors import name_to_rgb
from pyrr import matrix44
import math
import numpy as np
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_IMPACT, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO
from ...Memory.AllocentricMemory.GridCell import CELL_PHENOMENON, CELL_UNKNOWN, CELL_NO_ECHO

SCALE_LEVEL_1 = 0.8
SCALE_LEVEL_2 = 0.5


class HexagonalCell:
    """A cell in the hexagonal grid"""
    def __init__(self, cell, batch, group1, group2):
        self.cell = cell
        self.batch = batch

        # The level 1 hexagon
        point1 = np.array([cell.radius * SCALE_LEVEL_1, 0, 0])
        self.shape1 = self.create_shape(point1, group1)

        # The level 2 hexagon
        point2 = np.array([cell.radius * SCALE_LEVEL_2, 0, 0])
        self.shape2 = self.create_shape(point2, group2)

        self.update_color()

    def create_shape(self, point, group):
        """Create the hexagonal shape around the center point"""
        points = [point]
        rotation_matrix = matrix44.create_from_z_rotation(math.pi/3)
        for i in range(0, 5):
            point = matrix44.apply_to_vector(rotation_matrix, point)
            points.append(point)
        points += self.cell.point

        points = np.array([p[0:2] for p in points]).flatten().astype("int").tolist()
        return self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                      ('v2i', points), ('c4B', 6 * (*name_to_rgb('white'), 0)))

    def update_color(self):
        """Update the color and opacity of the shapes based on the cell status"""
        status1 = self.cell.status[1]
        color = name_to_rgb('white')
        opacity = 255
        if status1 == CELL_UNKNOWN:
            color = name_to_rgb('grey')
            opacity = 0
        if status1 == EXPERIENCE_PLACE:
            color = name_to_rgb('LightGreen')
        if status1 == EXPERIENCE_BLOCK:
            color = name_to_rgb('red')
        if status1 == EXPERIENCE_IMPACT:
            color = name_to_rgb('red')
        if status1 == EXPERIENCE_FLOOR:
            color = name_to_rgb('black')
        if status1 == EXPERIENCE_ALIGNED_ECHO:
            color = name_to_rgb('orange')
        if status1 == EXPERIENCE_CENTRAL_ECHO:
            color = name_to_rgb('sienna')
        if status1 == CELL_PHENOMENON:
            color = name_to_rgb('yellow')
        # Reset the color of the shape1
        self.shape1.colors[0:24] = 6 * (*color, opacity)

        # Level 2: No echo or focus
        opacity2 = 255
        if self.cell.status[3] == EXPERIENCE_FOCUS:
            color2 = name_to_rgb('fireBrick')
        else:
            if self.cell.status[2] == CELL_NO_ECHO:
                color2 = name_to_rgb('CadetBlue')
            else:
                color2 = name_to_rgb('grey')
                opacity2 = 0
        # Reset the color of the shape2
        self.shape2.colors[0:24] = 6 * (*color2, opacity2)
