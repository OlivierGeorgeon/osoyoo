from HexaMemory import HexaMemory
from MemoryNew import MemoryNew
import random

class Agent6():
    """ The goal here is to create an agent that
    aim to discover and map his environment (i.e. the HexaMemory)
    so it should be attracted to cells with the "Unknown" status

    Author : TKnockaert
    """
    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory

    def action(self, outcome):
        """Return the action taken by the agent
        
        :Parameters:
            `outcome` : int
                outcome of the previous action
        :Return:
                `int` : the chosen action (0 : Go forward, 1 : Turn left, 2 : Turn right)
        """

        neighbors = self.hexa_memory.get_robot_neighbors_with_direction()
        unknown_neighbors = [ element for element in neighbors if element[0].status == "Unknown" ]
        if(len(unknown_neighbors) == 0):
            #jsp encore quoi faire ici
            print("AGENT 6 action() : no unknown neighbors")
            return random.randint(0,2)
        else :
            print("Nb neighbors : " , len(unknown_neighbors))
        target, target_direction = unknown_neighbors[0][0], unknown_neighbors[0][1]
        
        relative_direction = target_direction - self.hexa_memory.robot_orientation
        if(relative_direction < -3 ) :
            relative_direction += 6
        elif(relative_direction > 3):
            relative_direction -= 6
        
        action = 0
        match relative_direction :
            case  -1|-2|-3 :
                action = 1
            case 1|2|3 :
                action = 2
            case 0 :
                action = 0 
            case _:
                print("AGENT 6 action() : invalid relative direction : ",  relative_direction)
        return action
        
