import math
from pyrr import matrix44
from . GridCell import GridCell
from ..EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_PLACE


class AllocentricMemory:
    """The agent's allocentric memory made with an hexagonal grid."""

    def __init__(self, width, height, cell_radius=50):
        """Construct the allocentric memory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        self.affordances = []
        self.grid = list()
        self.width = width
        self.height = height
        for i in range(self.width):
            self.grid.append(list())
            for j in range(self.height):
                self.grid[i].append(GridCell(i, j))

        self.cell_radius = cell_radius
        self.robot_cell_x = self.width // 2
        self.robot_cell_y = self.height // 2
        self.robot_pos_x = 0
        self.robot_pos_y = 0
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        self.cells_changed_recently = []

    def reset(self):
        """Reset the hexamemory"""
        super().__init__(self.width, self.height)
        self.robot_cell_x = self.width // 2
        self.robot_cell_y = self.height // 2
        self.robot_pos_x = 0
        self.robot_pos_y = 0
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        self.cells_changed_recently = []

    def __str__(self):
        output = ""
        for j in range(self.height-1, -1, -1):
            if j % 2 == 1:
                output += "-----"
            for i in range(self.width):
                output += str(self.grid[i][j])
                output += "-----"
            output += "\n"
        return output

    def convert_pos_in_cell(self, pos_x, pos_y):
        """Convert an allocentric position to cell coordinates."""
        radius = self.cell_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
        tmp_cell_x = self.width // 2
        tmp_cell_y = self.height // 2
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
        while abs(pos_y) >= abs(2*mini_radius) :
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
            if abs(pos_y) >= mini_radius :
                "on est forcement dans hgg bgg hdd bdd"
                return tmp_cell_x+ x_sign, tmp_cell_y + 2*y_sign
            else:
                "on est dans g ou d"
                return tmp_cell_x + x_sign, tmp_cell_y

        if abs(pos_x) >= 2 * radius:
            "on est dans hgg g bgg hg bg / hdd d bdd hd bd "
            if abs(pos_y) >= mini_radius :
                "on est dans hgg-hg  bgg-bg  hdd-hd bd-bdd"
                # On trouve l'équation de la ligne de démarcation
                x_depart = 2.5 * radius
                y_depart = mini_radius

                x_fin = 2* radius
                y_fin = 2*mini_radius

                slope = (y_fin - y_depart) / (x_fin - x_depart)
                offset = y_depart - (slope * x_depart)

                y_ref = abs(pos_x) * slope + offset

                if abs(pos_y) <= abs(y_ref):
                    # on est dans hg hd bg bd
                    return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign, y_sign)
                else:
                    "on est dans hgg bgg hdd bdd"
                    return tmp_cell_x+ x_sign, tmp_cell_y + 2*y_sign
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
                if abs(pos_y) >= abs(y_ref) :
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
                return self.find_coordinates_corner(tmp_cell_x, tmp_cell_y, x_sign,y_sign)
        if abs(pos_y) > mini_radius:
            return tmp_cell_x, tmp_cell_y + y_sign*2
        else:
            return tmp_cell_x, tmp_cell_y

    def convert_cell_to_pos(self, cell_x, cell_y):
        """Return the allocentric position of the center of the given cell."""
        radius = self.cell_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
        start_x = self.width // 2
        change_x = cell_x - start_x
        start_y = self.height // 2
        change_y = cell_y - start_y
        pos_x = 3 * radius * change_x
        pos_y = 0
        reste = 0
        if change_y % 2 == 0:
            pos_y = mini_radius * change_y
        else:
            signe = change_y/abs(change_y)
            pos_y = mini_radius * (change_y - signe)
            reste = signe

        if reste != 0:
            y_arrivee = (change_y - signe) + start_y
            signe_x = 1 if y_arrivee % 2 == 0 else -1
            pos_x += signe_x * (3/2)*radius
            pos_y += signe * mini_radius

        return int(pos_x), int(pos_y)

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

    def move(self, body_direction_rad, translation, is_egocentric_translation=True):
        """Move the robot in allocentric memory. mark the traversed cells Free. Returns the new position"""
        destination_x = self.robot_pos_x
        destination_y = self.robot_pos_y
        if is_egocentric_translation:
            destination_x += round((translation[0] * math.cos(body_direction_rad) -
                                    translation[1] * math.sin(body_direction_rad)))
            destination_y += round((translation[0] * math.sin(body_direction_rad) +
                                    translation[1] * math.cos(body_direction_rad)))
        else:
            destination_x += translation[0]
            destination_y += translation[1]

        try:
            self.apply_changes(self.robot_pos_x, self.robot_pos_y, destination_x, destination_y)
            self.robot_pos_x = destination_x
            self.robot_pos_y = destination_y
        except IndexError:
            print("IndexError")
            self.robot_cell_x = self.width // 2
            self.robot_cell_y = self.height // 2
            self.robot_pos_x = 0
            self.robot_pos_y = 0

        # Leave the previous occupied cell
        if self.grid[self.robot_cell_x][self.robot_cell_y] != EXPERIENCE_FLOOR:
            self.grid[self.robot_cell_x][self.robot_cell_y].set_to(EXPERIENCE_PLACE)
        self.grid[self.robot_cell_x][self.robot_cell_y].leave()
        self.cells_changed_recently.append((self.robot_cell_x, self.robot_cell_y))

        # Mark the new occupied cell
        self.robot_cell_x, self.robot_cell_y = self.convert_pos_in_cell(
            self.robot_pos_x, self.robot_pos_y)
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        self.cells_changed_recently.append((self.robot_cell_x, self.robot_cell_y))

        return destination_x, destination_y

    def place_robot(self, body_memory):
        """Apply the PLACE status to the cells at the position of the robot"""
        for i in range(self.width):
            for j in range(self.height):
                pos_x, pos_y = self.convert_cell_to_pos(i, j)
                if body_memory.is_inside_robot(pos_x - self.robot_pos_x, pos_y - self.robot_pos_y):
                    self.apply_status_to_cell(i, j, EXPERIENCE_PLACE)

    def apply_changes(self, start_x, start_y, end_x, end_y, status="Free"):
        """Apply the given status (Free by default) to every cell between coordinates start_x,start_y and end_x,end_y"""

        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        if distance == 0:
            return
        nb_step = int(distance / self.cell_radius)
        if nb_step == 0:
            return
        step_x = int((end_x - start_x)/nb_step)
        step_y = int((end_y - start_y)/nb_step)
        current_pos_x = start_x
        current_pos_y = start_y
        for _ in range(nb_step):
            cell_x, cell_y = self.convert_pos_in_cell(
                current_pos_x, current_pos_y)
            # if(self.grid[cell_x][cell_y].status == "Unknown"):
            if self.grid[cell_x][cell_y].status != "Frontier":
                self.grid[cell_x][cell_y].status = status
            self.grid[cell_x][cell_y].leave()
            self.cells_changed_recently.append((cell_x, cell_y))
            current_pos_x += step_x
            current_pos_y += step_y

    def apply_status_to_cell(self, cell_x, cell_y, status):
        try:
            self.grid[cell_x][cell_y].status = status
            self.cells_changed_recently.append((cell_x, cell_y))
        except IndexError:
            print("Error cell out of grid, cell_x:", cell_x, "cell_y:", cell_y, "Status:", status)
            exit()

    def body_position_matrix(self):
        return matrix44.create_from_translation([self.robot_pos_x, self.robot_pos_y, 0])
