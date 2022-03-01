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

    def act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        self.project_memory_on_internal_grid()
        self.synthesize()
     

    def project_memory_on_internal_grid(self):
        """ Convert position of egocentric interactions of the memory into
        position in the allocentric representation
        """
        yaw = self.hexa_memory.robot_orientation * 60
        print("yaw = ", yaw)
        yaw = math.radians(yaw)
        x_robot, y_robot = self.hexa_memory.get_robot_pos()
        radius = self.hexa_memory.cells_radius
        x_robot = x_robot * radius
        y_robot = y_robot * radius
        for interaction in self.memory.phenomenons :
            #calcul de la distance au robot 
            distance = math.sqrt(interaction.x**2 + interaction.y**2)
            print(distance)
            #calcul du x et y allocentric
            #x_interaction = x_robot +  math.tan(yaw) * distance
            x_prime = interaction.x * math.cos(yaw) - interaction.y * math.sin(yaw)
            #y_interaction = y_robot + math.cos(yaw) * distance
            y_prime = interaction.y * math.cos(yaw) - interaction.x * math.sin(yaw)

            print("coordonnées de base : ", interaction.x, ",",interaction.y)
            print("coordonnées converties (tjr relatif au robot) : ", x_prime, ",",y_prime)
            print("coordonnées converties ", x_prime + x_robot, ",",y_prime + y_robot)

            # on converti le tout en coordonnées pour les cells
            x_robot, y_robot = self.hexa_memory.get_robot_pos()
            nb_radius_x = int( x_prime // (radius) )
            nb_radius_y = int( y_prime // (radius) )
            x_for_hexa = nb_radius_x//2
            y_for_hexa = nb_radius_y
            y_add = 0
            x_add = 0
            if(not nb_radius_x %2 == 0):
                if(not y_robot %2 == 0):
                    x_add = 1
                    print("x_add")
                y_add = 1
                print("y_add")
            
            x_interaction =  x_for_hexa + x_robot +x_add
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
                final_status = "Unknown"
                cell_hexa = self.hexa_memory.grid[i][j]
                cell_intra = self.internal_hexa_grid.grid[i][j]
                interaction_line = [element for element in cell_intra.interactions if (element.type == "Line")]
                if(len(interaction_line) > 0) :
                    print("Cell at (",i,",",j,"has interaction line")
                interaction_blocked = [element for element in cell_intra.interactions if (element.type == "Block")]
                interaction_shock = [element for element in cell_intra.interactions if (element.type == "Shock")]
                interaction_echo = [element for element in cell_intra.interactions if (element.type == "Echolocalisation")]
                if(cell_hexa.status == 'Occupied'):
                    final_status = 'Occupied'
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_line) ):
                    final_status = "Frontier"
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_blocked)) :
                    final_status = "Blocked"
                elif(len(interaction_shock)) :
                    final_status = "Movable Obstacle"
                elif (len(interaction_echo)):
                    final_status = "Something"
                else :
                    final_status = cell_hexa.status

                cell_hexa.status = final_status

                


