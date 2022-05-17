import math
from .. Memory.HexaMemory.HexaGrid import HexaGrid
from .. Misc.Utils import translate_interaction_type_to_cell_status
from ..  Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO
from .. Memory.HexaMemory.HexaGrid import HexaGrid
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

    def act(self):
        """blabla"""
        if self.mode == MANUAL_MODE:
            self.act_manual()
        elif self.mode == AUTOMATIC_MODE :
            self.act_automatic()

    def act_automatic(self):
        print("not implemented yet")

    def act_manual(self):
        """blabla"""
        if self.synthetizing_step == 0 :
            self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
            echoes = [elem for elem in self.interactions_list if elem.type == "Echo"]
            real_echos = self.treat_echos(echoes)
            self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
            self.project_interactions_on_internal_hexagrid(self.interactions_list)
            self.indecisive_cells,self.decided_cells = self.comparison_step()
            if len(self.indecisive_cells  )> 0:
                self.synthetizing_step = 1
            else :
                self.synthetizing_step = 2

        if self.synthetizing_step == 1 and self.user_action is not None:
            cell_treated,decision = self.apply_user_action(self.user_action)
            self.user_action = None
            if decision is not "Not done":
                self.indecisive_cells.remove(cell_treated)
                if decision is not None:
                    self.decided_cells.append(decision)

        synthesize_results = self.synthesize()
        self.known_obstacles.append([elem for elem in synthesize_results if elem[2] == "Obstacle"])

        if self.synthetizing_step == 2 :
            self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
            self.interactions_list = []



    def treat_echos(self, interactions_list):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == INTERACTION_ECHO)
        echo_list = [elem for elem in interactions_list if elem.type == INTERACTION_ECHO]
        #Compute distance between robot and echolocation for every element in echo_list
        dist_list = [math.sqrt(elem.x**2 + elem.y**2) for elem in echo_list]
        #Find all the local minimums in dist_list (dist_list[i] < dist_list[i+1] and dist_list[i] < dist_list[i-1])
        # append the corresponding echo to min_list
        min_list = [echo_list[i+1] for i,elem in enumerate(dist_list[1:-1]) if (elem<dist_list[i] and elem<dist_list[i+2])]
        min_list = []
        min_ind_list = []
        for i,elem in enumerate(dist_list[1:-1]):
            if (elem<dist_list[i] and elem<dist_list[i+2]):
                #print("on va test")
                if( (len(min_ind_list )== 0) or (abs(min_ind_list[-1] - i+1) > 3 or abs(dist_list[min_ind_list[-1]-1] - elem) > 50 ) ):
                    #print("test ok")
                    min_list.append(echo_list[i+1])
                    min_ind_list.append(i+1)

        print("len(min_list)",len(min_list))
        return min_list

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
                    else :
                        if len(cell.interactions) > 0 :
                            decided_cells.append((i,j),cell.interactions[-1],intern_status)
                else : #AUTO_MODE
                        decided_cells.append(((i,j),cell.interactions[-1], intern_status))
        return(inde_cells,decided_cells)

    def apply_user_action(self,user_action):
        """Apply the user action to the first of the indecided_cells"""
        print("FAUTCHANGER TODO TODO")
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
        for coord,inte,status in self.decided_cells:
            self.hexa_memory.grid[coord[0]][coord[1]].interactions.append(inte)
            self.hexa_memory.grid[coord[0]][coord[1]].status = status
            cells_treated.append((coord,inte,status))

        for elem  in cells_treated:
            self.decided_cells.remove(elem)
        return cells_treated
