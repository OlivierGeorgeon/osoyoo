import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from ast import match_case
import math
from . HexaGrid import HexaGrid


class HexaMemory(HexaGrid):
    """Hexa memory is an allocentric memory, made with an hexagonal grid.
    You can find informations on the hexagonal grid coordinates system in the docs
    folder.
    """

    def __init__(self, width, height, cells_radius=50, robot_width=200):
        """Construct the HexaMemory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        super().__init__(width, height)
        self.cells_radius = cells_radius
        self.robot_cell_x = self.width // 2
        self.robot_cell_y = self.height // 2
        self.robot_pos_x = 0
        self.robot_pos_y = 0
        self.robot_width = robot_width
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        self.robot_angle = 90
        self.orientation = 0
        self.update_orientation()
        self.azimuth = 0

    def reset(self):
        """Reset the hexamemory"""
        super().__init__(self.width, self.height)
        self.robot_cell_x = self.width // 2
        self.robot_cell_y = self.height // 2
        self.robot_pos_x = 0
        self.robot_pos_y = 0
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        self.robot_angle = 90
        self.orientation = 0
        self.azimuth = 0
        self.update_orientation()

    def update_orientation(self):
        "update the orientation of the robot based on its angle"
        angle = self.robot_angle
        if angle <= 60:
            self.orientation = 1
            return
        if angle <= 120:
            self.orientation = 0
            return
        if angle <= 180:
            self.orientation = 5
            return
        if angle <= 240:
            self.orientation = 4
            return
        if angle <= 300:
            self.orientation = 3
            return
        self.orientation = 2

    def depr_convert_pos_in_cell(self, pos_x, pos_y):
        """blabla"""
        radius = self.cells_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
        nb_cells_x = 0
        if(pos_x > radius):
            nb_cells_x = 1
            to_go = pos_x - radius
            while to_go > 0:
                if nb_cells_x % 2 != 0:
                    if(to_go > radius):
                        to_go -= radius
                        nb_cells_x += 1
                    else:
                        to_go = 0
                else:
                    if(to_go > 2*radius):
                        to_go -= 2*radius
                        nb_cells_x += 1
                    else:
                        to_go = 0
           # nb_cells_x += int((pos_x - radius) / (radius*2)) #TODO: merde
        elif(pos_x < (0-radius)):
            nb_cells_x = -1
            nb_cells_x += int((pos_x + radius) / (radius*2))  # TODO: merde

            nb_cells_x = -1
            to_go = pos_x + radius
            while to_go < 0:
                if nb_cells_x % 2 != 0:
                    if(to_go < 0-radius):
                        to_go += radius
                        nb_cells_x -= 1
                    else:
                        to_go = 0
                else:
                    if(to_go < 0-2*radius):
                        to_go += 2*radius
                        nb_cells_x -= 1
                    else:
                        to_go = 0
        nb_cells_y = 0
        if(pos_y > mini_radius):
            nb_cells_y = 1
            nb_cells_y += int((pos_y - mini_radius) / (mini_radius*2))
        elif(pos_y < (0-mini_radius)):
            nb_cells_y = -1
            if (pos_y + mini_radius) / (mini_radius*2) < -1:
                nb_cells_y += int((pos_y + mini_radius) / (mini_radius*2))

        start_cell_x = self.width//2
        start_cell_y = self.height // 2

        x_decal = 0
        y_decal = 0
        y_add = 0

        while nb_cells_y != 0:
            if(nb_cells_y > 0):
                y_decal += 2
                nb_cells_y -= 1
            else:
                y_decal -= 2
                nb_cells_y += 1

        cell_y = start_cell_y + y_decal
        current_y_is_even = cell_y % 2 == 0

        nb_cells_x_is_even = nb_cells_x % 2 == 0
        while nb_cells_x != 0:
            if nb_cells_x > 0:
                if current_y_is_even:
                    y_add = 1
                    current_y_is_even = False

                else:
                    y_add = 0
                    current_y_is_even = True
                    x_decal += 1
                nb_cells_x -= 1
            elif nb_cells_x < 0:
                if current_y_is_even:
                    y_add = 1
                    x_decal -= 1
                    current_y_is_even = False
                else:
                    y_add = 0
                    current_y_is_even = True
                nb_cells_x += 1
        if (not nb_cells_x_is_even) and (y_add == 1) and (y_decal != 0):
            if(y_decal > 0):
                y_add = -1
            else:
                y_add = 1

        end_x = start_cell_x + x_decal
        end_y = start_cell_y + y_decal + y_add

        return end_x, end_y


    def convert_pos_in_cell(self,pos_x, pos_y):
        """j'essaie autre chose"""
        radius = self.cells_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
        tmp_cell_x = self.width // 2
        tmp_cell_y = self.height // 2
        tmp_cell_x_center = 0
        tmp_cell_y_center = 0
        # Do the regular part of translation :
        # to go to the next cell on the right/left you move by 3*radius on the x axis.
        x_sign = 1
        if pos_x < 0 :
            x_sign = -1
        y_sign = 1
        if pos_y < 0 :
            y_sign = -1
        while abs(pos_x) >= abs(3*radius) :
            tmp_cell_x += x_sign
            pos_x -= (3*radius) * x_sign
            tmp_cell_x_center += (3*radius) * x_sign
        #To move to the cell on the top/bottom you move by 2*mini_radius on the y axis. 
        while abs(pos_y) >= abs(2*mini_radius) :
            tmp_cell_y += 2*y_sign
            pos_y -= 2*mini_radius*y_sign
            tmp_cell_y_center += 2*mini_radius*y_sign
        # Elimination pour trouver dans quel voisin de la cellule courante on est
        distance = math.sqrt(pos_x**2 + pos_y**2)
        if(distance <= mini_radius): # On est forcement dans la bonne pos
            return tmp_cell_x, tmp_cell_y
        if distance <= radius :
            "determiner la ligne qui risque d'etre traversée, et si on a passé la ligne ou non"
        if abs(pos_x) >= 2.5 * radius:
            "on est forcément dans g hgg bgg ou d hdd bdd"
            if abs(pos_y) >= mini_radius :
                "on est forcement dans hgg bgg hdd bdd"
                return tmp_cell_x+ x_sign, tmp_cell_y + 2*y_sign
            else :
                "on est dans g ou d"
                return tmp_cell_x + x_sign, tmp_cell_y

        if abs(pos_x) >= 2 * radius :
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

                if abs(pos_y) <= abs(y_ref) :
                   "on est dans hg hd bg bd"
                   return self.find_coordinates_corner(tmp_cell_x,tmp_cell_y, x_sign,y_sign)
                else :
                   "on est dans hgg bgg hdd bdd"
                   return tmp_cell_x+ x_sign, tmp_cell_y + 2*y_sign
                # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente descendante
                # il faut donc juste regarder si le y du point est inférieur ou supérieur au 
                # y correspondant au x sur l'equation de droite

            else : 
                "on est dans hd ou d (ou equivalent)"
                # On trouve l'équation de la ligne de démarcation
                x_depart = 2.5 * radius
                y_depart = mini_radius

                x_fin = 2* radius
                y_fin = 0

                slope = (y_fin - y_depart) / (x_fin - x_depart)
                offset = y_depart - (slope * x_depart)

                y_ref = abs(pos_x) * slope + offset

                # sauf erreur, si on met tout en valeur absolue on obtient toujours une pente ascendante
                # il faut donc juste regarder si le y du point est inférieur ou supérieur au 
                # y correspondant au x sur l'equation de droite
                if abs(pos_y) >= abs(y_ref) :
                   "on est dans hd"
                   return self.find_coordinates_corner(tmp_cell_x,tmp_cell_y, x_sign,y_sign)
                else :
                   "on est dans d"
                   return tmp_cell_x+ x_sign, tmp_cell_y
            
        if abs(pos_x)> radius and abs(pos_x)< 2*radius :
            "on est dans hd"
            return self.find_coordinates_corner(tmp_cell_x,tmp_cell_y, x_sign,y_sign)
        if abs(pos_x) > radius/2 and abs(pos_x)<= 2*radius:
            # on est dans c, h ou hd
            x1 = radius
            y1 = 0

            x2 = radius/2
            y2 = mini_radius

            x3 = radius
            y3= 2*mini_radius

            slope1 = (y1 - y2) / (x1 - x2)
            offset1 = y2 - (slope1 * x2)
            y_ref1 = slope1 * pos_x + offset1

            slope2 = (y3 - y2) / (x3 - x2)
            offset2 = y2 - (slope2 * x2)
            y_ref2 = slope2 * pos_x + offset2


            if abs(pos_y) >= y_ref1 and abs(pos_y) <= y_ref2:
                # on est dans hd
                return self.find_coordinates_corner(tmp_cell_x,tmp_cell_y, x_sign,y_sign)
        if abs(pos_y)>mini_radius :
            return tmp_cell_x, tmp_cell_y + y_sign*2
        else :
            return tmp_cell_x, tmp_cell_y



    def find_coordinates_corner(self,cell_x,cell_y,x_sign,y_sign):
        """aaaaaaaaa"""
        f_x, f_y =0,0
        y_even =cell_y % 2 == 0
        if(y_even):
            if(x_sign > 0):
                f_x = cell_x
            else :
                f_x = cell_x - 1

        else :
            if(x_sign > 0):
                f_x = cell_x+1
            else :
                f_x = cell_x

        if(y_sign > 0):
            f_y = cell_y +1 
        else :
            f_y = cell_y - 1

        return f_x,f_y
        


    def move(self, rotation, move_x, move_y):
        """Handle movement of the robot in the hexamemory"""
        self.rotate_robot(rotation)

        rota_radian = math.radians(self.robot_angle)
        #move_x += self.robot_pos_x
        #move_y += self.robot_pos_y
        x_prime = int(move_x * math.cos(rota_radian) - move_y * math.sin(rota_radian))  # OG 27/08/2022
        y_prime = int(move_x * math.sin(rota_radian) + move_y * math.cos(rota_radian))
        x_prime += self.robot_pos_x
        y_prime += self.robot_pos_y
        self.apply_changes(
            self.robot_pos_x, self.robot_pos_y, x_prime, y_prime)
        self.robot_pos_x = x_prime
        self.robot_pos_y = y_prime
        self.grid[self.robot_cell_x][self.robot_cell_y].set_to('Free')
        self.grid[self.robot_cell_x][self.robot_cell_y].leave()
        self.robot_cell_x, self.robot_cell_y = self.convert_pos_in_cell(
            self.robot_pos_x, self.robot_pos_y)
        self.grid[self.robot_cell_x][self.robot_cell_y].occupy()
        return x_prime, y_prime

    
    def apply_phenomenon(self, phenomenon, pos_x, pos_y):
        """Apply a phenomenon to the grid
        Args :
            phenomenon : type of phenomenon (TODO: but should be things like "line", "unmovable object", "movable object", etc.)
            pos_x, pos_y : position of the phenomenon (relative to the robot's position)
        """

    def rotate_robot(self, rotation):
        """Rotate the representation of the robot by the given angle.

        :Parameters:
            `rotation` : int, degrees of rotation
        """
        self.robot_angle = (self.robot_angle + rotation)
        while self.robot_angle < 0:
            self.robot_angle = 360 + self.robot_angle
        self.robot_angle = self.robot_angle % 360

        if(360-(self.robot_angle-90)  < self.azimuth -10 or 360-(self.robot_angle-90) > self.azimuth+10):
            print( " <HEXA_MEMORY> : correction erreur angle")
            self.robot_angle = 360 - self.azimuth +90
        self.update_orientation()
        #print("robot_orientation in hexa_memory : ", self.orientation,
        #      "robot_angle in hexa_memory : ", self.robot_angle)  # TODO: arranger ce bordel

    # def go_forward(self,distance):
    #    self.move(self.robot_orientation,distance)

    def get_robot_pos(self):
        return self.robot_cell_x, self.robot_cell_y

    def get_robot_neighbors_with_direction(self):
        """"""
        return self.get_all_neighbors_with_direction(self.robot_cell_x, self.robot_cell_y)



    def apply_changes(self, start_x, start_y, end_x, end_y, status="Free"):
        """Apply the given status (Free by default) to every cell between coordinates start_x,start_y and end_x,end_y"""

        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        if distance == 0:
            return
        nb_step = int(distance/(self.cells_radius))
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
            self.grid[cell_x][cell_y].status = status
            self.grid[cell_x][cell_y].leave()
            ####
            current_pos_x += step_x
            current_pos_y += step_y
            """
            if(abs(current_pos_x ) > abs(end_x)):
                current_pos_x = end_x
            if(abs(current_pos_y ) > abs(end_y)):
                current_pos_y = end_y
            """

    def get_direction_of_neighbor_with_status(self, status):
        ""

    def apply_movement(self, rotation, distance):
        self.rotate_robot(rotation)
        self.go_forward(distance)








################ DEPRECATED
def depr_move(self, direction, distance):
        """Handle the movement of the robot in the HexaGrid : change position of the robot in the HexaGrid
        and apply changes on cells passed through
        Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
               Distance = distance travelled by the robot

        Return : the new cell of the robot
        """
        cells_passed = []

        number_of_cells_travelled = 0
        number_of_cells_travelled = distance // (2*self.cells_radius)
        final_cell = self.grid[self.robot_cell_x][self.robot_cell_y]
        if(number_of_cells_travelled > 0):
            x_base = self.robot_cell_x
            y_base = self.robot_cell_y
            cells_passed.append(self.grid[x_base][y_base])

            for i in range(number_of_cells_travelled-1):
                tmp_cell = self.get_neighbor_in_direction(
                    x_base, y_base, direction)
                if(tmp_cell is None):
                    break
                cells_passed.append(tmp_cell)
                x_base = tmp_cell.x
                y_base = tmp_cell.y

            # ATTENTION TODO DEBUG : ça va merder quand on sort de la grille
            self.apply_changes_on_cells_passed(cells_passed)
            final_cell_tmp = self.get_neighbor_in_direction(
                x_base, y_base, direction)
            if(final_cell_tmp is not None):
                final_cell = final_cell_tmp
                self.robot_cell_x = final_cell.x
                self.robot_cell_y = final_cell.y
        if(number_of_cells_travelled < 0):
            print("en arrierent")
            x_base = self.robot_cell_x
            y_base = self.robot_cell_y
            cells_passed.append(self.grid[x_base][y_base])

            for i in range(number_of_cells_travelled-1):
                tmp_cell = self.get_neighbor_in_direction(
                    x_base, y_base, (direction+3) % 6)
                if(tmp_cell is None):
                    break
                cells_passed.append(tmp_cell)
                x_base = tmp_cell.x
                y_base = tmp_cell.y

            # ATTENTION TODO DEBUG : ça va merder quand on sort de la grille
            self.apply_changes_on_cells_passed(cells_passed)
            final_cell_tmp = self.get_neighbor_in_direction(
                x_base, y_base, (direction+3) % 6)
            if(final_cell_tmp is not None):
                final_cell = final_cell_tmp
                self.robot_cell_x = final_cell.x
                self.robot_cell_y = final_cell.y
        final_cell.set_to("Occupied")

def apply_changes_on_cells_passed(self, cells_passed):
    """Apply changes on cells passed through by the robot i.e. change their state to "Free" 
    """
    cells_passed = [element.set_to("Free") for element in cells_passed]
    return None