from pyglet import gl
from webcolors import name_to_rgb
import math
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_FOCUS, EXPERIENCE_SHOCK, EXPERIENCE_PLACE, EXPERIENCE_CENTRAL_ECHO


class Cell:
    """A cell in the hexagonal grid"""
    def __init__(self, x, y, batch, group, radius, status):
        self.x, self.y = x, y
        self.batch = batch
        self.group = group
        self.radius = radius * 0.8
        self.status = status

        points = []
        theta = 0
        for i in range(0, 12, 2):
            points.append(int(x + math.cos(theta) * self.radius))
            points.append(int(y + math.sin(theta) * self.radius))
            theta += math.pi/3

        self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                                            ('v2i', points), ('c4B', 6 * (*name_to_rgb('white'), 128)))

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
        if status == EXPERIENCE_SHOCK:
            color = name_to_rgb('red')
        if status == EXPERIENCE_FLOOR:
            color = name_to_rgb('black')
        if status == EXPERIENCE_ALIGNED_ECHO:
            color = name_to_rgb('orange')
        if status == EXPERIENCE_CENTRAL_ECHO:
            color = name_to_rgb('sienna')
        if status == EXPERIENCE_FOCUS:
            color = name_to_rgb('fireBrick')
        self.shape.colors[0:24] = 6 * (*color, 128)
