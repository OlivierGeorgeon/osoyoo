import sys
import os
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Synthesizer import Synthesizer
from Interaction import Interaction
from MemoryV1 import MemoryV1
from HexaMemory import HexaMemory
from HexaView import HexaView
from EgoMemoryWindowNew import EgoMemoryWindowNew
from ControllerNew import ControllerNew
from Agent6 import Agent6
if __name__ == '__main__':
    memory = MemoryV1()
    hexaMemory = HexaMemory(100,200,cells_radius = 5)
    agent = Agent6(memory,hexaMemory)
    synthesizer = Synthesizer(memory, hexaMemory)

    hexaview = HexaView()
    view = EgoMemoryWindowNew()
    controller  = ControllerNew(agent,memory,view = view,synthesizer = synthesizer, 
                 hexa_memory = hexaMemory, hexaview = hexaview, automatic = False)
    controller.main()