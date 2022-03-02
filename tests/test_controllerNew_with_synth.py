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
    hexaMemory = HexaMemory(30,30,cells_radius = 20)
    agent = Agent6(memory,hexaMemory)
    synthesizer = Synthesizer(memory, hexaMemory)
    view = EgoMemoryWindowNew()
    hexaview = HexaView()
    controller  = ControllerNew(view,agent,memory,synthesizer = synthesizer,
                 hexa_memory = hexaMemory, hexaview = hexaview)
    while (True):
        controller.loop()