import math
from ... Model.Hexamemories.HexaGrid import HexaGrid
from ... Misc.Utils import translate_interaction_type_to_cell_status
from ... Model.Interactions.Interaction import INTERACTION_TRESPASSING, INTERACTION_ECHO, INTERACTION_BLOCK, INTERACTION_SHOCK
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
        self.interactions_list = []
        self.max_delta = 200
        self.obstacles_list = []

    def reset(self):
        """ Reset the internal_hexa_grid """
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        self.obstacles_list = []
        self.last_used_id = -1


    def act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        #Firstly : keep only the interactions that are not already treated (id > last_used_id)
        self.interactions_list = []
        self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
        print(len(self.interactions_list))
        #Secondly : At this point self.interactions_list contains all the echolocations made by the robot, so we need to treat them to find the
        #true position of the objects echolocated
        real_echos = self.treat_echos()
        print("len real_echos :", len(real_echos))

        self.project_echos_on_internal_grid_and_correct_robot_position(real_echos)
        #Remove the echos not returned by treat_echos
        self.interactions_list= [elem for elem in self.interactions_list if elem.type != INTERACTION_ECHO] #or elem in real_echos]
        #Project the interactions on the internal_hexa_grid
        self.project_memory_on_internal_grid()
        #Synthesize the existing hexamemory and the internal_hexa_grid
        self.synthesize()

    def treat_echos(self):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == INTERACTION_ECHO)
        echo_list = [elem for elem in self.interactions_list if elem.type == INTERACTION_ECHO]
        #Compute distance between robot and echolocation for every element in echo_list
        dist_list = [math.sqrt(elem.x**2 + elem.y**2) for elem in echo_list]
        #Find all the local minimums in dist_list (dist_list[i] < dist_list[i+1] and dist_list[i] < dist_list[i-1])
        # append the corresponding echo to min_list
        min_list = [echo_list[i+1] for i,elem in enumerate(dist_list[1:-1]) if (elem<dist_list[i] and elem<dist_list[i+2])]                
        print("len(min_list)",len(min_list))
        return min_list

    def project_echos_on_internal_grid_and_correct_robot_position(self,echos):
        """Project the new echos on the internal grid,
        if an echo is close enough to a known obstacle, it should consider that it is the same and
        that the robot has an error on his position, so it should correct it"""
        rota_radian = math.radians(self.hexa_memory.robot_angle)
       #For each echo in echos compute the allocentric coordinates of the interaction
        for _, echo in enumerate(echos):
            #Compute the allocentric coordinates of the interaction
            allo_x = int(echo.x * math.cos(rota_radian) - echo.y * math.sin(rota_radian)  + self.hexa_memory.robot_pos_x)
            allo_y = int(echo.x * math.sin(rota_radian) + echo.y * math.cos(rota_radian)  + self.hexa_memory.robot_pos_y)
            #Look for an obstacle close
            close_obstacle = self.find_obstacle_close(allo_x,allo_y)
            x_obs,y_obs = close_obstacle[0],close_obstacle[1]
            if x_obs is not None and y_obs is not None :
                #If x_obs and y_obs are not None, it means we have found an obstacle close
                #Enough to consider that the robot has an error on his position
                #So we correct it
                x_diff = allo_x - x_obs
                y_diff = allo_y - y_obs
                print("Correcting robot position :",x_diff,y_diff)
                self.hexa_memory.robot_pos_x += x_diff
                self.hexa_memory.robot_pos_y += y_diff
                self.last_used_id = max(self.last_used_id, echo.id)
            else :
            #Compute the hexa_coordinates of the interaction
                cell_x,cell_y = self.hexa_memory.convert_pos_in_cell(allo_x,allo_y)
                self.internal_hexa_grid.add_interaction(cell_x,cell_y,echo)
                self.last_used_id = max(echo.id,self.last_used_id)
                self.obstacles_list.append(obstacle(allo_x,allo_y, cell_x = cell_x, cell_y = cell_y))
            
            

    def project_memory_on_internal_grid(self):
        """Project the interactions on the internal_hexa_grid"""
        #For each interaction in self.interactions_list compute the allocentric coordinates of the interaction
        #and add it to the internal_hexa_grid
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        allocentric_coordinates = []
        for _,interaction in enumerate(self.interactions_list):
             for corner in interaction.corners:
                corner_x,corner_y = corner
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        #Add the allocentric coordinates to the internal_hexa_grid
        for allocentric_coordinate,interaction in allocentric_coordinates:
            coordinate_x,coordinate_y = allocentric_coordinate
            cell_x,cell_y = self.hexa_memory.convert_pos_in_cell(coordinate_x,coordinate_y)
            self.internal_hexa_grid.add_interaction(cell_x,cell_y,interaction)
            self.last_used_id = max(interaction.id,self.last_used_id)
    

    def synthesize(self):
        """Compare the content of the hexamemory and the internal hexa grid, apply the final status of each cell to the hexa_memory"""
        for i,row in enumerate(self.internal_hexa_grid.grid):
            for j, cell in enumerate(row):
                intern_status = "Free" if len(cell.interactions) == 0 else translate_interaction_type_to_cell_status(cell.interactions[-1].type)
                current_status = self.hexa_memory.grid[i][j].status
                final_status = current_status if intern_status == "Free" else intern_status
                if(self.hexa_memory.grid[i][j].status == final_status) :
                    if intern_status != "Free" :
                        print("Augmente confidence de la cell : ",i,j)
                        self.hexa_memory.grid[i][j].confidence +=1
                else :
                    self.hexa_memory.grid[i][j].status = final_status
                    self.hexa_memory.grid[i][j].confidence = 1

    def find_obstacle_close(self,hexa_x,hexa_y):
        """Find the closest obstacle to the given hexa_coordinates"""
        #Find the closest obstacle to the given hexa_coordinates
        min_dist = float('inf')
        min_obstacle = None
        for obstacle in self.obstacles_list:
            dist = math.sqrt((obstacle.x-hexa_x)**2 + (obstacle.y-hexa_y)**2)
            if dist < min_dist:
                min_dist = dist
                min_obstacle = obstacle
        if min_dist > self.max_delta :
            return None,None
        return min_obstacle.x,min_obstacle.y

class obstacle():

    def __init__(self,x,y, cell_x = None, cell_y = None):
        self.x = x
        self.y = y
        self.cell_x = cell_x
        self.cell_y = cell_y