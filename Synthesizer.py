import math
from MemoryNew import MemoryNew
from HexaMemory import HexaMemory
from HexaGrid import HexaGrid

class Synthesizer:
    """ The synthesizer has the role to synthesize the short term egocentric memory
        and the long term allocentric hexa_memory.
        It shall produce new status for the cells that are registred in the hexa_memory.
        To do so it does the following :
                - Create a clean internal_HexaGrid
                - Project Interactions of the memory on the internal_HexaGrid
                - Use informations from the internal_HexaGrid and hexa_memory to change cells status
        """
    def __init__(self,memory,hexa_memory):
        """ The synthesizer has the role to synthesize the short term egocentric memory
        and the long term allocentric hexa_memory.
        It shall produce new status for the cells that are registred in the hexa_memory.
        To do so it does the following :
                - Create a clean internal_HexaGrid
                - Project Interactions of the memory on the internal_HexaGrid
                - Use informations from the internal_HexaGrid and hexa_memory to change cells status
        """
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)
        self.last_used_id = -1
        self.tolerance = 3 #nombre d'id d'ecart d'une interaction que l'on tolère par rapport au last_id pour intervenir sur la synthese

    def act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        self.project_memory_on_internal_grid()
        self.synthesize()
     

    def project_memory_on_internal_grid(self):
        """ Convert position of egocentric interactions of the memory into
        position in the allocentric representation
        """
        for interaction in self.memory.interactions :
            #print("<SYNTHESIZER> : interaction id : ,",interaction.id, "last used id :" ,self.last_used_id)
            corners = interaction.corners
            used_points = []
            if(interaction.id<= self.last_used_id):
                continue
            #print("<SYNTHESIZER> : actual_durability of interact: ", interaction.actual_durability)
            if(interaction.actual_durability > 0):
                for _,point in enumerate(corners) :
                    rota_radian = math.radians(self.hexa_memory.robot_angle)
                    x_corner = point[0]
                    y_corner = point[1]
                    # les interactions etant egocentrés, on fait la manip pour les allocentrer
                    x_prime = int(x_corner * math.cos(rota_radian) + y_corner * math.sin(rota_radian))
                    y_prime = int(y_corner * math.cos(rota_radian) + x_corner * math.sin(rota_radian))
                    # on demande ensuite à l'hexamem de nous traduire leur position en cells
                    x_prime += self.hexa_memory.robot_pos_x
                    y_prime += self.hexa_memory.robot_pos_y
                    x, y = self.hexa_memory.convert_pos_in_cell(x_prime, y_prime)
                    if(x,y) in used_points :
                        continue
                    if(x >= self.hexa_memory.width or y >= self.hexa_memory.height or x <  0 or y < 0):
                        #print("<SYNTHESIZER> Interaction ignorée car hors de la grille")
                        continue
                    try :
                        self.internal_hexa_grid.grid[x][y].interactions.append(interaction)
                        used_points.append((x,y))
                        if len(used_points )>1 : 
                            print("print sur ", len(used_points)," cases : ",used_points[0],used_points[1])
                    except IndexError:
                        print("<SYNTHESIZER> Interaction caused an error : x=",x,"y = ",y,"width = ", self.hexa_memory.width,"height = ",self.hexa_memory.height)
                        continue
            if(interaction.id > self.last_used_id):
                self.last_used_id = interaction.id

    def depr_project_memory_on_internal_grid(self):
        """ Convert position of egocentric interactions of the memory into
        position in the allocentric representation
        """
        # To understand the calculus made here I strongly advise you to
        # have a look at the (quite beautiful) drawing called
        # hexagonal_grid_neighbors_coordinates_schema.png that
        # you can find in the docs folder
        yaw = self.hexa_memory.robot_orientation * 60
        #print("yaw = ", yaw)
        yaw = math.radians(yaw)
        x_robot, y_robot = self.hexa_memory.get_robot_pos()
        radius = self.hexa_memory.cells_radius
        mini_radius = math.sqrt(radius**2 - (radius/2)**2)
        x_robot = x_robot * mini_radius
        y_robot = y_robot * mini_radius
        print(len(self.memory.phenomenons))
        for interaction in self.memory.phenomenons :
            if(interaction is None or interaction.x is None or interaction.y is None):
                continue
            #calcul de la distance au robot
            print( "interaction :" , interaction)
            distance = math.sqrt(interaction.x**2 + interaction.y**2)
            print(distance)
            #calcul du x et y allocentric
    
            x_prime = int(interaction.x * math.cos(yaw) - interaction.y * math.sin(yaw))
            y_prime = int(interaction.y * math.cos(yaw) - interaction.x * math.sin(yaw))

            # on converti le tout en coordonnées pour les cells
            x_robot, y_robot = self.hexa_memory.get_robot_pos()
            nb_radius_x = int( x_prime // (radius) )
            nb_radius_y = int( y_prime // (mini_radius) )
            x_for_hexa = 0
            y_for_hexa = 0
            y_add = 0
            x_add = 0
            if nb_radius_x > 0 :
                current_x = x_robot
                current_x_is_even = current_x%2  == 0
                for _ in range(nb_radius_x):
                    if current_x_is_even :
                        y_add = 1
                        current_x_is_even = False
                    else :
                        y_add = 0
                        x_for_hexa += 1
                        current_x_is_even = True


            #x_for_hexa = nb_radius_x//2
            if nb_radius_y > 0 :
                nb_radius_y -= 1
                y_for_hexa = (1 + nb_radius_y//2) *2
                # we consider the robot is always on the center of the cell
                # so to move in y dimension you first need to move one radius up
                #for the first cell, then 2 radius for each cells after that
                # so (1 + nb_radius_y//2) gets you the number of y cells passed
                # you the multiply it by two because in our coordinates system
                # the cell direct up from the (x,y) cell is the (x,y+2) cell        
            x_interaction = x_for_hexa + x_robot +x_add
            y_interaction = y_for_hexa + y_robot + y_add
            # et on place le tout sur notre internal_grid

            self.internal_hexa_grid.grid[x_interaction][y_interaction].interactions.append(interaction)


    def synthesize(self):
        """Compare states in the HexaMemory to
        and projected interactions in the internal_hexa_grid
        to create new_status for the hexa_memory, and apply them
        """
        for i in range(self.hexa_memory.width) :
            for j in range(self.hexa_memory.height):
                final_status = self.hexa_memory.grid[i][j].status
                cell_hexa = self.hexa_memory.grid[i][j]
                cell_intra = self.internal_hexa_grid.grid[i][j]
                interaction_line = [element for element in cell_intra.interactions if (element.type == "Line" and element.id > self.last_used_id - self.tolerance )]
                if(len(interaction_line) > 0) :
                    ""
                    #print("Cell at (",i,",",j,"has interaction line")
                interaction_blocked = [element for element in cell_intra.interactions if (element.type == "Block" and element.id > self.last_used_id - self.tolerance )]
                interaction_shock = [element for element in cell_intra.interactions if (element.type == "Shock" and element.id > self.last_used_id - self.tolerance )]
                interaction_echo = [element for element in cell_intra.interactions if (element.type == "obstacle" and element.id > self.last_used_id - self.tolerance )]
                if(cell_hexa.status == 'Occupied'):
                    final_status = 'Occupied'
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_line) ):
                    final_status = "Frontier"
                    #print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_blocked)) :
                    final_status = "Blocked"
                elif(len(interaction_shock)) :
                    final_status = "Movable Obstacle"
                elif (len(interaction_echo)):
                    final_status = "Something"
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                else :
                    final_status = cell_hexa.status

                cell_hexa.status = final_status

                


