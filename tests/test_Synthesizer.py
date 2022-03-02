import sys
import os
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Synthesizer import Synthesizer
from Interaction import Interaction
from MemoryV1 import MemoryV1
from HexaMemory import HexaMemory
from HexaView import HexaView

if __name__ == '__main__':
    mem = MemoryV1()
    hexaMemory = HexaMemory(20,20,cells_radius = 20)
    synthe = Synthesizer(mem, hexaMemory)
    view = HexaView()
    it = Interaction(20,20)
    mem.phenomenons.append(Interaction(200,200).red_line(41,21))
    mem.phenomenons.append(Interaction(0,0).green_circle(100,100))
    view.refresh(hexaMemory)
    time.sleep(0.2)
    synthe.act()
    view.refresh(hexaMemory)
    time.sleep(5)