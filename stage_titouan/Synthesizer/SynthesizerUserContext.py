from ..  Synthesizer.SynthesizerUserInteraction import SynthesizerUserInteraction,math
from .. Robot.RobotDefine import SCAN_DISTANCE
class SynthesizerUserContext(SynthesizerUserInteraction):
    """Synthesizer that have two modes : 
    Manual and Automatic.
    In Manual mode, the user can interact with the synthesizer.
    In Automatic mode, the synthesizer will try to find the best action for the user.
    """
    def __init__(self,memory,hexa_memory,model):
        """
        :param memory: Memory object
        :param hexa_memory: HexaMemory object
        :param control_mode: "auto" or "manual"
        """
        self.model = model
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
        self.obstacle_to_find = None

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

        for obstacle in known_obstacles:
            if obstacle not in dict_association.values():
                # we figure out if the obstacle should be scannable by the robot
                # for that it need to meet two conditions :
                # Be above the line formed by the robot pos and the point x1,y1 which is
                # the point at scan_dsitance from the robot with an angle of robot_angle+90
                # If robot_angle > 0, else below it
                # And be at a distance under scan_distance from the robot

                # first condition
                first_condition_met = line_slope * obstacle[0] + line_intercept > obstacle[1] * sign_changer
                # second condition
                second_condition_met = math.sqrt((obstacle[0]-robot_pos_x)**2 + (obstacle[1]-robot_pos_y)**2) < scan_dist
                if first_condition_met and second_condition_met:
                    # we can scan in the direction of the obstacle
                # TODO TODO TODO Command robot to tell to scan in the direction of the obstacle1    
                    """blabla lance l'action"""
                    angle_to_look = 0 # TODO compute it
                    self.model.intended_interaction["action"] = "+"
                    self.model.intended_interaction["focus_x"] = 0 #TODO
                    self.model.intended_interaction["focus_y"] = 0 #TODO
                    self.model.f_agent_action_ready = True
                    self.synthetizing_step = 3
                    self.obstacle_to_find = obstacle

 

        # Third_step : Look for the position of the robot that match the best
        # the distance computed in dict_association
        # and move the robot to this position in the memory
    def project_interactions_on_internal_hexagrid(self):
        """blabla"""
        a = 1
        

    def comparison_step(self):
        """blabla"""
        super().comparison_step() 
        if self.current_mode == self.AUTOMATIC_MODE:
            if self.synthetizing_step == 1 :
                self.need_user_action = False
                self.synthetizing_step = 2
                for cell in self.indecisive_cells :
                    self.decided_cells.append(cell)
                    self.indecisive_cells.remove(cell)


    def get_enacted_interaction_and_verify_it(self,enacted_interaction):
        """"""