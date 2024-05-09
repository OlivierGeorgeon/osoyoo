########################################################################################
# The math used to handle the hexagonal grid
# https://www.redblobgames.com/grids/hexagons/
# Orientation: flat_top.
# Coordinate system: Axial
# Pooling with aperture of 7
# https://ieeexplore.ieee.org/document/8853238
########################################################################################


# def most_interesting_pool(self, clock):
#     """Return the coordinates of the cell that has the most interesting pool value"""
#     interests = []
#     coords = []
#
#     # for n in range(-2, 2):
#     #     for m in range(-2, 2):
#     # 3 tours counterclockwise:
#     visit = [(2, 0), (-1, 4), (-2, -4), (2, -2), (0, 4), (-2, -2), (2, -4), (1, 4), (-2, 0), (1, -4), (2, 4), (-2, 2),
#              (0, -4), (2, 2), (-2, 4), (-1, -4)]
#     visit = [(2, 0), (-1, 4), (-2, -4), (2, -2), (0, 4), (-2, -2), (2, -4), (1, 4), (-2, 0), (1, -4), (2, 4), (-2, 2),
#              (0, -4), (2, 2), (-2, 4), (-1, -4)]
#     for i in visit:
#         i_even = 3 * i[0] + i[1]
#         j_even = -2 * i[0] + 4 * i[1]
#         coords.append([i_even, j_even])
#         interests.append(self.pool_interest(i_even, j_even, clock))
#         # i_odd = i_even - 2
#         # j_odd = j_even + 1
#         # cells.append([i_odd, j_odd])
#         # interests.append(self.pool_interest(i_odd, j_odd, clock))
#     max_interest = max(interests)
#     coord = coords[interests.index(max_interest)]
#     # Update the prompt
#     if self.prompt_i is not None:
#         self.grid[self.prompt_i][self.prompt_j][STATUS_3] = CELL_UNKNOWN
#     self.prompt_i, self.prompt_j = coord[0], coord[1]
#     self.grid[self.prompt_i][self.prompt_j][STATUS_3] = EXPERIENCE_PROMPT
#     self.grid[self.prompt_i][self.prompt_j][CLOCK_PROMPT] = clock
#     print("Most interesting pool:", coord, "with interest", max_interest)
#     return self.prompt_i, self.prompt_j  # TODO use that
#     # return self.grid[self.prompt_i][self.prompt_j].point()
#
# def pool_interest(self, i, j, clock):
#     """Return the sum of interest of neighbors plus this cell"""
#     if (self.min_i + 1 <= i <= self.max_i - 1) and (self.min_j + 1 <= j <= self.max_j - 1):
#         interest = self.grid[i][j].interest_value(clock)
#         for n in get_neighbors(i, j).values():
#             interest_value = 0
#             # Interesting if not visited
#             if self.grid[i][j][STATUS_0] == CELL_UNKNOWN:
#                 interest_value = 1
#             # Not interesting if already prompted
#             if self.grid[i][j][CLOCK_PROMPT] > 0:
#                 interest_value = -10
#             # Very interesting if colored
#             # Not working because stop on the cell and don't change the clock_place
#             # if self.color_index is not None and self.color_index > 0 and clock - self.clock_place > 5:
#             #     interest_value = 10
#             interest += interest_value
#         return interest
#     else:
#         # If not in the grid
#         return -20


# def get_neighbors(i, j):
#     """Return a dictionary of the coordinates of the six neighboring cells"""
#     neighbors = {}
#     for d in range(6):
#         neighbors[d] = get_neighbor_in_direction(i, j, d)
#     return neighbors
#
#
# def get_neighbor_in_direction(i, j, direction):
#     """Return the cell coordinate of the neighboring cell in the given direction
#     Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
#     """
#     if j % 2 == 0:
#         # Even lines
#         di, dj = [(0, 2), (0, 1), (0, -1), (0, -2), (-1, -1), (-1, 1)][direction]
#     else:
#         # Odd lines
#         di, dj = [(0, 2), (1, 1), (1, -1), (0, -2), (0, -1), (0, 1)][direction]
#     return i + di, j + dj
#
#
# def pool_neighbors(i, j):
#     """Return the pool cells neighboring this cell"""
#     if j % 2 == 0:
#         # Even lines
#         neighbors = np.array([[1, -1], [1, 4], [-1, 5], [-2, 1], [-1, -4], [0, -5]])
#     else:
#         # Odd lines
#         # relative_neighbors = np.array([[3, -2], [2, 3], [1, 4], [0, 0], [0, -5], [2, -6]])
#         neighbors = np.array([[2, -1], [1, 4], [0, 5], [-1, 1], [-1, -4], [1, -5]])
#     neighbors += np.array([i, j])
#     return neighbors


# def cell_to_point_offset(i, j, radius=CELL_RADIUS):
#     """Convert the cell coordinates into allocentric coordinates"""
#     cell_height = np.sqrt((2 * radius) ** 2 - radius ** 2)
#     x = np.where(j % 2 == 0, i * 3 * radius, (1.5 * radius) + i * 3 * radius)
#     y = np.where(j % 2 == 0, cell_height * (j / 2), (cell_height / 2) + (j - 1) / 2 * cell_height)
#     return np.transpose(np.array([x, y]), axes=(1, 2, 0))


# def is_pool_offset(i, j):
#     """True if this cell is used for pooling with aperture 7"""
#     # https://ieeexplore.ieee.org/document/8853238
#     # even:
#     # i = 3n + m   -4*3n -4m -2n +4m = -14n
#     # j = -2n + 4m
#     # odd: i = 3n + m -2, j = -2n + 4m + 1
#     pool_even = (-4 * i + j) % 14 == 0
#     pool_odd = (-4 * i + j - 9) % 14 == 0
#     return np.logical_or(pool_even, pool_odd)
#
#
# def point_to_cell_offset(point, radius=CELL_RADIUS):
#     """Convert an allocentric position to cell coordinates."""
#     # print(point)
#     pos_x, pos_y = point[0], point[1]
#     # radius = self.cell_radius
#     mini_radius = math.sqrt(radius ** 2 - (radius / 2) ** 2)
#     tmp_cell_x = 0  # self.width // 2  # The offset x
#     tmp_cell_y = 0  # self.height // 2  # The offset y
#     tmp_cell_x_center = 0
#     tmp_cell_y_center = 0
#     # Do the regular part of translation :
#     # to go to the next cell on the right/left you move by 3*radius on the x axis.
#
#     x_sign = 1
#     if pos_x < 0:
#         x_sign = -1
#     y_sign = 1
#     if pos_y < 0:
#         y_sign = -1
#     while abs(pos_x) >= abs(3 * radius):
#         tmp_cell_x += x_sign
#         pos_x -= (3 * radius) * x_sign
#         tmp_cell_x_center += (3 * radius) * x_sign
#     # To move to the cell on the top/bottom you move by 2*mini_radius on the y axis.
#     while abs(pos_y) >= abs(2 * mini_radius):
#         tmp_cell_y += 2 * y_sign
#         pos_y -= 2 * mini_radius * y_sign
#         tmp_cell_y_center += 2 * mini_radius * y_sign
#     # Elimination pour trouver dans quel voisin de la cellule courante on est
#     distance = math.sqrt(pos_x ** 2 + pos_y ** 2)
#     if distance <= mini_radius:  # On est forcement dans la bonne pos
#         return tmp_cell_x, tmp_cell_y
#     if distance <= radius:
#         "determiner la ligne qui risque d'etre traversée, et si on a passé la ligne ou non"
#     if abs(pos_x) >= 2.5 * radius:
#         "on est forcément dans g hgg bgg ou d hdd bdd"
#         if abs(pos_y) >= mini_radius:
#             "on est forcement dans hgg bgg hdd bdd"
#             return tmp_cell_x + x_sign, tmp_cell_y + 2 * y_sign
#         else:
#             "on est dans g ou d"
#             return tmp_cell_x + x_sign, tmp_cell_y
#
#     if abs(pos_x) >= 2 * radius:
#         "on est dans hgg g bgg hg bg / hdd d bdd hd bd "
#         if abs(pos_y) >= mini_radius:
#             "on est dans hgg-hg  bgg-bg  hdd-hd bd-bdd"
#             # On trouve l'équation de la ligne de démarcation
#             x_depart = 2.5 * radius
#             y_depart = mini_radius
#
#             x_fin = 2 * radius
#             y_fin = 2 * mini_radius
#
#             slope = (y_fin - y_depart) / (x_fin - x_depart)
#             offset = y_depart - (slope * x_depart)
#
#             y_ref = abs(pos_x) * slope + offset
#
#             if abs(pos_y) <= abs(y_ref):
#                 # on est dans hg hd bg bd
#                 return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
#             else:
#                 "on est dans hgg bgg hdd bdd"
#                 return tmp_cell_x + x_sign, tmp_cell_y + 2 * y_sign
#             # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente descendante
#             # il faut donc juste regarder si le y du point est inférieur ou supérieur au
#             # y correspondant au x sur l'equation de droite
#
#         else:
#             "on est dans hd ou d (ou equivalent)"
#             # On trouve l'équation de la ligne de démarcation
#             x_depart = 2.5 * radius
#             y_depart = mini_radius
#
#             x_fin = 2 * radius
#             y_fin = 0
#
#             slope = (y_fin - y_depart) / (x_fin - x_depart)
#             offset = y_depart - (slope * x_depart)
#
#             y_ref = abs(pos_x) * slope + offset
#
#             # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente ascendante
#             # il faut donc juste regarder si le y du point est inférieur ou supérieur au
#             # y correspondant au x sur l'equation de droite
#             if abs(pos_y) >= abs(y_ref):
#                 "on est dans hd"
#                 return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
#             else:
#                 "on est dans d"
#                 return tmp_cell_x + x_sign, tmp_cell_y
#
#     if radius < abs(pos_x) < 2 * radius:
#         "on est dans hd"
#         return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
#     if radius / 2 < abs(pos_x) <= 2 * radius:
#         # on est dans c, h ou hd
#         x1 = radius
#         y1 = 0
#
#         x2 = radius / 2
#         y2 = mini_radius
#
#         x3 = radius
#         y3 = 2 * mini_radius
#
#         slope1 = (y1 - y2) / (x1 - x2)
#         offset1 = y2 - (slope1 * x2)
#         y_ref1 = slope1 * pos_x + offset1
#
#         slope2 = (y3 - y2) / (x3 - x2)
#         offset2 = y2 - (slope2 * x2)
#         y_ref2 = slope2 * pos_x + offset2
#
#         if y_ref1 <= abs(pos_y) <= y_ref2:
#             # on est dans hd
#             return find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
#     if abs(pos_y) > mini_radius:
#         return tmp_cell_x, tmp_cell_y + y_sign * 2
#     else:
#         return tmp_cell_x, tmp_cell_y
#
#
# def find_coordinates_corner(cell_x, cell_y, x_sign, y_sign):
#     """aaaaaaaaa"""
#     f_x, f_y = 0, 0
#     y_even = cell_y % 2 == 0
#     if y_even:
#         if x_sign > 0:
#             f_x = cell_x
#         else:
#             f_x = cell_x - 1
#     else:
#         if x_sign > 0:
#             f_x = cell_x + 1
#         else:
#             f_x = cell_x
#     if y_sign > 0:
#         f_y = cell_y + 1
#     else:
#         f_y = cell_y - 1
#
#     return f_x, f_y
