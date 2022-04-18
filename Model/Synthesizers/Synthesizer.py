import math
from Model.Memories import MemoryNew
from Model.Hexamemories import HexaMemory
from Model.Hexamemories import HexaGrid
from Misc import translate_interaction_type_to_cell_status
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

        delta = 100
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
        if True :
            self.new_act()
            return
        self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
        self.treat_echos()
        self.project_memory_on_internal_grid()
        self.synthesize()

    def new_act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        #Firstly : keep only the interactions that are not already treated (id > last_used_id)
        self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
        print(len(self.interactions_list))
        #Secondly : At this point self.interactions_list contains all the echolocations made by the robot, so we need to treat them to find the
        #true position of the objects echolocated
        real_echos = self.new_treat_echos()
        print("len real_echos :", len(real_echos) )
        #Remove the echos not returned by new_treat_echos
        self.interactions_list= [elem for elem in self.memory.interactions if elem.type != 'obstacle' or elem in real_echos]
        #Project the interactions on the internal_hexa_grid
        self.new_project_memory_on_internal_grid()
        #Synthesize the existing hexamemory and the internal_hexa_grid
        self.new_synthesize()

    def new_treat_echos(self):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == 'obstacle')
        echo_list = [elem for elem in self.interactions_list if elem.type == 'obstacle']
        #Compute distance between robot and echolocation for every element in echo_list
        dist_list = [math.sqrt(elem.x**2 + elem.y**2) for elem in echo_list]
        #Find all the local minimums in dist_list (dist_list[i] < dist_list[i+1] and dist_list[i] < dist_list[i-1])
        # append the corresponding echo to min_list
        min_list = [echo_list[i+1] for i,elem in enumerate(dist_list[1:-1]) if (elem<dist_list[i] and elem<dist_list[i+2])]                
        print("len(min_list)",len(min_list))
        return min_list

    def new_project_memory_on_internal_grid(self):
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
    

    def new_synthesize(self):
        """Compare the content of the hexamemory and the internal hexa grid, apply the final status of each cell to the hexa_memory"""
        for i,row in enumerate(self.internal_hexa_grid.grid):
            for j, cell in enumerate(row):
                intern_status = "Free" if len(cell.interactions) == 0 else translate_interaction_type_to_cell_status(cell.interactions[-1].type)
                current_status = self.hexa_memory.grid[i][j].status
                final_status = current_status if intern_status == "Free" else intern_status
                self.hexa_memory.grid[i][j].status = final_status



    
     
    def treat_echos(self):
        """Analyse interactions created by the echolocation, to find true position of the object located """
        echos = []

        to_remove = []
        distance_max = 800
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
            
            if i==0 :
                if (dist<dists[i+1] or abs(dist-dists[i+1]) > 100):

                    output.append(echos[i])
            elif i >= len(dists)-1  :
                if (dist <= dists[i-1] or abs(dist-dists[i-1]) > 100):
                    #print("SYTHE echos[i] x y :",echos[i].x, echos[i].y)
                    output.append(echos[i])
            elif (dist <= dists[i-1] or abs(dist-dists[i-1]) > 100) and (dist<dists[i+1] or abs(dist-dists[i+1]) > 100):
                    #print("SYTHE echos[i] x y :",echos[i].x, echos[i].y)
                    output.append(echos[i])

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
        x_cell, y_cell = self.hexa_memory.convert_pos_in_cell(x_prime, y_prime)
        for obstacle in self.obstacles_list :
            #print("kss")
            # print difference between obstacle and interaction coordinates
            if(abs(obstacle[0] - x_prime) < self.delta_x and abs(obstacle[1] - y_prime) < self.delta_y):
                is_significant = False
                if(abs(obstacle[0] -x_prime) > self.min_delta or abs(obstacle[1] - y_prime) > self.min_delta):
                    is_significant = True

                delta_x = obstacle[0] - x_prime
                delta_y = obstacle[1] - y_prime
                #input("Is this the obstacle blabla TODO")
                self.hexa_memory.grid[x_cell][y_cell].confidence += 1
                return True, obstacle, is_significant, delta_x, delta_y
        return False, None, False, 0, 0

    def project_memory_on_internal_grid(self):
        """ Convert position of egocentric interactions of the memory into
        position in the allocentric representation
        """
        loop_nb = 0
        for interaction in self.interactions_list :
            loop_nb += 1
            #print("hopla ",interaction.type)
            corners = interaction.corners
            print("SYNTHESIZER corners", corners)
            used_points = []
            if(interaction.id<= self.last_used_id):
                print("bizarre l'affaire")
                continue
            if(interaction.actual_durability > 0):
                # call compare_echolocation if the interaction is of type obstacle
                if(interaction.type == "obstacle"): # TODO : changer obstacle -> echo   
                    is_same_obstacle, obstacle, is_away_enough, obstacle_delta_x, obstacle_delta_y = self.compare_echolocation(interaction)
                    if(False) : #if(is_same_obstacle):
                        print("oula")
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
                        # on demande ensuite à l'hexamem de nous traduire leur position en cells
                        # les interactions etant egocentrés, on fait la manip pour les allocentrer
                        rota_radian = math.radians(self.hexa_memory.robot_angle)
                        x_prime = int(interaction.x * math.cos(rota_radian) - interaction.y * math.sin(rota_radian))
                        y_prime = int(interaction.y * math.cos(rota_radian) + interaction.x * math.sin(rota_radian))
                        x_prime += self.hexa_memory.robot_pos_x
                        y_prime += self.hexa_memory.robot_pos_y
                        #print("Synthe de la deums", x_prime,y_prime)
                        self.obstacles_list.append((x_prime,y_prime))
                for _,point in enumerate(corners) :
                    rota_radian = math.radians(self.hexa_memory.robot_angle)
                    x_corner = point[0]
                    y_corner = point[1]
                    x_corner,y_corner = point
                    # les interactions etant egocentrés, on fait la manip pour les allocentrer
                    x_prime = int(x_corner * math.cos(rota_radian) - y_corner * math.sin(rota_radian))
                    y_prime = int(y_corner * math.cos(rota_radian) + x_corner * math.sin(rota_radian))
                    # on demande ensuite à l'hexamem de nous traduire leur position en cells
                    x_prime += self.hexa_memory.robot_pos_x
                    y_prime += self.hexa_memory.robot_pos_y
                    x, y = self.hexa_memory.convert_pos_in_cell(x_prime, y_prime)
                    #print("x,y (cells) :", x, y, "x_prime,y_prime:", x_prime, y_prime)
                    #print(loop_nb,"x_corners,y_corners :", x_corner, y_corner,"x_prime,y_prime :", x_prime, y_prime, " coordinates : ", x, y, " type d'inter :",interaction.type)
                    if(x,y) in used_points :
                        continue
                    if(x >= self.hexa_memory.width or y >= self.hexa_memory.height or x <  0 or y < 0):
                        continue
                    try :
                        self.internal_hexa_grid.grid[x][y].interactions.append(interaction)
                        print("Interaction added to cell ", x, y)
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
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_line) > 0):
                    final_status = "Frontier"
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_blocked) > 0) :
                    final_status = "Blocked"
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif(len(interaction_shock)> 0) :
                    final_status = "Movable Obstacle"
                    print("Cell at (",i,",",j,") final_status : ", final_status)
                elif (len(interaction_echo)> 0):
                    final_status = "Something"
                    #print("Cell at (",i,",",j,") final_status : ", final_status)
                else :
                    final_status = cell_hexa.status

                cell_hexa.status = final_status

                


