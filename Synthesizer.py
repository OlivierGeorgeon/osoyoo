from MemoryNew import MemoryNew
from HexaMemory import HexaMemory
from HexaGrid import HexaGrid
import math
class Synthesizer:
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
        yaw = self.memory.yaw()
        x_robot, y_robot = self.hexa_memory.get_robot_pos()
        radius = self.hexa_memory.radius
        x_robot = x_robot * radius
        y_robot = y_robot * radius
        for interaction in self.memory.phenomenons :
            #calcul de la distance au robot 
            distance = 0
            #calcul du x et y allocentric
            x_interaction = x_robot +  math.tan(math.radians(yaw)) * distance
            y_interaction = y_robot + math.cos(math.radians(yaw)) * distance
 
            # on converti le tout en coordonnées pour les cells
            x_interaction = x_interaction // radius
            y_interaction = y_interaction // radius

            # et on place le tout sur notre internal_grid

            self.internal_hexa_grid[x_interaction][y_interaction].interactions.append(interaction)



    def synthesize(self):
        for i in range(self.hexa_memory.width) : 
            for j in range(self.hexa_memory.height):
                final_status = "Unknown"
                cell_hexa = self.hexa_memory.grid[i][j]
                cell_intra = self.internal_hexa_grid[i][j]
                interaction_line = [element for element in cell_intra.interaction if (element.type == "Line")]
                interaction_blocked = [element for element in cell_intra.interaction if (element.type == "Block")]
                interaction_shock = [element for element in cell_intra.interaction if (element.type == "Shock")]
                interaction_echo = [element for element in cell_intra.interaction if (element.type == "Echolocalisation")]
                if(len(interaction_line) ):
                    final_status = "Frontier"
                elif(len(interaction_blocked)) :
                    final_status = "Blocked"
                elif(len(interaction_shock)) :
                    final_status = "Movable Obstacle"
                elif (len(interaction_echo)):
                    final_status = "Something"
                else :
                    final_status = cell_hexa.status

                cell_hexa.status = final_status

                


