from HexaGrid import HexaGrid
class HexaMemory(HexaGrid):
    """Hexa memory is an allocentric memory, made with an hexagonal grid.
    You can find informations on the hexagonal grid coordinates system in the docs
    folder.
    """

    def __init__(self,width,height,cells_radius = 50, robot_width = 200):
        """Construct the HexaMemory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        super().__init__(width,height)
        self.cells_radius = cells_radius    
        self.robotPos_x = self.width // 2
        self.robotPos_y = self.height // 2
        self.robot_width = robot_width
        print("DEBUG : Robot position at init of HEXAMEMORY : ",self.robotPos_x,self.robotPos_y)
        self.grid[self.robotPos_x][self.robotPos_y].set_to("Occupied")
        self.robot_orientation = 0 # Should use the same values as directions of the move() function
        self.robot_angle = 0

    def move(self, direction, distance):
        """Handle the movement of the robot in the HexaGrid : change position of the robot in the HexaGrid
        and apply changes on cells passed through
        Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
               Distance = distance travelled by the robot

        Return : the new cell of the robot 
        """
        cells_passed = []

        number_of_cells_travelled = 0
        number_of_cells_travelled = distance // (2*self.cells_radius)
        final_cell = self.grid[self.robotPos_x][self.robotPos_y]
        if(number_of_cells_travelled > 0):
            x_base = self.robotPos_x
            y_base = self.robotPos_y
            cells_passed.append(self.grid[x_base][y_base])
            
            for i in range(number_of_cells_travelled-1):
                tmp_cell = self.get_neighbor_in_direction(x_base, y_base,direction)
                if(tmp_cell is None):
                    break
                cells_passed.append(tmp_cell)
                x_base = tmp_cell.x
                y_base = tmp_cell.y
            
            ## ATTENTION TODO DEBUG : ça va merder quand on sort de la grille
            self.apply_changes_on_cells_passed(cells_passed)
            final_cell_tmp = self.get_neighbor_in_direction(x_base, y_base,direction)
            if(final_cell_tmp is not None):
                final_cell = final_cell_tmp
                self.robotPos_x = final_cell.x
                self.robotPos_y = final_cell.y
        if(number_of_cells_travelled < 0):
            print("en arrierent")
            x_base = self.robotPos_x
            y_base = self.robotPos_y
            cells_passed.append(self.grid[x_base][y_base])
            
            for i in range(number_of_cells_travelled-1):
                tmp_cell = self.get_neighbor_in_direction(x_base, y_base,(direction+3)%6)
                if(tmp_cell is None):
                    break
                cells_passed.append(tmp_cell)
                x_base = tmp_cell.x
                y_base = tmp_cell.y
            
            ## ATTENTION TODO DEBUG : ça va merder quand on sort de la grille
            self.apply_changes_on_cells_passed(cells_passed)
            final_cell_tmp = self.get_neighbor_in_direction(x_base, y_base,(direction+3)%6)
            if(final_cell_tmp is not None):
                final_cell = final_cell_tmp
                self.robotPos_x = final_cell.x
                self.robotPos_y = final_cell.y
        final_cell.set_to("Occupied")

    def apply_phenomenon(self,phenomenon,pos_x,pos_y):
        """Apply a phenomenon to the grid
        Args : 
            phenomenon : type of phenomenon (TODO: but should be things like "line", "unmovable object", "movable object", etc.)
            pos_x, pos_y : position of the phenomenon (relative to the robot's position)
        """
        
    def rotate_robot(self,rotation):
        """Rotate the representation of the robot in the given direction.

        :Parameters:
            `rotation` : int
                Degrees
        """
        self.robot_angle = (self.robot_angle + rotation)
        while self.robot_angle < 0 :
            self.robot_angle = 360 + self.robot_angle
        self.robot_angle = self.robot_angle %360
        self.robot_orientation = int((self.robot_angle)//60)
        ""
        print("robot_orientation in hexa_memory : ", self.robot_orientation) # TODO: arranger ce bordel

    def go_forward(self,distance):
        self.move(self.robot_orientation,distance)
    
    def get_robot_pos(self):
        return self.robotPos_x,self.robotPos_y

    def get_robot_neighbors_with_direction(self):
        """"""
        return self.get_all_neighbors_with_direction(self.robotPos_x, self.robotPos_y)

    def apply_changes_on_cells_passed(self, cells_passed):
        """Apply changes on cells passed through by the robot i.e. change their state to "Free" 
        """
        cells_passed = [element.set_to("Free") for element in cells_passed]
        return None



    def apply_movement(self,rotation,distance):
        self.rotate_robot(rotation)
        self.go_forward(distance)