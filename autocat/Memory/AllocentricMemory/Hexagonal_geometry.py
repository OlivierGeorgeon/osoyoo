########################################################################################
# The math used to handle the hexagonal grid
# https://www.redblobgames.com/grids/hexagons/
# Orientation: flat_top.
# Coordinate system: Horizontal layout with odd row offset
#                    (0,0) center. Positive rows upward.
# Pooling with aperture of 7
# https://ieeexplore.ieee.org/document/8853238
########################################################################################

import math
import numpy as np

CELL_RADIUS = 50  # (mm) Diameter of the outer circle


def get_neighbors(i, j):
    """Return a dictionary of the coordinates of the six neighboring cells"""
    neighbors = {}
    for d in range(6):
        neighbors[d] = get_neighbor_in_direction(i, j, d)
    return neighbors


def get_neighbor_in_direction(i, j, direction):
    """Return the cell coordinate of the neighboring cell in the given direction
    Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
    """
    if j % 2 == 0:
        # Even lines
        di, dj = [(0, 2), (0, 1), (0, -1), (0, -2), (-1, -1), (-1, 1)][direction]
    else:
        # Odd lines
        di, dj = [(0, 2), (1, 1), (1, -1), (0, -2), (0, -1), (0, 1)][direction]
    return i + di, j + dj


def cell_to_point(i, j, radius=CELL_RADIUS):
    """Convert the cell coordinates into allocentric coordinates"""
    cell_height = math.sqrt((2 * radius) ** 2 - radius ** 2)
    if j % 2 == 0:
        x = i * 3 * radius
        y = cell_height * (j / 2)
    else:
        x = (1.5 * radius) + i * 3 * radius
        y = (cell_height / 2) + (j - 1) / 2 * cell_height
    return np.array([x, y, 0], dtype=int)


def point_to_cell(point, radius=CELL_RADIUS):
    """Convert an allocentric position to cell coordinates."""
    # print(point)
    pos_x, pos_y = point[0], point[1]
    # radius = self.cell_radius
    mini_radius = math.sqrt(radius ** 2 - (radius / 2) ** 2)
    tmp_cell_x = 0  # self.width // 2  # The offset x
    tmp_cell_y = 0  # self.height // 2  # The offset y
    tmp_cell_x_center = 0
    tmp_cell_y_center = 0
    # Do the regular part of translation :
    # to go to the next cell on the right/left you move by 3*radius on the x axis.
    x_sign = 1
    if pos_x < 0:
        x_sign = -1
    y_sign = 1
    if pos_y < 0:
        y_sign = -1
    while abs(pos_x) >= abs(3 * radius):
        tmp_cell_x += x_sign
        pos_x -= (3 * radius) * x_sign
        tmp_cell_x_center += (3 * radius) * x_sign
    # To move to the cell on the top/bottom you move by 2*mini_radius on the y axis.
    while abs(pos_y) >= abs(2 * mini_radius):
        tmp_cell_y += 2 * y_sign
        pos_y -= 2 * mini_radius * y_sign
        tmp_cell_y_center += 2 * mini_radius * y_sign
    # Elimination pour trouver dans quel voisin de la cellule courante on est
    distance = math.sqrt(pos_x ** 2 + pos_y ** 2)
    if distance <= mini_radius:  # On est forcement dans la bonne pos
        return tmp_cell_x, tmp_cell_y
    if distance <= radius:
        "determiner la ligne qui risque d'etre traversée, et si on a passé la ligne ou non"
    if abs(pos_x) >= 2.5 * radius:
        "on est forcément dans g hgg bgg ou d hdd bdd"
        if abs(pos_y) >= mini_radius:
            "on est forcement dans hgg bgg hdd bdd"
            return tmp_cell_x + x_sign, tmp_cell_y + 2 * y_sign
        else:
            "on est dans g ou d"
            return tmp_cell_x + x_sign, tmp_cell_y

    if abs(pos_x) >= 2 * radius:
        "on est dans hgg g bgg hg bg / hdd d bdd hd bd "
        if abs(pos_y) >= mini_radius:
            "on est dans hgg-hg  bgg-bg  hdd-hd bd-bdd"
            # On trouve l'équation de la ligne de démarcation
            x_depart = 2.5 * radius
            y_depart = mini_radius

            x_fin = 2 * radius
            y_fin = 2 * mini_radius

            slope = (y_fin - y_depart) / (x_fin - x_depart)
            offset = y_depart - (slope * x_depart)

            y_ref = abs(pos_x) * slope + offset

            if abs(pos_y) <= abs(y_ref):
                # on est dans hg hd bg bd
                return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
            else:
                "on est dans hgg bgg hdd bdd"
                return tmp_cell_x + x_sign, tmp_cell_y + 2 * y_sign
            # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente descendante
            # il faut donc juste regarder si le y du point est inférieur ou supérieur au
            # y correspondant au x sur l'equation de droite

        else:
            "on est dans hd ou d (ou equivalent)"
            # On trouve l'équation de la ligne de démarcation
            x_depart = 2.5 * radius
            y_depart = mini_radius

            x_fin = 2 * radius
            y_fin = 0

            slope = (y_fin - y_depart) / (x_fin - x_depart)
            offset = y_depart - (slope * x_depart)

            y_ref = abs(pos_x) * slope + offset

            # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente ascendante
            # il faut donc juste regarder si le y du point est inférieur ou supérieur au
            # y correspondant au x sur l'equation de droite
            if abs(pos_y) >= abs(y_ref):
                "on est dans hd"
                return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
            else:
                "on est dans d"
                return tmp_cell_x + x_sign, tmp_cell_y

    if radius < abs(pos_x) < 2 * radius:
        "on est dans hd"
        return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
    if radius / 2 < abs(pos_x) <= 2 * radius:
        # on est dans c, h ou hd
        x1 = radius
        y1 = 0

        x2 = radius / 2
        y2 = mini_radius

        x3 = radius
        y3 = 2 * mini_radius

        slope1 = (y1 - y2) / (x1 - x2)
        offset1 = y2 - (slope1 * x2)
        y_ref1 = slope1 * pos_x + offset1

        slope2 = (y3 - y2) / (x3 - x2)
        offset2 = y2 - (slope2 * x2)
        y_ref2 = slope2 * pos_x + offset2

        if y_ref1 <= abs(pos_y) <= y_ref2:
            # on est dans hd
            return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
    if abs(pos_y) > mini_radius:
        return tmp_cell_x, tmp_cell_y + y_sign * 2
    else:
        return tmp_cell_x, tmp_cell_y


def find_coordinates_corner(cell_x, cell_y, x_sign, y_sign):
    """aaaaaaaaa"""
    f_x, f_y = 0, 0
    y_even = cell_y % 2 == 0
    if y_even:
        if x_sign > 0:
            f_x = cell_x
        else:
            f_x = cell_x - 1
    else:
        if x_sign > 0:
            f_x = cell_x + 1
        else:
            f_x = cell_x
    if y_sign > 0:
        f_y = cell_y + 1
    else:
        f_y = cell_y - 1

    return f_x, f_y
