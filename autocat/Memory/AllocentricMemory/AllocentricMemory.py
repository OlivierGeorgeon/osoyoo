import math
import numpy as np
from pyrr import matrix44
import time
from . GridCell import GridCell, CELL_UNKNOWN
from ..EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_PLACE
from ..AllocentricMemory.GridCell import CELL_NO_ECHO
from ...Utils import rotate_vector_z
from ..EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PROMPT


class AllocentricMemory:
    """The agent's allocentric memory made with an hexagonal grid."""

    def __init__(self, width, height, cell_radius=50):
        """Construct the allocentric memory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        self.affordances = []
        self.grid = list()
        self.width = width  # Nb cells width
        self.height = height  # Nb cells height
        self.min_i = -width // 2 + 1
        self.max_i = width // 2
        self.min_j = -height // 2 + 1
        self.max_j = height // 2
        self.cell_radius = cell_radius

        self.focus_i = None
        self.focus_j = None
        self.prompt_i = None
        self.prompt_j = None

        # Fill the grid with cells
        # Use negative grid index for negative positions
        for i in range(self.width):
            self.grid.append(list())
            if i <= self.width // 2:
                cell_i = i
            else:
                cell_i = -self.width + i
            for j in range(self.height):
                if j <= self.height // 2:
                    cell_j = j
                else:
                    cell_j = -self.height + j
                self.grid[i].append(GridCell(cell_i, cell_j, self.cell_radius))

        # Allocentric memory is initialized with the robot at its center
        self.robot_point = np.array([0, 0, 0], dtype=float)
        # self.robot_cell_x = self.width // 2
        # self.robot_cell_y = self.height // 2

    # def reset(self):
    #     """Reset the hexamemory"""
    #     super().__init__(self.width, self.height)
    #     # self.robot_cell_x = self.width // 2
    #     # self.robot_cell_y = self.height // 2
    #     self.robot_point = np.array([0, 0, 0], dtype=float)
    #     # self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
    #     # self.cells_changed_recently = []

    def __str__(self):
        output = ""
        for j in range(self.max_j, self.min_j - 1, -1):
            if j % 2 == 1:
                output += "-----"
            for i in range(self.min_i, self.max_i + 1):
                output += str(self.grid[i][j]) + "-----"
                # output += "-----"
            output += "\n"
        return output

    def convert_pos_in_cell(self, pos_x, pos_y):
        """Convert an allocentric position to cell coordinates."""
        radius = self.cell_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
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
        while abs(pos_x) >= abs(3*radius):
            tmp_cell_x += x_sign
            pos_x -= (3*radius) * x_sign
            tmp_cell_x_center += (3*radius) * x_sign
        # To move to the cell on the top/bottom you move by 2*mini_radius on the y axis.
        while abs(pos_y) >= abs(2*mini_radius):
            tmp_cell_y += 2*y_sign
            pos_y -= 2*mini_radius*y_sign
            tmp_cell_y_center += 2*mini_radius*y_sign
        # Elimination pour trouver dans quel voisin de la cellule courante on est
        distance = math.sqrt(pos_x**2 + pos_y**2)
        if distance <= mini_radius:  # On est forcement dans la bonne pos
            return tmp_cell_x, tmp_cell_y
        if distance <= radius:
            "determiner la ligne qui risque d'etre traversée, et si on a passé la ligne ou non"
        if abs(pos_x) >= 2.5 * radius:
            "on est forcément dans g hgg bgg ou d hdd bdd"
            if abs(pos_y) >= mini_radius:
                "on est forcement dans hgg bgg hdd bdd"
                return tmp_cell_x + x_sign, tmp_cell_y + 2*y_sign
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
                    return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
                else:
                    "on est dans hgg bgg hdd bdd"
                    return tmp_cell_x + x_sign, tmp_cell_y + 2*y_sign
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
                    return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
                else:
                    "on est dans d"
                    return tmp_cell_x + x_sign, tmp_cell_y
            
        if radius < abs(pos_x) < 2 * radius:
            "on est dans hd"
            return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
        if radius/2 < abs(pos_x) <= 2 * radius:
            # on est dans c, h ou hd
            x1 = radius
            y1 = 0

            x2 = radius/2
            y2 = mini_radius

            x3 = radius
            y3 = 2*mini_radius

            slope1 = (y1 - y2) / (x1 - x2)
            offset1 = y2 - (slope1 * x2)
            y_ref1 = slope1 * pos_x + offset1

            slope2 = (y3 - y2) / (x3 - x2)
            offset2 = y2 - (slope2 * x2)
            y_ref2 = slope2 * pos_x + offset2

            if y_ref1 <= abs(pos_y) <= y_ref2:
                # on est dans hd
                return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
        if abs(pos_y) > mini_radius:
            return tmp_cell_x, tmp_cell_y + y_sign*2
        else:
            return tmp_cell_x, tmp_cell_y

    def find_coordinates_corner(self, cell_x, cell_y, x_sign, y_sign):
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
                f_x = cell_x+1
            else:
                f_x = cell_x
        if y_sign > 0:
            f_y = cell_y + 1
        else:
            f_y = cell_y - 1

        return f_x, f_y

    def move(self, body_direction_rad, translation, clock, is_egocentric_translation=True):
        """Move the robot in allocentric memory. Mark the traversed cells Free. Returns the new position"""
        # Compute the robot destination point
        if is_egocentric_translation:
            destination_point = self.robot_point + rotate_vector_z(translation, body_direction_rad)
        else:
            destination_point = self.robot_point + translation
        # Check that the robot remains within allocentric memory limits
        # try:
        self.apply_changes(self.robot_point, destination_point, clock)
        self.robot_point = destination_point
        # except IndexError:
        #     print("IndexError")
        #     self.robot_cell_x = self.width // 2
        #     self.robot_cell_y = self.height // 2
        #     self.robot_point = np.array([0, 0, 0], dtype=float)

        # # Leave the previous occupied cell
        # if self.grid[self.robot_cell_x][self.robot_cell_y] != EXPERIENCE_FLOOR:
        #     self.grid[self.robot_cell_x][self.robot_cell_y].set_to(EXPERIENCE_PLACE)
        #
        # # Mark the new occupied cell
        # self.robot_cell_x, self.robot_cell_y = self.convert_pos_in_cell(
        #     self.robot_point[0], self.robot_point[1])

        return np.round(destination_point)

    def place_robot(self, body_memory, clock):
        """Apply the PLACE status to the cells at the position of the robot"""
        # start_time = time.time()
        outline = body_memory.outline() + self.robot_point
        polygon = [p[0:2] for p in outline]
        for c in [c for line in self.grid for c in line if c.is_inside(polygon)]:
            c.status[0] = EXPERIENCE_PLACE
            c.clocks[0] = clock
            # self.apply_status_to_cell(c.i, c.j, EXPERIENCE_PLACE)
        # print("Place robot time:", time.time() - start_time, "seconds")

    def clear_phenomena(self):
        """Reset the phenomena from cells"""
        # for i in range(self.width):
        #     for j in range(self.height):
        #         if self.grid[i][j].phenomenon is not None:
        for c in [c for line in self.grid for c in line if c.phenomenon is not None]:
            # self.apply_status_to_cell(i, j, CELL_UNKNOWN)
            c.status[1] = CELL_UNKNOWN
            c.clocks[1] = 0
            c.phenomenon = None

    def apply_changes(self, start, end, clock):
        """Mark the cells traversed by the robot"""
        # distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        distance = math.dist(start, end)
        if distance == 0:
            return
        nb_step = int(distance / self.cell_radius)
        if nb_step == 0:
            return
        step_x = int((end[0] - start[0])/nb_step)
        step_y = int((end[1] - start[1])/nb_step)
        current_pos_x = start[0]
        current_pos_y = start[1]
        for _ in range(nb_step):
            cell_x, cell_y = self.convert_pos_in_cell(current_pos_x, current_pos_y)
            # self.grid[cell_x][cell_y].status[1] = status
            self.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_PLACE, clock)
            current_pos_x += step_x
            current_pos_y += step_y

    def apply_status_to_cell(self, i, j, status, clock):
        """Change the cell status"""
        if (self.min_i <= i <= self.max_i) and (self.min_j <= j <= self.max_j):
            if status == EXPERIENCE_FLOOR:
                self.grid[i][j].status[0] = status
                self.grid[i][j].clocks[0] = clock
            else:
                self.grid[i][j].status[1] = status
                self.grid[i][j].clocks[1] = clock
        else:
            print("Error: cell out of grid, i:", i, "j:", j, "Status:", status)

    def mark_echo_area(self, affordance):
        """Mark the area covered by the echolocalization sensor in allocentric memory"""
        # start_time = time.time()
        points = affordance.sensor_triangle()
        triangle = [p[0:2] for p in points]
        for c in [c for line in self.grid for c in line if c.is_inside(triangle)]:
            c.status[2] = CELL_NO_ECHO
            c.clocks[2] = affordance.experience.clock
        # print("Place echo time:", time.time() - start_time, "seconds")

    def update_focus(self, allo_focus):
        """Update the focus in allocentric memory"""
        # Clear the previous focus cell
        if self.focus_i is not None:
            self.grid[self.focus_i][self.focus_j].status[3] = CELL_UNKNOWN
        # Add the new focus cell
        if allo_focus is not None:
            self.focus_i, self.focus_j = self.convert_pos_in_cell(allo_focus[0], allo_focus[1])
            self.grid[self.focus_i][self.focus_j].status[3] = EXPERIENCE_FOCUS
            # print("Focus in cell", self.focus_i, ", ", self.focus_j)

    def update_prompt(self, allo_prompt):
        """Update the prompt in allocentric memory"""
        # Clear the previous focus cell
        if self.prompt_i is not None:
            self.grid[self.prompt_i][self.prompt_j].status[3] = CELL_UNKNOWN
        # Add the new prompt cell
        if allo_prompt is not None:
            self.prompt_i, self.prompt_j = self.convert_pos_in_cell(allo_prompt[0], allo_prompt[1])
            self.grid[self.prompt_i][self.prompt_j].status[3] = EXPERIENCE_PROMPT
            print("Prompt in cell", self.prompt_i, ", ", self.prompt_j)
