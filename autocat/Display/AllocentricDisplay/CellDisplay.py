from pyglet import gl
from webcolors import name_to_rgb
from pyrr import matrix44
import math
import numpy as np
from . import DISPLAY_POOL
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_IMPACT, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_PROMPT, \
    EXPERIENCE_ROBOT, FLOOR_COLORS
from ...Memory.AllocentricMemory.AllocentricMemory import CELL_UNKNOWN, CELL_NO_ECHO
from ...Memory import CELL_RADIUS
from ...Memory.AllocentricMemory import STATUS_FLOOR, STATUS_ECHO, STATUS_2, STATUS_3, STATUS_4, COLOR_INDEX, \
    CLOCK_INTERACTION, CLOCK_NO_ECHO, CLOCK_PLACE, POINT_X, POINT_Y, IS_POOL, PLACE_CELL_ID
from ...Memory import EXPERIENCE_DURABILITY, PLACE_GRID_DURABILITY

SCALE_LEVEL_0 = 2.5  # 3
SCALE_LEVEL_1 = 0.8  # 0.9
SCALE_LEVEL_2 = 0.6  # 0.65
SCALE_LEVEL_3 = 0.35  # 0.4


class CellDisplay:
    """A cell in the hexagonal grid"""

    # Initialize the unit hexagon to create cells
    unit_hexagon = np.empty((6, 3), dtype=float)
    unit_hexagon[0, :] = [1, 0, 0]
    rotation_matrix = matrix44.create_from_z_rotation(math.pi / 3)
    for i in range(1, 6):
        unit_hexagon[i, :] = matrix44.apply_to_vector(rotation_matrix, unit_hexagon[i-1, :])
    unit_hexagon = unit_hexagon[:, 0:2]

    # Initialize the pool hexagon
    pool_hexagon = np.empty((6, 3), dtype=float)
    rotation_matrix = matrix44.create_from_z_rotation(-math.atan2(math.sqrt(3), -2))
    pool_hexagon[0, :] = matrix44.apply_to_vector(rotation_matrix, [CELL_RADIUS * SCALE_LEVEL_0, 0, 0])
    rotation_matrix = matrix44.create_from_z_rotation(math.pi / 3)
    for i in range(1, 6):
        pool_hexagon[i, :] = matrix44.apply_to_vector(rotation_matrix, pool_hexagon[i-1, :])
    pool_hexagon = pool_hexagon[:, 0:2]

    def __init__(self, cell, batch, groups, clock):
        # Do not store the cell because it may be cloned
        self.batch = batch

        # The level 0 hexagon: Pool cell
        self.shape0 = None
        if DISPLAY_POOL and cell[IS_POOL]:
            hexagon = CellDisplay.pool_hexagon + cell[POINT_X: POINT_Y+1]
            points = hexagon.flatten().astype(int).tolist()
            self.shape0 = self.batch.add_indexed(6, gl.GL_TRIANGLES, groups[0], [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                                 ('v2i', points), ('c4B', (*name_to_rgb('white'), 0) * 6))
        # The level 1 hexagon
        self.shape1 = self.create_shape(cell[POINT_X: POINT_Y+1], CELL_RADIUS * SCALE_LEVEL_1, groups[1])

        # The level 2 hexagon
        self.shape2 = self.create_shape(cell[POINT_X: POINT_Y+1], CELL_RADIUS * SCALE_LEVEL_2, groups[2])

        # The level 3 hexagon
        self.shape3 = self.create_shape(cell[POINT_X: POINT_Y+1], CELL_RADIUS * SCALE_LEVEL_3, groups[3])

        self.update_color(cell, clock)

    def create_shape(self, cell_point, radius, group):
        """Create the hexagonal shape at the cell point"""
        hexagon = CellDisplay.unit_hexagon * radius + cell_point
        points = hexagon.flatten().astype(int).tolist()
        return self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                      ('v2i', points), ('c4B', (*name_to_rgb('white'), 0) * 6))

    def update_color(self, cell, clock):
        """Update the color and opacity of the shapes based on the cell status"""
        # Level 0 Pool
        if self.shape0 is not None:
            color0 = name_to_rgb('royalBlue')
            self.shape0.colors[:] = 6 * (*color0, 255)

        # Level 1
        color1 = name_to_rgb('blue')
        opacity1 = 255
        if cell[STATUS_FLOOR] == CELL_UNKNOWN:
            color1 = name_to_rgb('grey')
            opacity1 = 0
        if cell[STATUS_FLOOR] == EXPERIENCE_PLACE:
            color1 = name_to_rgb('Lavender')  # name_to_rgb('LightGreen')  # name_to_rgb(FLOOR_COLORS[0])
            opacity1 = int(max(255 * (PLACE_GRID_DURABILITY - clock + cell[CLOCK_PLACE]) / PLACE_GRID_DURABILITY, 0))
        if cell[STATUS_FLOOR] == EXPERIENCE_FLOOR:
            if cell[COLOR_INDEX] == 0:
                color1 = name_to_rgb('black')
            else:
                color1 = name_to_rgb(FLOOR_COLORS[cell[COLOR_INDEX]])
        # Reset the color of the shape0
        self.shape1.colors[0:24] = 6 * (*color1, opacity1)

        # Level 2
        color2 = name_to_rgb('white')
        opacity2 = 255
        if cell[STATUS_ECHO] == CELL_UNKNOWN:
            color2 = name_to_rgb('grey')
            opacity2 = 0
        if cell[STATUS_ECHO] == EXPERIENCE_BLOCK:
            color2 = name_to_rgb('salmon')
            opacity2 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_INTERACTION]) / EXPERIENCE_DURABILITY,
                               0))
        if cell[STATUS_ECHO] == EXPERIENCE_IMPACT:
            color2 = name_to_rgb('salmon')
            opacity2 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_INTERACTION]) / EXPERIENCE_DURABILITY,
                               0))
        if cell[STATUS_ECHO] == EXPERIENCE_ROBOT:
            color2 = name_to_rgb('lightSteelBlue')
            opacity2 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_INTERACTION]) / EXPERIENCE_DURABILITY,
                               0))
        if cell[STATUS_ECHO] == EXPERIENCE_ALIGNED_ECHO:
            color2 = name_to_rgb('orange')
            opacity2 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_INTERACTION]) / EXPERIENCE_DURABILITY,
                               0))
        if cell[STATUS_ECHO] == EXPERIENCE_CENTRAL_ECHO:
            color2 = name_to_rgb('sienna')
            opacity2 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_INTERACTION]) / EXPERIENCE_DURABILITY,
                               0))
        if cell[PLACE_CELL_ID] > 0:
            color2 = name_to_rgb('yellow')
            opacity2 = 255
        # Reset the color of the shape1
        self.shape2.colors[0:24] = 6 * (*color2, opacity2)

        # Level 3: Focus or Prompt or No Echo
        opacity3 = 255
        if cell[STATUS_3] == EXPERIENCE_FOCUS:
            color3 = name_to_rgb('fireBrick')
        elif cell[STATUS_4] == EXPERIENCE_PROMPT:
            color3 = name_to_rgb('Orchid')
        else:
            if cell[STATUS_2] == CELL_NO_ECHO:
                color3 = name_to_rgb('CadetBlue')  # CadetBlue LightGreen
                opacity3 = int(max(255 * (EXPERIENCE_DURABILITY - clock + cell[CLOCK_NO_ECHO]) / EXPERIENCE_DURABILITY,
                                   0))
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
