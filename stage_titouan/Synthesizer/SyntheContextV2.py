import math
from .. Memory.HexaMemory.HexaGrid import HexaGrid
from .. Misc.Utils import translate_interaction_type_to_cell_status
from ..  Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO
from .. Memory.HexaMemory.HexaGrid import HexaGrid
import numpy as np
AUTOMATIC_MODE = "automatic"
MANUAL_MODE = "manual"
from .. Memory.HexaMemory.HexaGrid import HexaGrid
class SyntheContextV2 :
    """J'essaie de simplifier encore"""

    def __init__(self,memory,hexa_memory,workspace):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)
        self.workspace = workspace

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

    def act(self,user_action = None):
        """blabla"""
        if self.mode == MANUAL_MODE:
            self.act_manual(user_action)
        elif self.mode == AUTOMATIC_MODE :
            self.act_automatic(user_action)

    def act_automatic(self,user_action):
        """act automatic"""
        # Should use the context created in the manual mode, so no new Obstacle should be added on the grid,
        # instead an echo should be linked to a known obstacle, and used to compute the correct position of the robot.
        self.user_action = user_action

        if self.synthetizing_step == 0 : # start of the synthesis
            self.synthetizing_step = 0.1 
            self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
            if len(self.interactions_list )> 0:
                self.last_used_id = max([elem.id for elem in self.interactions_list])
                echoes = [elem for elem in self.interactions_list if elem.type == "Echo"]
                real_echos = self.treat_echos_alt(echoes)
                self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo"]
                #We now have the echoes differenciated from the other interactions
                #We now have to compare the echoes with the known obstacles
                self.linking_list = self.compare_echoes_with_context(real_echos,[])
                #We now have the echoes linked to the known obstacles
                #We have to make sure that there is no obstacle that should have been seen by the robot but wasn't 
                #if the current linking is correct we should be able to find the obstacle by sending the correct action to the robot
                is_missing_obstacle,self.obstacle_to_find, action_to_enact = self.find_missing_obstacle(self.linking_list)
                if is_missing_obstacle:
                    # there is a missing obstacle, we should try to find it by sending the correct action to the robot
                    #TODO : ajouter l'envoi de l'action

                    return
                #there is no missing obstacle, we will consider that the linking is correct
                self.synthetizing_step = 0.2
        
        if self.synthetizing_step == 0.1 : # we had a return during the previous loop in the if self.synthetizing_step == 0, which means
            # we had an obstacle to find, so we need to see if the action we send to the robot was enacted
            if  not self.f_robot_action_enacted :
                # we need to wait for the robot to enact the action
                return
            # the robot has enacted the action, we need to see if it found the missing obstacle
            missing_obstacle_found = self.has_missing_obstacle_been_found(self.obstacle_to_find)
            if missing_obstacle_found :
                #we can consider our linking as correct so we go to the next step
                self.synthetizing_step = 0.2

            else :
                # our linking was incorrect, we need to try another one
                # TODO : we need to try another linking
                ""
        if self.synthetizing_step == 0.2:
            #we should now look for the correct position of the robot considering the linking between
            #the known obstacles and the echoes
            translation_between_echo_and_context = self.find_translation_between_echo_and_context(self.linking_list)
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
            self.decided_cells = self.decided_cells + n_decided_cells + n_indecisive_cells
            self.synthesize()
            self.synthetizing_step = 2
                


    def act_manual(self,user_action):
        """blabla"""
        self.user_action = user_action
        if self.synthetizing_step == 0 :
            self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
            if len(self.interactions_list )> 0:
                self.last_used_id = max([elem.id for elem in self.interactions_list])
                echoes = [elem for elem in self.interactions_list if elem.type == "Echo"]
                print("len echoes :", len(echoes))
                real_echos = self.treat_echos_alt(echoes)
                print("len real_echos : ", len(real_echos))
                self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
                self.project_interactions_on_internal_hexagrid(self.interactions_list)
                n_indecisive_cells,n_decided_cells = self.comparison_step()
                self.indecisive_cells = self.indecisive_cells + n_indecisive_cells
                print(self.indecisive_cells)
                self.decided_cells = self.decided_cells + n_decided_cells
                if len(self.indecisive_cells  )> 0:
                    print("<SyntheContextV2> synthe step passe a 1")
                    self.synthetizing_step = 1
                else :
                    self.synthetizing_step = 2

        if self.synthetizing_step == 1 and self.user_action is not None:
            print("ok on est la")
            cell_treated,decision = self.apply_user_action(self.user_action)
            self.user_action = None
            "on a pris la decision"
            if decision != "Not done":
                self.indecisive_cells.remove(cell_treated)
                if decision is not None:
                    self.decided_cells.append(decision)
            if len(self.indecisive_cells)  == 0 :
                self.synthetizing_step = 2

        synthesize_results = self.synthesize()
        if len(synthesize_results) > 0 :
            for elem in synthesize_results :
                print(elem)
            obstacles_in_results = [elem for elem in synthesize_results if elem[2] == "Something"]
            self.known_obstacles = self.known_obstacles + obstacles_in_results
            print(self.known_obstacles)
            print("len obstacles : ",len(self.known_obstacles))

        if self.synthetizing_step == 2 :
            print("on rest tout ")
            self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
            self.interactions_list = []
            self.synthetizing_step = 0



    def treat_echos(self, interactions_list):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == INTERACTION_ECHO)
        echo_list = [elem for elem in interactions_list if elem.type == INTERACTION_ECHO]
        #Compute distance between robot and echolocation for every element in echo_list
        dist_list = [math.sqrt(elem.x**2 + elem.y**2) for elem in echo_list]
        #Find all the local minimums in dist_list (dist_list[i] < dist_list[i+1] and dist_list[i] < dist_list[i-1])
        # append the corresponding echo to min_list
        min_list = [echo_list[i+1] for i,elem in enumerate(dist_list[1:-1]) if (elem<dist_list[i] and elem<=dist_list[i+2])]
        min_list = []
        min_ind_list = []
        for i,elem in enumerate(dist_list[1:-1]):
            if (elem<dist_list[i] and elem<dist_list[i+2]):
                #print("on va test")
                if( (len(min_ind_list )== 0) or (abs(min_ind_list[-1] - i+1) > 3 or abs(dist_list[min_ind_list[-1]-1] - elem) > 50 ) ):
                    #print("test ok")
                    min_list.append(echo_list[i+1])
                    min_ind_list.append(i+1)
        return min_list

    def treat_echos_alt(self,echo_list):
        """blabla"""
        echo_list = self.revert_echoes_to_angle_distance(echo_list)
        max_delta_dist = 50
        max_delta_angle = math.radians(20)
        angle_start_of_strike = -1
        angle_end_of_strike = -1
        distance_start_of_strike = -1
        distance_end_of_strike = -1
        new_strike = False
        current_strike = []
        output = []
        for angle,distance,interaction in echo_list :
            if angle_start_of_strike == -1 :
                angle_start_of_strike = angle
                distance_start_of_strike = distance
                angle_end_of_strike = angle
                distance_end_of_strike = distance
                current_strike.append(interaction)
            else :
                #if the difference between the angle and the last angle is too big or the difference between the last distance 
                #and the current distance is too big, we have a new strike else we continue the current strike
                #if we end the strike we take the interaction in the middle of it, and we add it to the output array
                print("angle : ", math.degrees(angle), "angle_end_of_strike : ", math.degrees(angle_end_of_strike), "max_delta_angle : ",math.degrees( max_delta_angle))
                print("distance :", distance, "distance_end_of_strike : ", distance_end_of_strike, "max_delta_dist : ", max_delta_dist)
                if abs(angle - angle_end_of_strike) > max_delta_angle or abs(distance - distance_end_of_strike) > max_delta_dist :
                    new_strike = True
                    output.append(current_strike[int(len(current_strike)/2)])
                    current_strike = []
                    angle_start_of_strike = angle
                    distance_start_of_strike = distance
                    angle_end_of_strike = angle
                    distance_end_of_strike = distance
                    current_strike.append(interaction)
                else :
                    current_strike.append(interaction)
                    angle_end_of_strike = angle
                    distance_end_of_strike = distance

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
                        print("\n\n<SyntheContextV2> ajout à inde_cell\n\n")
                    else :
                        if len(cell.interactions) > 0 :
                            decided_cells.append(((i,j),cell.interactions[-1],intern_status))
                else : #AUTO_MODE
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
            print(self.decided_cells)
            for coord,inte,status in self.decided_cells:
                self.hexa_memory.grid[coord[0]][coord[1]].interactions.append(inte)
                self.hexa_memory.grid[coord[0]][coord[1]].status = status
                cells_treated.append((coord,inte,status))

        for elem  in cells_treated:
            self.hexa_memory.cells_changed_recently.append(elem[0])
            self.decided_cells.remove(elem)
        return cells_treated
