import math
from ... Model.Hexamemories.HexaGrid import HexaGrid
from ... Misc.Utils import translate_interaction_type_to_cell_status
from ... Model.Interactions.Interaction import INTERACTION_TRESPASSING, INTERACTION_ECHO, INTERACTION_BLOCK, INTERACTION_SHOCK

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

        self.hexa_memory_change_flag = False
    def reset(self):
        """ Reset the internal_hexa_grid """
        self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
        self.obstacles_list = []
        self.last_used_id = -1


    def act(self):
        """Create phenoms based on Interactions in memory and States in hexa_memory"""
        self.interaction_step()
        if(self.synthetizing_step == 0):
            self.internal_hexa_grid = HexaGrid(self.hexa_memory.width, self.hexa_memory.height)
            #Firstly : keep only the interactions that are not already treated (id > last_used_id)
            self.indecisive_cells = []
            self.decided_cells = []
            self.interactions_list = []
            self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
            for i,row in enumerate(self.internal_hexa_grid.grid):
                for j, cell in enumerate(row):
                    cell.interactions_list = []
            print(len(self.interactions_list))
            #Secondly : At this point self.interactions_list contains all the echolocations made by the robot, so we need to treat them to find the
            #true position of the objects echolocated
            real_echos = self.treat_echos()
            print("len real_echos :", len(real_echos))
            self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
            self.project_interactions_on_internal_hexagrid()
            self.projection_step()
        if self.synthetizing_step == 2 :
            self.synthesize_step()
            self.synthetizing_step = 0


    def treat_echos(self):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == INTERACTION_ECHO)
        echo_list = [elem for elem in self.interactions_list if elem.type == INTERACTION_ECHO]
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
                print("cell_x,cell_y",cell_x,cell_y , "  already used : ", already_used_cells)
                self.internal_hexa_grid.add_interaction(cell_x,cell_y,interaction)
                already_used_cells.append((cell_x,cell_y))
            self.last_used_id = max(interaction.id,self.last_used_id)

    def projection_step(self):
        """Compare the content of the hexamemory and the internal hexa grid, depending on the mode skip to the end or ask
        the user to take a decision."""
        if self.mode == AUTOMATIC_MODE :
            self.synthetizing_step = 2
            return
        for i,row in enumerate(self.internal_hexa_grid.grid):
            for j, cell in enumerate(row):
                intern_status = "Free" if len(cell.interactions) == 0 else translate_interaction_type_to_cell_status(cell.interactions[-1].type)
                current_status = self.hexa_memory.grid[i][j].status
                if self.mode == MANUAL_MODE :
                    if intern_status not in ["Free", current_status] :
                        self.indecisive_cells.append(((i,j), intern_status))
                        self.synthetizing_step = 1 # A cell need user decision, so we enter synthetizing step 1
        self.synthetizing_step = 2 if not self.synthetizing_step==1 else 1 # If self.synthetizing_step == 1 we need user decision
        #before synthetizing, so we stay in 1 else we can synthesize right away so we go in step 2

    def interaction_step(self):
        """check if the user as made decision for every indecisive cell, and if not, loop until it has"""
        if len(self.indecisive_cells) == 0 :
            self.synthetizing_step = 2 if self.synthetizing_step==1 else 0
        return

    def synthesize_step(self):
        """If the projection is finished, synthesize"""
        if self.synthetizing_step != 2 :
            return
        #Compare the content of the hexamemory and the internal hexa grid, apply the final status of each cell to the hexa_memory        
        for _,cell in enumerate(self.decided_cells):
            self.decided_cells.remove(cell)
            if len(cell) == 3 :
                cell_to_wipe_x,cell_to_wipe_y = cell[2]
                self.hexa_memory.grid[cell_to_wipe_x][cell_to_wipe_y].status = "Free"
                pos_attendue_inte = self.hexa_memory.convert_cell_to_pos(cell_to_wipe_x,cell_to_wipe_y)
                pos_reelle_inte = self.hexa_memory.convert_cell_to_pos(cell[0][0],cell[0][1])
                diff_x = pos_reelle_inte[0] - pos_attendue_inte[0]
                diff_y = pos_reelle_inte[1] - pos_attendue_inte[1]
                print("moving robot by ",-diff_x,-diff_y)
                self.hexa_memory.robot_pos_x -= diff_x
                self.hexa_memory.robot_pos_y -= diff_y

            
            cell_x,cell_y = cell[0]
            self.hexa_memory.grid[cell_x][cell_y].status = cell[1]
            self.hexa_memory_change_flag = True
        self.synthetizing_step = 0 if len(self.indecisive_cells) == 0 else 1
   
    def apply_user_action(self,action):
        """Apply the user action concerning the last indecisive_cell"""
        text,coord = action
        indecisive_cell,status = self.indecisive_cells[-1]
        if text == "y": #Apply the status to the cell
            print("Suggestion accepted")
            self.indecisive_cells.pop()
            self.decided_cells.append((indecisive_cell,status))
        elif text == "n": #Keep the cell as it is
            print("Suggestion refused")
            self.indecisive_cells.pop()
            self.decided_cells.append((indecisive_cell,self.hexa_memory.grid[indecisive_cell[0]][indecisive_cell[1]].status))
        elif text == "click": #Give the status to the cell clicked by the user
            print("Suggestion accepted for cell ",coord)
            self.indecisive_cells.pop()
            self.decided_cells.append((coord,status,indecisive_cell))
        if len(self.indecisive_cells )== 0:
            print("sytnhese")
            self.synthesize_step()