import math
from .. Memory.HexaMemory.HexaGrid import HexaGrid
from .. Misc.Utils import translate_interaction_type_to_cell_status
from ..  Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO

MANUAL_MODE = "manual"
AUTOMATIC_MODE = "automatic"

class SynthesizerUserInteraction :
    """Blabla"""

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
        self.last_used_id_on_last_round = -1
        self.mode = MANUAL_MODE

        self.indecisive_cells = []
        self.synthetizing_step = 0  # 0: idle. 1: Projection ready, waiting for decision. 2: decision made, hexamem adjusted.
        self.decided_cells = []
        self.cells_to_wipe = []
        self.change_RETREAT_DISTANCE = None
        self.flag_no = False
        self.need_user_action = False

        self.indecisive_interactions = []
    def reset(self):
        """ Reset the internal_hexa_grid """
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        self.obstacles_list = []
        self.last_used_id = -1


    def act(self):
        """blabla"""
        self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
        real_echos = self.treat_echos(self.interactions_list)
        self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
        self.project_interactions_on_internal_hexagrid()
        self.comparison_step()

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

    def project_interactions_on_internal_hexagrid(self):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list,
        and add them to the internal hexagrid"""
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        allocentric_coordinates = []
        for _,interaction in enumerate(self.interactions_list):
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
        """Compare the content of the hexamemory and the internal hexa grid, depending on the mode skip to the end or ask
        the user to take a decision."""
        for i,row in enumerate(self.internal_hexa_grid.grid):
            for j, cell in enumerate(row):
                intern_status = "Free" if len(cell.interactions) == 0 else translate_interaction_type_to_cell_status(cell.interactions[-1].type)
                current_status = self.hexa_memory.grid[i][j].status
                if self.mode == MANUAL_MODE :
                    if intern_status not in ["Free", current_status]  :
                        self.indecisive_cells.append(((i,j), intern_status))
                        self.indecisive_interactions.append(cell.interactions[-1])
                        self.synthetizing_step = 1 # A cell need user decision, so we enter synthetizing step 1
                        self.need_user_action = True
                    else :
                        if len(cell.interactions) > 0 :
                            self.hexa_memory.grid[i][j].interactions.append(cell.interactions[-1])
                else : 
                    if intern_status not in ["Free", current_status]  : 
                        self.decided_cells.append(((i,j), intern_status))
                        print ("decided \n AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA \n \n" ,self.decided_cells)
        self.synthetizing_step = 2 if not self.synthetizing_step==1 else 1 # If self.synthetizing_step == 1 we need user decision
        #before synthetizing, so we stay in 1 else we can synthesize right away so we go in step 2
        self.need_user_action = self.synthetizing_step == 1

    def apply_user_action(self,action):
        """Apply the user action concerning the last indecisive_cell"""
        text,coord = action
        indecisive_cell,status = self.indecisive_cells[-1]
        if text == "y": #Apply the status to the cell
            print("Suggestion accepted")
            self.indecisive_cells.pop()
            self.decided_cells.append((indecisive_cell,status))
            #self.hexa_memory.grid[indecisive_cell[0]][indecisive_cell[1]].interactions.append(self.indecisive_interactions.pop())
        elif text == "n": #Keep the cell as it is
            print("Suggestion refused")
            self.indecisive_cells.pop()
            self.decided_cells.append((indecisive_cell,self.hexa_memory.grid[indecisive_cell[0]][indecisive_cell[1]].status))
            self.flag_no = True
        elif text == "click": #Give the status to the cell clicked by the user
            print("Suggestion accepted for cell ",coord)
            self.indecisive_cells.pop()
            self.decided_cells.append((coord,status,indecisive_cell))
            

            # Try to find an interaction that match the status given, and approx the position of the chosen cell
            # then store the distance between that interaction and the one of the indecisive_cell
            # we should be able to use that distance to modify the RETREAT_DISTANCE of the controller
            interactions_correctes = [inte for inte in self.hexa_memory.grid[coord[0]][coord[1]].interactions if status == translate_interaction_type_to_cell_status(inte.type) ]
            if coord != indecisive_cell and len(interactions_correctes) >0:
                inte_corr_x = interactions_correctes[-1].x
                inte_corr_y = interactions_correctes[-1].y
                inte_fausse_x = self.indecisive_interactions[-1].x
                inte_fausse_y = self.indecisive_interactions[-1].y
                dist_between_corr_and_fausse_x = inte_corr_x - inte_fausse_x
                dist_between_corr_and_fausse_y = inte_corr_y - inte_fausse_y
                print("Dist between corr and fausse : ", dist_between_corr_and_fausse_x, dist_between_corr_and_fausse_y)
                if abs(interactions_correctes[-1].id - self.indecisive_interactions[-1].id) < 2 :
                    self.change_RETREAT_DISTANCE = - dist_between_corr_and_fausse_x
    def synthetize(self):
        """Synthetize the internal hexagrid according to the decided_cells"""
        for decision in self.decided_cells:
            cell,status,cell_to_wipe = None,None,None
            if len (decision) == 2 :
                cell,status = decision
                if self.flag_no :
                    self.indecisive_interactions.pop()
                    self.flag_no = False
                else :
                    if self.mode == MANUAL_MODE :
                        self.hexa_memory.grid[cell[0]][cell[1]].interactions.append(self.indecisive_interactions.pop())
            if len (decision) == 3 :
                cell,status,cell_to_wipe = decision
                cell_to_wipe_x,cell_to_wipe_y = cell_to_wipe
                pos_attendue_inte = self.hexa_memory.convert_cell_to_pos(cell_to_wipe_x,cell_to_wipe_y)
                pos_reelle_inte = self.hexa_memory.convert_cell_to_pos(cell[0],cell[1])
                diff_x = pos_reelle_inte[0] - pos_attendue_inte[0]
                diff_y = pos_reelle_inte[1] - pos_attendue_inte[1]
                print("moving robot by ",-diff_x,-diff_y)
                self.hexa_memory.robot_pos_x -= diff_x
                self.hexa_memory.robot_pos_y -= diff_y
                if cell == cell_to_wipe :
                    self.hexa_memory.grid[cell[0]][cell[1]].interactions.append(self.indecisive_interactions.pop())
                else :
                    self.indecisive_interactions.pop()
            #self.hexa_memory.grid[cell[0]][cell[1]].status = status
            self.hexa_memory.change_cell(cell[0],cell[1],status)
            
        self.decided_cells = []
        self.synthetizing_step = 2 if len(self.indecisive_cells) == 0 else 1
        self.need_user_action = self.synthetizing_step == 1

    def set_mode(self, mode):
        """AUTOMATIC : synthesizer use the known context
        MANUAL : synthesizer use the user's input on divergences"""
        if mode != AUTOMATIC_MODE and mode != MANUAL_MODE:
            raise ValueError("Wrong mode : {}".format(mode))
        else :
            self.current_mode = mode