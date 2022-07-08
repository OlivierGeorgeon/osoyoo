import math
from ..Memory.HexaMemory.HexaGrid import HexaGrid
from ..Misc.Utils import translate_interaction_type_to_cell_status
from ..Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO
from ..Memory.HexaMemory.HexaGrid import HexaGrid
import numpy as np
# from scipy.spatial.distance import cdist
AUTOMATIC_MODE = "automatic"
MANUAL_MODE = "manual"
SCAN_DISTANCE = 600
from ..Memory.HexaMemory.HexaGrid import HexaGrid
class SynthesizerSemiAuto :
    """J'essaie de simplifier encore"""

    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)

        self.synthetizing_step = 0
        self.mode = MANUAL_MODE
        self.known_obstacles = []
        self.interactions_list = []
        self.last_used_id = -999
        self.user_action = None
        self.indecisive_cells = []
        self.decided_cells = []


        self.linking_list = []
        self.obstacle_to_find = None


        self.f_robot_action_enacted = False
        self.robot_interaction_enacted = None
        self.robot_action_todo = None


        self.last_real_echos = []
        self.last_projection_for_context =[]

    def reset(self):
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)

        self.synthetizing_step = 0
        self.mode = MANUAL_MODE
        self.known_obstacles = []
        self.interactions_list = []
        self.last_used_id = -999
        self.user_action = None
        self.indecisive_cells = []
        self.decided_cells = []


        self.linking_list = []
        self.obstacle_to_find = None


        self.f_robot_action_enacted = False
        self.robot_interaction_enacted = None
        self.robot_action_todo = None


        self.last_real_echos = []
        self.last_projection_for_context =[]

    def act(self,user_action = None):
        """ Lance toute la synthese """
        if self.mode == MANUAL_MODE:
            self.act_manual(user_action)
        elif self.mode == AUTOMATIC_MODE :
            self.act_automatic(user_action)

    def act_automatic(self,user_action):
        """act automatic"""
        # Should use the context created in the manual mode, so no new Obstacle should be added on the grid,
        # instead an echo should be linked to a known obstacle, and used to compute the correct position of the robot.
        self.user_action = user_action
        self.linking_list = []
        self.last_projection_for_context = []

        if self.synthetizing_step == 0 : # start of the synthesis
            
            
            self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
            if len(self.interactions_list )> 0:
                print("Normal start of synthesis")
                self.synthetizing_step = 0.1
                self.last_used_id = max([elem.id for elem in self.interactions_list])
                echoes = [elem for elem in self.interactions_list if elem.type == "Echo2"]
                real_echos = self.treat_echos(echoes)
                self.last_real_echos = real_echos
########
                #echo_to_print = [(elem.x,elem.y) for elem in real_echos]
                #print("len real echos :", len(real_echos), "echos : ",echo_to_print)
########
                #echo_focus = [elem for elem in self.interactions_list if elem.type == "Echo"] #temporarily removed for debugging
                echo_focus = []
                #check if the distance between any element from real_echos and each element of echo_focus is below 50
                #if so, remove the element from echo_focus
                for elem in real_echos:
                    for elem2 in echo_focus:
                        if math.sqrt((elem.x-elem2.x)**2 + (elem.y-elem2.y)**2) < 90:
                            echo_focus.remove(elem2)
                real_echos = real_echos + echo_focus
                
                self.interactions_list = [elem for elem in self.interactions_list if (elem.type != "Echo2" and elem.type != "Echo")]
                #We now have the echoes differenciated from the other interactions
                #We now have to compare the echoes with the known obstacles

########
                
                #self.linking_list, mean_translations = self.compare_echoes_with_context(real_echos,[])
                self.linking_list, mean_translations= self.compare_echoes_with_context2(real_echos,[])
                print("linking done, len of linking_list : ", len(self.linking_list))
                for echo,obstacle_object in self.linking_list:
                        coord,inte,_ = obstacle_object
                        allo_x,allo_y = self.hexa_memory.convert_egocentric_position_to_allocentric(echo.x,echo.y)
                        print("\n","coord echo : ", allo_x,allo_y, " cell : ", self.hexa_memory.convert_pos_in_cell(allo_x,allo_y) ,"\n" )
                        #print("coord obstacle : ", self.hexa_memory.convert_cell_to_pos(coord[0],coord[1]), " cell : ", coord[0], coord[1])
########

                print("\n\n MEAN TRANSLATIONS :",mean_translations)

                #We now have the echoes linked to the known obstacles
                #We have to make sure that there is no obstacle that should have been seen by the robot but wasn't
                #if the current linking is correct we should be able to find the obstacle by sending the correct action to the robot
                is_missing_obstacle,self.obstacle_to_find, egocentric_x_of_missing_obstacle, egocentric_y_of_missing_obstacle = self.look_for_missing_obstacle(self.linking_list)
                print("result of look_for_missing_obstacle : ", is_missing_obstacle, "coordinates of the obstacle : ", egocentric_x_of_missing_obstacle, egocentric_y_of_missing_obstacle)
                if is_missing_obstacle:
                    # there is a missing obstacle, we should try to find it by sending the correct action to the robot
                    self.robot_action_todo = self.create_action_to_find_missing_obstacle(self.obstacle_to_find, egocentric_x_of_missing_obstacle, egocentric_y_of_missing_obstacle)
                    self.f_robot_action_enacted = False
                    return
                #there is no missing obstacle, we will consider that the linking is correct
                self.synthetizing_step = 0.2
            else :
                self.synthetizing_step = 2
        
        if self.synthetizing_step == 0.1 : # we had a return during the previous loop in the if self.synthetizing_step == 0, which means
            # we had an obstacle to find, so we need to see if the action we send to the robot was enacted
            if  not self.f_robot_action_enacted :
                # we need to wait for the robot to enact the action
                return
            # the robot has enacted the action, we need to see if it found the missing obstacle
            missing_obstacle_found = self.has_missing_obstacle_been_found(self.obstacle_to_find,self.robot_interaction_enacted)
            if missing_obstacle_found :
                #we can consider our linking as correct so we go to the next step
                self.synthetizing_step = 0.2

            else :
                # our linking was incorrect, we need to try another one
                # TODO : we need to try another linking
                self.synthetizing_step = 0.2 # TODO : remove this line
                ""
        if self.synthetizing_step == 0.2:
            #we should now look for the correct position of the robot considering the linking between
            #the known obstacles and the echoes
            translation_between_echo_and_context = self.find_translation_between_echo_and_context(self.linking_list)
            print("Mean translation between echo and context : ", translation_between_echo_and_context)
            trans_x,trans_y = translation_between_echo_and_context
            #if the vector created by trans_x and trans_y has a norm < to a cell_radius we reset them to zero
            vector = math.sqrt(trans_x**2 + trans_y**2)
            if vector < self.hexa_memory.cell_radius:
                print("vector norm < to cell radius, putting translation to 0")
                translation_between_echo_and_context = 0,0


            #we have the translation between the known obstacles and the echoes
            #we should apply this translation to the robot position
            self.apply_translation_to_hexa_memory(translation_between_echo_and_context)
            #we have applied the translation to the robot position, our robot should now be in the right position in its hexa_memory
            #we can now proceed with the normal synthesis (project interaction, compare, synthesize)
            self.synthetizing_step = 0.3

        if self.synthetizing_step == 0.3:
            # normal synthesis (project interaction, compare, synthesize)
            self.project_interactions_on_internal_hexagrid(self.interactions_list)
            n_indecisive_cells,n_decided_cells = self.comparison_step()
            self.decided_cells = self.decided_cells + n_decided_cells + n_indecisive_cells # we consider every cell to be correct, so indecided -> decided
            self.synthesize()
            self.synthetizing_step = 2

        if self.synthetizing_step == 2:
            # we have finished the synthesis
            self.synthetizing_step = 0
                


    def act_manual(self,user_action):
        """blabla"""
        self.user_action = user_action
        if self.synthetizing_step == 0 :
            self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
            if len(self.interactions_list )> 0:
                self.last_used_id = max([elem.id for elem in self.interactions_list])
                echoes = [elem for elem in self.interactions_list if elem.type == "Echo2"]
                print("len echoes :", len(echoes))
                real_echos = self.treat_echos(echoes)
                self.last_real_echos = real_echos
                print("len real_echos :", len(real_echos))
                self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" ] #temporarily remove echo_focus for debugging
                self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo2" or elem in real_echos]
                self.project_interactions_on_internal_hexagrid(self.interactions_list)
                n_indecisive_cells,n_decided_cells = self.comparison_step()
                self.indecisive_cells = self.indecisive_cells + n_indecisive_cells
                #print(self.indecisive_cells)
                self.decided_cells = self.decided_cells + n_decided_cells
                if len(self.indecisive_cells  )> 0:
                    self.synthetizing_step = 1
                else :
                    self.synthetizing_step = 2

        if self.synthetizing_step == 1 and self.user_action is not None:
            cell_treated,decision = self.apply_user_action(self.user_action)
            self.user_action = None
            #            "on a pris la decision"
            if decision != "Not done":
                self.indecisive_cells.remove(cell_treated)
                if decision is not None:
                    self.decided_cells.append(decision)
            if len(self.indecisive_cells)  == 0 :
                self.synthetizing_step = 2

        synthesize_results = self.synthesize()
        if len(synthesize_results) > 0 :
            obstacles_in_results = [elem for elem in synthesize_results if elem[2] == "Something"]
            self.known_obstacles = self.known_obstacles + obstacles_in_results
            print("len obstacles : ",len(self.known_obstacles))

        if self.synthetizing_step == 2 :
            print("on rest tout ")
            self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
            self.interactions_list = []
            self.synthetizing_step = 0






    def treat_echos(self,echo_list):
        if(len(echo_list) ==1):
            print(echo_list[0])
        echo_list = self.revert_echoes_to_angle_distance(echo_list)
        max_delta_dist = 50
        max_delta_angle = math.radians(20)
        streaks = [[],[],[],[],[],[],[],[],[],[],[],[]]
        angle_dist = [[],[],[],[],[],[],[],[],[],[],[],[]]
        current_id = 0
        echo_list = sorted(echo_list, key=lambda elem: elem[0]) # on trie par angle, pour avoir les streak "préfaites"
        for angle,distance,interaction in echo_list :
            check = False
            for i,streak in enumerate(streaks):
                if len(streak)> 0 and check == False:
                    if any((abs(ele[1]-distance)<max_delta_dist and abs(angle - ele[0])<max_delta_angle) for ele in streak):
                        streak.append((angle,distance,interaction))
                        angle_dist[i].append((math.degrees(angle),distance))
                        check = True
            if check:
                continue
            if (len(streaks[current_id]) == 0):
                streaks[current_id].append((angle,distance,interaction))
                angle_dist[current_id].append((math.degrees(angle),distance))
            else :
                current_id = (current_id + 1)
                streaks[current_id].append((angle,distance,interaction))
                angle_dist[current_id].append((math.degrees(angle),distance))
        output = []
        for streak in streaks :
            if len(streak) == 0 :
                continue
            else :
                output.append(streak[int(len(streak)/2)][2])
        return output
    def revert_echoes_to_angle_distance(self,echo_list):
        """blabla"""
        output = []
        for elem in echo_list:
            #compute the angle using elem x and y
            angle = math.atan2(elem.y,elem.x)
            #compute the distance using elem x and y
            distance = math.sqrt(elem.x**2 + elem.y**2)
            output.append((angle,distance,elem))
        return output

    def project_interactions_on_internal_hexagrid(self,interaction_list):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list,
        and add them to the internal hexagrid"""
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        allocentric_coordinates = []
        for _,interaction in enumerate(interaction_list):
                corner_x,corner_y = interaction.x,interaction.y
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        already_used_cells = []
        for allocentric_coordinate,interaction in allocentric_coordinates:
            coordinate_x,coordinate_y = allocentric_coordinate
            cell_x,cell_y = self.hexa_memory.convert_pos_in_cell(coordinate_x,coordinate_y)
            if (cell_x,cell_y) not in already_used_cells:
                self.internal_hexa_grid.add_interaction(cell_x,cell_y,interaction)
                already_used_cells.append((cell_x,cell_y))
            self.last_used_id = max(interaction.id,self.last_used_id)

    def get_allocentric_coordinates_of_interactions(self,interaction_list):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list
        
        Return a list of ((x,y),interaction)"""
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        allocentric_coordinates = []
        for _,interaction in enumerate(interaction_list):
                corner_x,corner_y = interaction.x,interaction.y
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        return allocentric_coordinates

    def comparison_step(self):
        """Compare cell by cell between internal_hexa_grid and hexa_memory.grid
        return (indecisive_cells,decided_cells)"""
        inde_cells = []
        decided_cells = []
        for i,row in enumerate(self.internal_hexa_grid.grid):
            for j, cell in enumerate(row):
                intern_status = "Free" if len(cell.interactions) == 0 else translate_interaction_type_to_cell_status(cell.interactions[-1].type)
                current_status = self.hexa_memory.grid[i][j].status
                if self.mode == MANUAL_MODE :
                    if intern_status not in ["Free", current_status]  :
                        inde_cells.append(((i,j),cell.interactions[-1],intern_status))
                    else :
                        if len(cell.interactions) > 0 :
                            decided_cells.append(((i,j),cell.interactions[-1],intern_status))
                else : #AUTO_MODE
                    if len(cell.interactions) > 0 :
                        decided_cells.append(((i,j),cell.interactions[-1], intern_status))
        return(inde_cells,decided_cells)

    def apply_user_action(self,user_action):
        """Apply the user action to the first of the indecided_cells"""
        text,coord = user_action
        indecisive_cell,interaction,status = self.indecisive_cells[-1]
        cell_treated = (indecisive_cell,interaction,status)
        decision = "Not done"
        if text == "y": # Apply the status to the cell, so keep status
            decision = indecisive_cell,interaction,status
            print("Status applied to the cell, suggestion accepted")
        if text == "n" :# Don't do anything, act will erase indecided_cell
            decision = None
            print("Suggestion Denied")
        if text == "click" :
            decision = coord,interaction,status
            print("Suggestion accepted for cell {}".format(coord))

        return cell_treated,decision
         
    def synthesize(self):
        """Apply the decisions of the decided cells"""
        cells_treated = []
        if len(self.decided_cells) > 0 :
            for coord,inte,status in self.decided_cells:
                self.hexa_memory.grid[coord[0]][coord[1]].interactions.append(inte)
                self.hexa_memory.grid[coord[0]][coord[1]].status = status
                cells_treated.append((coord,inte,status))

        for elem  in cells_treated:
            self.hexa_memory.cells_changed_recently.append(elem[0])
            self.decided_cells.remove(elem)
        return cells_treated


    def compare_echoes_with_context(self,real_echos,linking_list):
        """Compare the real echoes with the context (known_obstacles), and create a linking between all the echoes and one obstacle"""
        linking_output = []
        used_obstacles = []
        known_obstacles = self.known_obstacles
        echos_allocentric = self.get_allocentric_coordinates_of_interactions(real_echos)
        sum_translation_x,sum_translation_y = 0,0
        x_obstacle,y_obstacle = 0,0
        nb_linking = 0
        for (x_echo,y_echo),echo_interaction in echos_allocentric :
            min_dist = 9999999999
            min_obstacle = None
            for obstacle_object in known_obstacles:
                coord,_,_ = obstacle_object
                x_obstacle,y_obstacle = self.hexa_memory.convert_cell_to_pos(coord[0],coord[1])
                #get the obstacle with the minimum distance from the echo
                dist = math.sqrt((x_echo - x_obstacle)**2 + (y_echo - y_obstacle)**2)
                #We want : 1) dist to be less than the current minimum, the obstactle not being already linked, and the linking not being in the previous linking list
                if dist < min_dist and obstacle_object not in used_obstacles and (echo_interaction,obstacle_object) not in linking_list:
                    min_dist = dist
                    min_obstacle = obstacle_object
            if min_obstacle is not None :
                #TODO : just avoided for the time being to be able to conduct some tests, but should maybe produce an error
                linking_output.append((echo_interaction,min_obstacle))
                used_obstacles.append(min_obstacle) # quoi que ? on peut peut-être utiliser le meme obstacle pour différents echo ?
                sum_translation_x += x_obstacle - x_echo
                sum_translation_y += y_obstacle - y_echo
                nb_linking += 1

        if nb_linking > 0 :
            mean_translation_x = sum_translation_x / nb_linking
            mean_translation_y = sum_translation_y / nb_linking
        return linking_output,(mean_translation_x,mean_translation_y)


    def compare_echoes_with_context2(self, real_echos, linking_list):
        """Compare the real echoes with the context (known_obstacles), and create a linking between all the echoes and one obstacle"""
        linking_output = []
        sum_distance = 0
        nb_linking = 0
        echos_allocentric = self.get_allocentric_coordinates_of_interactions(real_echos)
        obstacle_allo_coords = [ (elem,self.hexa_memory.convert_cell_to_pos(elem[0][0],elem[0][1])) for elem in self.known_obstacles]
        all_distances = {}
        for obstacle_object,(x_obstacle,y_obstacle) in obstacle_allo_coords :
                all_distances[obstacle_object] = []
                for (echo_x,echo_y),interaction in echos_allocentric :
                    #self.last_projection_for_context.append(self.hexa_memory.convert_pos_in_cell(echo_x,echo_y))
                    all_distances[obstacle_object].append((math.sqrt(((x_obstacle - echo_x)**2 + (y_obstacle - echo_y)**2)),interaction))
       
        obstacle_object_unused = [key for key in all_distances.keys()]
        echoes_unused = [elem[1] for elem in echos_allocentric]

        print("before linking :","len obstacle_object_unused : {}".format(len(obstacle_object_unused)),"len echoes_unused : {}".format(len(echoes_unused)))
        while(len(obstacle_object_unused) > 0 and len(echoes_unused) > 0):
            min = 9999999999
            min_echo = None
            min_obstacle = None  
            for obstacle_object in all_distances :
                if obstacle_object  in obstacle_object_unused:
                    for distance,echo in all_distances[obstacle_object] :
                        if echo in echoes_unused :
                            if distance < min :
                                min = distance
                                min_echo = echo
                                min_obstacle = obstacle_object
            if min_obstacle is not None and min_echo is not None:
                sum_distance += min
                nb_linking += 1
                linking_output.append((min_echo,min_obstacle))
                obstacle_object_unused.remove(min_obstacle)
                echoes_unused.remove(min_echo)
        print("after linking :","len obstacle_object_unused : {}".format(len(obstacle_object_unused)),"len echoes_unused : {}".format(len(echoes_unused)))
        return linking_output,(sum_distance/nb_linking if nb_linking > 0 else sum_distance)



    def find_translation_between_echo_and_context(self,linking_list):
        "Compute the mean of the translation between echo and obstacle in the linking list given as parameter, return the ALLOCENTRIC translation"
        if len(linking_list) == 0 :
            return 0,0
        sum_translation_x = 0
        sum_translation_y = 0
        for echo,obstacle_object in linking_list:
            (allo_x,allo_y),_ = self.get_allocentric_coordinates_of_interactions([echo])[0]
            coord,obstacle,_ = obstacle_object
            obstacle_x,obstacle_y = self.hexa_memory.convert_cell_to_pos(coord[0],coord[1])
            diff_x = allo_x - obstacle_x
            diff_y = allo_y - obstacle_y  
            sum_translation_x +=  obstacle_x - allo_x
            sum_translation_y += obstacle_y - allo_y 
        mean_translation_x = sum_translation_x/len(linking_list)
        mean_translation_y = sum_translation_y/len(linking_list)


        return mean_translation_x,mean_translation_y

    def look_for_missing_obstacle(self,linking_list):
        "Look if any obstacle known and not in the linkinglist should be visible by the robot (i.e. in the half circle of radius SCAN_DISTANCE in front of the robot)"
        if len(linking_list) == 0:
            return False, None, None, None
        robot_angle = self.hexa_memory.robot_angle
        scan_dist = SCAN_DISTANCE
        robot_pos_x = self.hexa_memory.robot_pos_x
        robot_pos_y = self.hexa_memory.robot_pos_y
        angle_calcul = math.radians(90+ robot_angle)
        x_1 = math.cos(angle_calcul) * scan_dist
        y_1= math.sin(angle_calcul) * scan_dist
        line_slope = (y_1-robot_pos_y)/(x_1-robot_pos_x)
        line_intercept = robot_pos_y - line_slope * robot_pos_x
        sign_changer = 1 if robot_angle >= 0 else -1

        # we know have a line equation in the form y = line_slope * x + line_intercept
        # we need to find if an obstacle in self.known_obstacles is over (or under depending on sign_changer) this line
        # and if it's distance to the robot is below the scan_dist

        obstacle_object_in_linkings_list = list(zip(*linking_list))[1]
        for obstacle_object in self.known_obstacles:
                if obstacle_object not in obstacle_object_in_linkings_list:
                    coord,obstacle,_ = obstacle_object

                    #TODO : FALSE, should be based on projection, not interaction
                    # first condition
                    first_condition_met = line_slope * obstacle.x + line_intercept > obstacle.y * sign_changer # TODO: Maybe problem with the sign_changer
                    # second condition
                    second_condition_met = math.sqrt((obstacle.x-robot_pos_x)**2 + (obstacle.y-robot_pos_y)**2) < scan_dist
                    if not first_condition_met or not second_condition_met:
                        #the obstacle is not scannable from the current robot position, so we skip to the next one
                        continue
                    x_robot = self.hexa_memory.robot_pos_x
                    y_robot = self.hexa_memory.robot_pos_y
                    x_obstacle,y_obstacle = self.hexa_memory.convert_cell_to_pos(coord[0],coord[1])
                    robot_angle = math.radians(self.hexa_memory.robot_angle)
                    egocentric_x_of_missing_obstacle = (x_obstacle-x_robot) * math.cos(robot_angle) - (y_obstacle-y_robot) * math.sin(robot_angle)
                    egocentric_y_of_missing_obstacle = (x_obstacle-x_robot) * math.sin(robot_angle) + (y_obstacle-y_robot) * math.cos(robot_angle)

                    return True, obstacle_object, egocentric_x_of_missing_obstacle, egocentric_y_of_missing_obstacle
        return False, None, None, None

    def apply_translation_to_hexa_memory(self,translation_between_echo_and_context):
        "Convert the egocentric translation given as parameter to an allocentric one, and apply it to the hexa_memory"
        allocentric_translation_x,allocentric_translation_y = translation_between_echo_and_context
        #allocentric_translation_x,allocentric_translation_y = self.hexa_memory.convert_egocentric_translation_to_allocentric(translation_x,translation_y)
        print("SyntheContextV2 moves robot by",allocentric_translation_x,allocentric_translation_y)
        self.hexa_memory.apply_translation_to_robot_pos(allocentric_translation_x,allocentric_translation_y)

    def has_missing_obstacle_been_found(self,obstacle_to_find,robot_action_enacted):
        "Not implemented yet"
        coord,_,_ = obstacle_to_find
        pos_x,pos_y = self.hexa_memory.convert_cell_to_pos(coord[0],coord[1])
        #comput the distance between hexamemory.robotpos and coord
        dist = math.sqrt((pos_x-self.hexa_memory.robot_pos_x)**2 + (pos_y-self.hexa_memory.robot_pos_y)**2)


        #Compare that distance with the scan that has been done
        #TODO


        if False : # if abs(dist - robot_action_enacted.scan_dist) < threshold :
            return True
        return False

    def create_action_to_find_missing_obstacle(self,obstacle_to_find, egocentric_x_of_missing_obstacle, egocentric_y_of_missing_obstacle):
        intended_interaction = {}
        intended_interaction['action'] = '+'
        intended_interaction["focus_x"] = egocentric_x_of_missing_obstacle 
        intended_interaction["focus_y"] = egocentric_y_of_missing_obstacle
        return intended_interaction


    def set_mode(self, mode):
        if mode == MANUAL_MODE or mode == AUTOMATIC_MODE:
            self.mode = mode
        else :
            print("Invalid mode for SyntheContextV2")