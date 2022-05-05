from ..  Synthesizer.SynthesizerUserInteraction import SynthesizerUserInteraction,math
class SynthesizerUserContext(SynthesizerUserInteraction):
    """Synthesizer that have two modes : 
    Manual and Automatic.
    In Manual mode, the user can interact with the synthesizer.
    In Automatic mode, the synthesizer will try to find the best action for the user.
    """
    def __init__(self,memory,hexa_memory):
        """
        :param memory: Memory object
        :param hexa_memory: HexaMemory object
        :param control_mode: "auto" or "manual"
        """
        self.memory = None
        self.hexa_memory = None
        self.internal_hexa_grid = None
        self.last_used_id = None
        self.interactions_list = None
        self.max_delta = None
        self.obstacles_list = None
        self.last_used_id_on_last_round = None
        self.mode = None

        self.indecisive_cells = None
        self.synthetizing_step = None  # 0: idle. 1: Projection ready, waiting for decision. 2: decision made, hexamem adjusted.
        self.decided_cells = None
        self.cells_to_wipe = None
        self.change_RETREAT_DISTANCE = None
        self.flag_no = None
        self.need_user_action = None

        self.indecisive_interactions = []
        super().__init__(memory,hexa_memory)

        self.AUTOMATIC_MODE = "automatic"
        self.MANUAL_MODE = "manual"
        self.current_mode = self.AUTOMATIC_MODE
        self.known_obstacles = []

    def set_mode(self, mode):
        """AUTOMATIC : synthesizer use the known context
        MANUAL : synthesizer use the user's input on divergences"""
        if mode != self.AUTOMATIC_MODE and mode != self.MANUAL_MODE:
            raise ValueError("Wrong mode : {}".format(mode))
        else :
            self.current_mode = mode



    def act(self):
        """blabla"""
        if self.current_mode == self.MANUAL_MODE:
            super().act()
        else : 
            self.interactions_list = [elem for elem in self.memory.interactions if elem.id>self.last_used_id]
            real_echos = self.treat_echos()
            self.interactions_list = [elem for elem in self.interactions_list if elem.type != "Echo" or elem in real_echos]
            self.context_analysis(real_echos)
            self.project_interactions_on_internal_hexagrid()
            self.comparison_step()

    ### treat_echos(self) is inchanged from SynthesizerUserInteraction, so we don't reimplement it
    
    def context_analysis(self, real_echos):
        """Compare the positions of the real echos with the positions of the known obstacle"""


        # First step : associate each echo with the closest known obstacle
        known_obstacles = self.known_obstacles
        dict_association = {}
        allocentric_coordinates = []
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        for _,interaction in enumerate(real_echos):
                corner_x,corner_y = interaction.x,interaction.y
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        used_obstacles = []
        for elem in allocentric_coordinates:
            min = None
            min_obstacle = None
            for obstacle in known_obstacles:
                # compute distance between obstacle and elem
                # keep the minimum in min
                distance = math.sqrt((elem[0][0]-obstacle[0])**2 + (elem[0][1]-obstacle[1])**2)
                #if bancal faut ameliorer
                if min is None or distance < min and ([item for item in used_obstacles if item[0] == obstacle] == [] or [item for item in used_obstacles if item[0] == obstacle and item[1] < distance] != []):
                    min = distance
                    min_obstacle = obstacle
                used_obstacles.append(min_obstacle,min)
                dict_association[elem] = min_obstacle,min
                
        # Second step : Look if there is a missing obstacle (known obstacle that should have been detected)
        # If there is, command the robot to scan in the direction of the obstacle
        # if we find it : nice
        # if we don't find it : we need to change the associations TODO
        a = 1

        # Third_step : Look for the position of the robot that match the best
        # the distance computed in dict_association
        # and move the robot to this position in the memory
    def project_interactions_on_internal_hexagrid(self):
        """blabla"""
        a = 1
        
