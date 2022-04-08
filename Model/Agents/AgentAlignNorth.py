import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Model.Hexamemories.HexaMemory import HexaMemory
from Model.Memories.MemoryNew import MemoryNew
import random


class AgentAlignNorth():
    """ The goal here is to create an agent that align itself to the north
    every few actions to compensate imprecisions in the evaluation of it's angle
    """
    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.has_done_init = False
        self.count_since_last_align = 0
        self.aligned = False
        self.NB_ACTIONS_BEFORE_ALIGN = 5


    def action(self, outcome):
        """If the robot hasn't align to the north in a while align him, else does random action"""
        if self.count_since_last_align >= self.NB_ACTIONS_BEFORE_ALIGN or not self.has_done_init:
            if(self.hexa_memory.azimuth > 354 or self.hexa_memory.azimuth < 5 ) and self.has_done_init:
                self.hexa_memory.robot_angle = 90
                self.count_since_last_align = 0
            else :
                self.count_since_last_align += 1
                self.has_done_init = True
                print("\n\n ALIGNALIGNALIGNALIGNALIGNALIGNALIGNALIGNALIGNALIGNALIGNALIGN \n\n")
                return 3 #si on est pas aligné on lui dit de le faire
        self.count_since_last_align += 1
        dice = random.randint(0,100)
        if(dice >30):
            return 0
        else : 
            return random.randint(1,2)
        



        return random.randint(1,3)