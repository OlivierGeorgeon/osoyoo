from pyglet import gl
from webcolors import name_to_rgb
from pyrr import matrix44
import math
import numpy as np
from . import DISPLAY_POOL
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_IMPACT, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_PROMPT, FLOOR_COLORS
from ...Memory.AllocentricMemory.GridCell import CELL_PHENOMENON, CELL_UNKNOWN, CELL_NO_ECHO

SCALE_LEVEL_0 = 2.5  # 3
SCALE_LEVEL_1 = 0.8  # 0.9
SCALE_LEVEL_2 = 0.6  # 0.65
SCALE_LEVEL_3 = 0.35  # 0.4


class CellDisplay:
    """A cell in the hexagonal grid"""
    def __init__(self, cell, batch, groups, clock):
        # Do not store the cell because it may be cloned
        self.batch = batch

        # The level 0 hexagon: Pool cell
        self.shape0 = None
        if DISPLAY_POOL:
            if cell.is_pool():
                point_pool = np.array([cell.radius * SCALE_LEVEL_0, 0, 0])
                rotation_matrix = matrix44.create_from_z_rotation(-math.atan2(math.sqrt(3), -2))
                point_pool = matrix44.apply_to_vector(rotation_matrix, point_pool)
                self.shape0 = self.create_shape(cell.point(), point_pool, groups[0])

        # The level 1 hexagon
        point0 = np.array([cell.radius * SCALE_LEVEL_1, 0, 0])
        self.shape1 = self.create_shape(cell.point(), point0, groups[1])

        # The level 2 hexagon
        point1 = np.array([cell.radius * SCALE_LEVEL_2, 0, 0])
        self.shape2 = self.create_shape(cell.point(), point1, groups[2])

        # The level 3 hexagon
        point2 = np.array([cell.radius * SCALE_LEVEL_3, 0, 0])
        self.shape3 = self.create_shape(cell.point(), point2, groups[3])

        self.update_color(cell, clock)

    def create_shape(self, cell_point, point, group):
        """Create the hexagonal shape around the center point"""
        points = [point]
        rotation_matrix = matrix44.create_from_z_rotation(math.pi/3)
        for i in range(0, 5):
            point = matrix44.apply_to_vector(rotation_matrix, point)
            points.append(point)
        points += cell_point

        points = np.array([p[0:2] for p in points]).flatten().astype(int).tolist()
        return self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                      ('v2i', points), ('c4B', 6 * (*name_to_rgb('white'), 0)))

    def update_color(self, cell, clock):
        """Update the color and opacity of the shapes based on the cell status"""
        # Level 0 Pool
        if self.shape0 is not None:
            color0 = name_to_rgb('royalBlue')
            # if cell.clock_prompt > 0:
            #     color0 = name_to_rgb('MediumOrchid')
            self.shape0.colors[0:24] = 6 * (*color0, 255)

        # Level 1
        color1 = name_to_rgb('white')
        opacity1 = 255
        if cell.status[0] == CELL_UNKNOWN:
            color1 = name_to_rgb('grey')
            opacity1 = 0
        if cell.status[0] == EXPERIENCE_PLACE:
            color1 = name_to_rgb('Lavender')  # name_to_rgb('LightGreen')  # name_to_rgb(FLOOR_COLORS[0])
            opacity1 = int(max(255 * (30 - clock + cell.clock_place) / 30, 0))
        if cell.status[0] == EXPERIENCE_FLOOR:
            if cell.color_index == 0:
                color1 = name_to_rgb('black')
            else:
                color1 = name_to_rgb(FLOOR_COLORS[cell.color_index])
        # Reset the color of the shape0
        self.shape1.colors[0:24] = 6 * (*color1, opacity1)

        # Level 2
        color2 = name_to_rgb('white')
        opacity2 = 255
        if cell.status[1] == CELL_UNKNOWN:
            color2 = name_to_rgb('grey')
            opacity2 = 0
        # if cell.status[1] == EXPERIENCE_PLACE:  # Not used
        #     color2 = name_to_rgb('LightGreen')  # LightGreen
        if cell.status[1] == EXPERIENCE_BLOCK:
            color2 = name_to_rgb('salmon')
            opacity2 = int(max(255 * (10 - clock + cell.clock_interaction) / 10, 0))
        if cell.status[1] == EXPERIENCE_IMPACT:
            color2 = name_to_rgb('salmon')
            opacity2 = int(max(255 * (10 - clock + cell.clock_interaction) / 10, 0))
        # if cell.status[1] == EXPERIENCE_FLOOR:  # Not used
        #     color2 = name_to_rgb('black')
        if cell.status[1] == EXPERIENCE_ALIGNED_ECHO:
            color2 = name_to_rgb('orange')
            opacity2 = int(max(255 * (10 - clock + cell.clock_interaction) / 10, 0))
        if cell.status[1] == EXPERIENCE_CENTRAL_ECHO:
            color2 = name_to_rgb('sienna')
            opacity2 = int(max(255 * (10 - clock + cell.clock_interaction) / 10, 0))
        if cell.status[1] == CELL_PHENOMENON:
            color2 = name_to_rgb('yellow')
        # Reset the color of the shape1
        self.shape2.colors[0:24] = 6 * (*color2, opacity2)

        # Level 3: No echo or focus
        opacity3 = 255
        if cell.status[3] == EXPERIENCE_FOCUS:
            color3 = name_to_rgb('fireBrick')
        elif cell.status[4] == EXPERIENCE_PROMPT:
            color3 = name_to_rgb('Orchid')
        else:
            if cell.status[2] == CELL_NO_ECHO:
                color3 = name_to_rgb('CadetBlue')  # CadetBlue LightGreen
                opacity3 = int(max(255 * (10 - clock + cell.clock_no_echo) / 10, 0))
            else:
                color3 = name_to_rgb('grey')
                opacity3 = 0
        # Reset the color of the shape2
        self.shape3.colors[0:24] = 6 * (*color3, opacity3)

    def delete(self):
        """Delete the hexagon from the view"""
        if self.shape0 is not None:
            self.shape0.delete()
        self.shape1.delete()
        self.shape2.delete()
        self.shape3.delete()
