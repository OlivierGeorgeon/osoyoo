from pyglet import gl
from webcolors import name_to_rgb
from pyrr import matrix44
import math
import numpy as np
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_IMPACT, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_PROMPT
from ...Memory.AllocentricMemory.GridCell import CELL_PHENOMENON, CELL_UNKNOWN, CELL_NO_ECHO

SCALE_LEVEL_0 = 0.9
SCALE_LEVEL_1 = 0.65
SCALE_LEVEL_2 = 0.4


class CellDisplay:
    """A cell in the hexagonal grid"""
    def __init__(self, cell, batch, groups):
        # self.cell = cell Do not store the cell because it may be cloned
        self.batch = batch

        # The level 0 hexagon
        point0 = np.array([cell.radius * SCALE_LEVEL_0, 0, 0])
        self.shape0 = self.create_shape(cell.point, point0, groups[0])

        # The level 1 hexagon
        point1 = np.array([cell.radius * SCALE_LEVEL_1, 0, 0])
        self.shape1 = self.create_shape(cell.point, point1, groups[1])

        # The level 2 hexagon
        point2 = np.array([cell.radius * SCALE_LEVEL_2, 0, 0])
        self.shape2 = self.create_shape(cell.point, point2, groups[2])

        self.update_color(cell.status)

    def create_shape(self, cell_point, point, group):
        """Create the hexagonal shape around the center point"""
        points = [point]
        rotation_matrix = matrix44.create_from_z_rotation(math.pi/3)
        for i in range(0, 5):
            point = matrix44.apply_to_vector(rotation_matrix, point)
            points.append(point)
        points += cell_point

        points = np.array([p[0:2] for p in points]).flatten().astype("int").tolist()
        return self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                      ('v2i', points), ('c4B', 6 * (*name_to_rgb('white'), 0)))

    def update_color(self, status):
        """Update the color and opacity of the shapes based on the cell status"""
        # Level 0
        color0 = name_to_rgb('white')
        opacity0 = 255
        if status[0] == CELL_UNKNOWN:
            color0 = name_to_rgb('grey')
            opacity0 = 0
        if status[0] == EXPERIENCE_PLACE:
            color0 = name_to_rgb('LightGreen')
        if status[0] == EXPERIENCE_FLOOR:
            color0 = name_to_rgb('black')
        # Reset the color of the shape0
        self.shape0.colors[0:24] = 6 * (*color0, opacity0)

        # Level 1
        color1 = name_to_rgb('white')
        opacity1 = 255
        if status[1] == CELL_UNKNOWN:
            color1 = name_to_rgb('grey')
            opacity1 = 0
        if status[1] == EXPERIENCE_PLACE:  # Not used
            color1 = name_to_rgb('LightGreen')
        if status[1] == EXPERIENCE_BLOCK:
            color1 = name_to_rgb('red')
        if status[1] == EXPERIENCE_IMPACT:
            color1 = name_to_rgb('red')
        if status[1] == EXPERIENCE_FLOOR:  # Not used
            color1 = name_to_rgb('black')
        if status[1] == EXPERIENCE_ALIGNED_ECHO:
            color1 = name_to_rgb('orange')
        if status[1] == EXPERIENCE_CENTRAL_ECHO:
            color1 = name_to_rgb('sienna')
        if status[1] == CELL_PHENOMENON:
            color1 = name_to_rgb('yellow')
        # Reset the color of the shape1
        self.shape1.colors[0:24] = 6 * (*color1, opacity1)

        # Level 2: No echo or focus
        opacity2 = 255
        if status[3] == EXPERIENCE_FOCUS:
            color2 = name_to_rgb('fireBrick')
        elif status[3] == EXPERIENCE_PROMPT:
            color2 = name_to_rgb('Orchid')
        else:
            if status[2] == CELL_NO_ECHO:
                color2 = name_to_rgb('CadetBlue')
            else:
                color2 = name_to_rgb('grey')
                opacity2 = 0
        # Reset the color of the shape2
        self.shape2.colors[0:24] = 6 * (*color2, opacity2)

    def delete(self):
        """Delete the hexagon from the view"""
        self.shape0.delete()
        self.shape1.delete()
        self.shape2.delete()
