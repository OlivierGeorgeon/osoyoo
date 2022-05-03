from HexaMemory import HexaMemory
from MemoryNew import MemoryNew
import random

class AgentSwing():
    """ The goal here is to create an agent that
    aim to discover and map his environment by using echolocated
    objects as "anchors".
    It should have a behavior loop that ressemble that :
        1)while no new object found :
            1.1) look for a new object, that will serve as an anchor
        2) Make a move that should keep the anchor in the field of view of the robot (i.e. in the 180° in
        front of the robot, and not too far away).
        3) Correct his position change using the anchor position
        4) Look for a new object without moving, if one is found : make it the new anchor.
        5) Go back to 2)

    Expected problem is that the robot will sometimes not find a new anchor, and will loop endlessly while
    keeping the old anchor in his FOV.

    Called swing because the robot should swing from one anchor to another like monkey on vines
    Author : TKnockaert
    """
    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.has_done_init = False
        self.anchor = None

    def action(self, outcome):
        """Return the action taken by the agent
        
        :Parameters:
            `outcome` : int
                outcome of the previous action
        :Return:
                `int` : the chosen action (0 : Go forward, 1 : Turn left, 2 : Turn right)
        """
        action = 's'
        if self.anchor is None:
        # if anchor is
          print("pas fait")
        return action
        
