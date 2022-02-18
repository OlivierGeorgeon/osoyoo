import HexaGrid
class HexaMemory(HexaGrid):
    def __init__(self,width,height,cells_radius = 50, robot_width = 200):
        """Construct the HexaMemory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        super().__init__(width,height)
        self.cells_radius = cells_radius    
        self.robotPos_x = self.width / 2
        self.robotPos_y = self.height / 2
        self.robot_width = robot_width

    def move(self, direction, distance):
        """Handle the movement of the robot in the HexaGrid
        Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
               Distance = distance travelled by the robot

        Return : the new cell of the robot 
        """
        cells_passed = []

        number_of_cells_travelled = 0
        number_of_cells_travelled = distance // (2*self.cells_radius)
        if(number_of_cells_travelled > 0):
            cells_passed.append(self.grid[x_base][y_base])
            x_base = self.robotPos_x
            y_base = self.robotPos_y
            for i in range(number_of_cells_travelled-1):
                tmp_cell = self.get_neighbor_in_direction(x_base, y_base,direction)
                cells_passed.append(tmp_cell)
                x_base = tmp_cell.x
                y_base = tmp_cell.y
            
            ## ATTENTION TODO DEBUG : ça va merder quand on sort de la grille
            self.apply_changes(cells_passed)
            final_cell = self.get_neighbor_in_direction(x_base, y_base,direction)

        self.robotPos_x = final_cell.x
        self.robotPos_y = final_cell.y

    def apply_changes(self, cells_passed):
        return None