import math
from Memories import MemoryNew
from Hexamemories import HexaMemory
from Hexamemories import HexaGrid

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

        delta = 400
        self.delta_x = delta
        self.delta_y = delta

        self.min_delta = 20
        self.obstacles_list = []
        self.interactions_list = []

    def reset(self):
        """ Reset the internal_hexa_grid """
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        self.obstacles_list = []
        self.last_used_id = -1
    def act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
        self.treat_echos()
        self.project_memory_on_internal_grid()
        self.synthesize()
     
    def treat_echos(self):
        """Analyse interactions created by the echolocation, to find true position of the object located """
        echos = []

        to_remove = []
        distance_max = 600
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        
        for _,inte in enumerate(self.interactions_list):
            if inte.type ==  "obstacle":
                echos.append(inte)
                to_remove.append(inte)
        for _,inte in enumerate(to_remove):
            self.interactions_list.remove(inte)
        dists = []
        for _,echo in enumerate(echos):
            x_prime = int(echo.x * math.cos(rota_radian) - echo.y * math.sin(rota_radian))
            y_prime = int(echo.y * math.cos(rota_radian) + echo.x * math.sin(rota_radian))
            # on demande ensuite à l'hexamem de nous traduire leur position en cells
            #print("ksss")
            x_prime += self.hexa_memory.robot_pos_x
            y_prime += self.hexa_memory.robot_pos_y
            dists.append(math.sqrt((x_prime - self.hexa_memory.robot_pos_x )**2 + (y_prime- self.hexa_memory.robot_pos_y)**2))
        output =[]
        for i,dist in enumerate(dists):

            if dist > distance_max :
                continue
            if i!= len(dists)-1 and (dist< dists[i+1] or abs(dist-dists[i+1]) > 100):
                print(dist, ",", abs(dist-dists[i+1]))
                if i > 0 and dist>=dists[i-1] and abs(dist-dists[i-1]) < 100:
                    continue
                output.append(echos[i])
                print("i1 : ", i)
            elif i== len(dists)-1 and dist < dists[i-1]:
                output.append(echos[i])
                print("i2 : ", i)
            
        print("len output :", len(output))
        for _,echo in enumerate(output):
            self.interactions_list.append(echo)
            #print("interactions :", len(self.interactions_list))

        
                    




    def compare_echolocation(self,interaction):
        """ Compare the coordinates of the interaction with the coordinates of the obstacles in the list,
        if the difference between the coordinates of the interaction and one known obstacle is less than self.delta_x and self.delta_y,
        return True and the obstacle, else return False, None """
        # les interactions etant egocentrés, on fait la manip pour les allocentrer
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        x_prime = int(interaction.x * math.cos(rota_radian) - interaction.y * math.sin(rota_radian))
        y_prime = int(interaction.y * math.cos(rota_radian) + interaction.x * math.sin(rota_radian))
        # on demande ensuite à l'hexamem de nous traduire leur position en cells
        #print("ksss")
        x_prime += self.hexa_memory.robot_pos_x
        y_prime += self.hexa_memory.robot_pos_y
        for obstacle in self.obstacles_list :
            #print("kss")
            # print difference between obstacle and interaction coordinates
            #print("<SYNTHESIZER> : obstacle x : ", obstacle[0], "interaction x : ", x_prime, "obstacle y : ", obstacle[1], "interaction y : ", y_prime)
            if(abs(obstacle[0] - x_prime) < self.delta_x and abs(obstacle[1] - y_prime) < self.delta_y):
                is_significant = False
                if(abs(obstacle[0] -x_prime) > self.min_delta or abs(obstacle[1] - y_prime) > self.min_delta):
                    is_significant = True

                delta_x = obstacle[0] - x_prime
                delta_y = obstacle[1] - y_prime
                return True, obstacle, is_significant, delta_x, delta_y
        return False, None, False, 0, 0

    def project_memory_on_internal_grid(self):
        """ Convert position of egocentric interactions of the memory into
        position in the allocentric representation
        """
        
        for interaction in self.interactions_list :
            corners = interaction.corners
            used_points = []
            if(interaction.id<= self.last_used_id):
                continue
            if(interaction.actual_durability > 0):
                # call compare_echolocation if the interaction is of type obstacle
                if(interaction.type == "obstacle"): # TODO : changer obstacle -> echo   
                    is_same_obstacle, obstacle, is_away_enough, obstacle_delta_x, obstacle_delta_y = self.compare_echolocation(interaction)
                    if(is_same_obstacle):
                        if not is_away_enough:
                            continue
                        #move the robot in the memory, according to the mesured delta
                        self.hexa_memory.robot_pos_x += obstacle_delta_x
                        self.hexa_memory.robot_pos_y += obstacle_delta_y
                        #print("<SYNTHESIZER> : OBSTACLE already known detected, robot has been moved by :",-obstacle_delta_x,-obstacle_delta_y)
                        if(interaction.id > self.last_used_id):
                            self.last_used_id = interaction.id
                        continue
                    else :
                        print("ks")
                        # on demande ensuite à l'hexamem de nous traduire leur position en cells
                        # les interactions etant egocentrés, on fait la manip pour les allocentrer
                        rota_radian = math.radians(self.hexa_memory.robot_angle)
                        x_prime = int(interaction.x * math.cos(rota_radian) - interaction.y * math.sin(rota_radian))
                        y_prime = int(interaction.y * math.cos(rota_radian) + interaction.x * math.sin(rota_radian))
                        x_prime += self.hexa_memory.robot_pos_x
                        y_prime += self.hexa_memory.robot_pos_y
                        self.obstacles_list.append((x_prime,y_prime))
                for _,point in enumerate(corners) :
                    rota_radian = math.radians(self.hexa_memory.robot_angle)
                    x_corner = point[0]
                    y_corner = point[1]
                    # les interactions etant egocentrés, on fait la manip pour les allocentrer
                    x_prime = int(x_corner * math.cos(rota_radian) - y_corner * math.sin(rota_radian))
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
                    except IndexError:
                        #print("<SYNTHESIZER> Interaction caused an error : x=",x,"y = ",y,"width = ", self.hexa_memory.width,"height = ",self.hexa_memory.height)
                        continue
            if(interaction.id > self.last_used_id):
                self.last_used_id = interaction.id

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
                elif(len(interaction_line) ):
                    final_status = "Frontier"
                    #print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_blocked)) :
                    final_status = "Blocked"
                elif(len(interaction_shock)) :
                    final_status = "Movable Obstacle"
                elif (len(interaction_echo)):
                    final_status = "Something"
                else :
                    final_status = cell_hexa.status

                cell_hexa.status = final_status

                


