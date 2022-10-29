from pyglet import gl
from webcolors import name_to_rgb
import math
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_IMPACT, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO
from ...Memory.AllocentricMemory.GridCell import CELL_PHENOMENON


class HexagonalCell:
    """A cell in the hexagonal grid"""
    def __init__(self, cell_x, cell_y, batch, group, radius, status, scale):
        # self.x, self.y = x, y
        # self.batch = batch
        # self.group = group
        # self.radius = radius * scale
        # self.status = status

        # The position of the center in the allocentric view
        height = math.sqrt((2 * radius) ** 2 - radius ** 2)
        if cell_y % 2 == 0:
            x = cell_x * 3 * radius
            y = height * (cell_y / 2)
        else:
            x = (1.5 * radius) + cell_x * 3 * radius
            y = (height / 2) + (cell_y - 1) / 2 * height

        # The position of the points in the allocentric view
        points = []
        theta = 0
        for i in range(0, 12, 2):
            points.append((x + math.cos(theta) * radius * scale))  # int
            points.append((y + math.sin(theta) * radius * scale))  # int
            theta += math.pi/3

        self.shape = batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                       ('v2f', points), ('c4B', 6 * (*name_to_rgb('white'), 128)))

        self.set_color(status)

    def set_color(self, status):
        """ Set the color from the status"""
        color = name_to_rgb('white')
        if status == 'Free':
            color = name_to_rgb('LightGreen')
        if status == EXPERIENCE_PLACE:
            color = name_to_rgb('LightGreen')
        if status == 'Occupied':
            color = name_to_rgb('slateBlue')
        if status == EXPERIENCE_BLOCK:
            color = name_to_rgb('red')
        if status == EXPERIENCE_IMPACT:
            color = name_to_rgb('red')
        if status == EXPERIENCE_FLOOR:
            color = name_to_rgb('black')
        if status == EXPERIENCE_ALIGNED_ECHO:
            color = name_to_rgb('orange')
        if status == EXPERIENCE_CENTRAL_ECHO:
            color = name_to_rgb('sienna')
        if status == EXPERIENCE_FOCUS:
            color = name_to_rgb('fireBrick')
        if status == CELL_PHENOMENON:
            color = name_to_rgb('yellow')
        # Reset the color of the shape
        self.shape.colors[0:24] = 6 * (*color, 128)
