import random
import math
# BASED ON https://drive.google.com/file/d/1OSWNrD-VopQigvEtu1yt4ZQrEH6JO5ec/view?usp=sharing


class AgentRotator:
    """aaaaaaaaa"""
    def __init__(self, memory, hexa_memory):
        """aaa"""
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.focus_object_cell_x = None
        self.focus_object_cell_y = None
        self.sweep_done = False
        self.angle_to_object = None
        self.distance_to_object = None
        self.last_action = "0"
        self.debug_mode = False

        self.borne_basse_dist = 150  # 200
        self.borne_haute_dist = 400  # 500
        self.focus_x = None
        self.focus_y = None

        self.has_moved_last_interaction = False

    def propose_intended_interaction(self, enacted_interaction, lost_focus):
        """Propose the next intended interaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.result(enacted_interaction)
        # Compute the next intended interaction possibly including the focus
        intended_interaction = self.action(outcome, lost_focus)
        return intended_interaction

    def result(self, a):
        return {'action': self.last_action}

    def action(self, outcome, focus_lost):
        """aaa"""
        if self.focus_object_cell_x is None :
            if not (self.search_object_to_focus_on_in_hexamem()):
                if self.debug_mode :
                    print("Object to focus found : ", self.focus_object_cell_x, self.focus_object_cell_y)
                self.last_action = self.C1()
                return self.last_action
        #self.last_action = self.C6()
        if self.memory.last_enacted_interaction['floor'] == 0 :
            if not focus_lost:
                self.last_action = self.C6_bypass()
            else :
                self.last_action = self.Rotation_Focus_Lost()
        else:
            self.last_action = self.Move_Line_Crossed()
        if type(self.last_action) is dict :
            return self.last_action
        else:
            return {'action': self.last_action}

    def C6(self):
        if self.has_moved_last_interaction:
            self.has_moved_last_interaction = False
            return self.Action_Sweep_After_Move()
        else:
            return self.C2()
        
    def C6_bypass(self):
        self.has_moved_last_interaction = False
        return self.C2()

    def Action_Sweep_After_Move(self):
        #return {"action":"+", "angle":self.angle_to_object}
        return {"action": "-"}
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
        possible_moves = ["1", "2", "3", "4", "5", "6", "8"]
        if self.debug_mode:
            print("Doing random move")
        return random.choice(possible_moves)
        
    def C2(self):
        """Are we aligned to the object ?"""
        self.sweep_done = False
        self.compute_distance_and_angle_to_focus_object()
        angle = self.angle_to_object
        if angle > 180:
            angle -= 360
            self.angle_to_object -= 360
        if abs(angle) > 35 :
            if self.debug_mode :
                print("Not aligned to the object, angle to object :", angle, " doing a turn")
            return self.A3() 
        else:
            if self.debug_mode:
                print("Good angle : ", self.angle_to_object)
            return self.C3()
        
    def A3(self):
        """Turn in the direction of the object"""
        print("Angle to object too big: ", self.angle_to_object)
        self.has_moved_last_interaction = True
        action = "3" if self.angle_to_object < 0 else "1"
        return self.action_with_focus(action)

    def C3(self):
        """Are we in the good distance interval ?"""

        if self.distance_to_object > self.borne_basse_dist and self.distance_to_object < self.borne_haute_dist :
            if self.debug_mode :
                print("Good distance, distance to object :", self.distance_to_object, " do a left move")
            return self.A5()
        else:
            if self.debug_mode :
                print("Not good distance : ", self.distance_to_object)
            return self.A4()

    def A4(self):
        """We move to put ourself in the interval"""
        if self.debug_mode:
                print("Moving forward/backward to get in good distance")
        self.has_moved_last_interaction = True
        action = "8" if self.distance_to_object > self.borne_haute_dist else "2"
        return self.action_with_focus(action)

    def A5(self):
        """We move to the left"""
        self.has_moved_last_interaction = True
        action = "4"
        return self.action_with_focus(action)


    def compute_distance_and_angle_to_focus_object(self):
        """"""
        object_x, object_y = self.hexa_memory.convert_cell_to_pos(self.focus_object_cell_x,self.focus_object_cell_y)
        robot_pos_x = self.hexa_memory.robot_pos_x
        robot_pos_y = self.hexa_memory.robot_pos_y
        angle = ( math.degrees(math.atan2((object_y - robot_pos_y), (object_x - robot_pos_x))) - self.hexa_memory.robot_angle) % 360
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

    def action_with_focus(self, action,modif_focus_x = 0, modif_focus_y = 0):
        """Return the dict for the given action with the focus on the focus object"""
        object_x, object_y = self.hexa_memory.convert_cell_to_pos(self.focus_object_cell_x,self.focus_object_cell_y)
        focus_x,focus_y = self.hexa_memory.convert_allocentric_position_to_egocentric_translation(object_x, object_y)
        return {'action': action, 'focus_x': focus_x+modif_focus_x, 'focus_y': focus_y + modif_focus_y}

    def Rotation_Focus_Lost(self):
        """Rotation to the right with focus on the focus_object to try to get it back"""

        print(" AGENT ROTATOR, ROTATION TO TRY TO GET FOCUS BACK")
        return self.action_with_focus("3", modif_focus_y = -20)

    def Move_Line_Crossed(self):
        """Move left with focus on the focus_object """
        floor = self.memory.last_enacted_interaction['floor']
        if floor == 1 :
            return self.action_with_focus("4", modif_focus_y = 20)
        return self.action_with_focus("4")
        
    def last_action_had_focus(self):
        """Return True if the last action had focus"""

        return type(self.last_action) is dict and 'focus_x' in self.last_action.keys()
        #return self.memory.last_enacted_interaction['focus_x'] != None