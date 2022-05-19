from HexaMemory import HexaMemory
from MemoryNew import MemoryNew
import random


class AgentRandom():
    """ The goal here is to create an agent that
    aim to discover and map his environment (i.e. the HexaMemory)
    so it should be attracted to cells with the "Unknown" status

    Author : TKnockaert
    """
    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.has_done_init = False

    def action(self, outcome):
        return random.randint(1,3)