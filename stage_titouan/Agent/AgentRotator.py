import random
import math
class AgentRotator:
    """aaaaaaaaa"""
    def __init__(self,memory,hexa_memory):
        """aaa"""
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.focus_object_cell_x = None
        self.focus_object_cell_y = None
        self.sweep_done= False

        self.angle_to_object = None
        self.distance_to_object = None
        self.last_action = "0"

        self.debug_mode = False


        self.borne_basse_dist = 200
        self.borne_haute_dist = 500

        self.focus_x = None
        self.focus_y = None
    def result(self,a):
        return  {'action' : self.last_action}
    def action(self,outcome):
        """aaa"""
        if self.focus_object_cell_x is None :
            if not (self.search_object_to_focus_on_in_hexamem()):
                if self.debug_mode :
                    print("Object to focus found : ", self.focus_object_cell_x, self.focus_object_cell_y)
                self.last_action = self.C1()
                return self.last_action
        self.last_action = self.C2()
        return self.last_action

    def C1(self):
        """Sweep done ?"""
        return self.A1() if not self.sweep_done else self.A2()
    def A1(self):
        """Sweep"""
        self.sweep_done = True
        if self.debug_mode :
                    print("Doing sweep")
        return "-"
    def A2(self):
        """Random move"""
        self.sweep_done = False
        possible_moves = ["1","2","3","4","5","6","8"]
        if self.debug_mode :
            print("Doing random move")
        return random.choice(possible_moves)
        
    def C2(self):
        """Are we aligned to the object ?"""
        self.sweep_done = False
        self.compute_distance_and_angle_to_focus_object()
        angle = self.angle_to_object
        if angle > 180 :
            angle -= 360
        if abs(angle) > 30 :
            if self.debug_mode :
                    print("Not aligned to the object, angle to object :",angle," doing a turn")
            return self.A3() 
        else:
            if self.debug_mode :
                print("Good angle : ", self.angle_to_object)
            return self.C3()
        
    def A3(self):
        """Turn in the direction of the object"""
        print("Angle to object too big: ", self.angle_to_object)
        return "1" if self.angle_to_object < 0 else "3"

    def C3(self):
        """Are we in the good distance interval ?"""

        if self.distance_to_object > self.borne_basse_dist and self.distance_to_object < self.borne_haute_dist :
            if self.debug_mode :
                    print("Good distance, distance to object :", self.distance_to_object, " do a left move")
            return self.A5()
        else :
            if self.debug_mode :
                    print("Not good distance : ", self.distance_to_object)
            return self.A4()

    def A4(self):
        """We move to put ourself in the interval"""
        if self.debug_mode :
                    print("Moving forward/backward to get in good distance")
        return "8" if self.distance_to_object > self.borne_haute_dist else "2"
    def A5(self):
        """We move to the left"""
        return "4"


    def compute_distance_and_angle_to_focus_object(self):
        """"""
        object_x, object_y = self.hexa_memory.convert_cell_to_pos(self.focus_object_cell_x,self.focus_object_cell_y)
        robot_pos_x = self.hexa_memory.robot_pos_x
        robot_pos_y = self.hexa_memory.robot_pos_y
        if self.debug_mode :
            print(" ROBOT ANGLE : ",self.hexa_memory.robot_angle)
        third_x = math.cos(math.radians(self.hexa_memory.robot_angle)) * 100
        third_y = math.sin(math.radians(self.hexa_memory.robot_angle)) * 100
        """
        first_vector = (robot_pos_x - object_x , robot_pos_y - object_y)
        second_vector = (robot_pos_x-third_x, robot_pos_y-third_y)
        
        #Compute angle between first and second vector
        angle = math.degrees(math.atan2(second_vector[1],second_vector[0]) - math.atan2(first_vector[1],first_vector[0]))
        """
        angle = ( math.degrees(math.atan2((object_y - robot_pos_y), (object_x - robot_pos_x))) - self.hexa_memory.robot_angle) %180
        self.angle_to_object = angle
        self.distance_to_object = math.dist([robot_pos_x,robot_pos_y],[object_x,object_y])

    def search_object_to_focus_on_in_hexamem(self):
        """Look for an object to focus on"""
        grid = self.hexa_memory.grid
        for x in range(self.hexa_memory.width):
            for y in range(self.hexa_memory.height):
                if grid[x][y].status== "Something":
                    self.focus_object_cell_x = x
                    self.focus_object_cell_y = y
                    return True
        return False
