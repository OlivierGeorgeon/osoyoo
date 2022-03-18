import pyglet
from Synthesizer import Synthesizer
from MemoryV1 import MemoryV1
from HexaMemory import HexaMemory
from HexaView import HexaView

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))


# Testing the synthesiser
if __name__ == '__main__':
    # Initialize memory
    mem = MemoryV1()
    # Add interactions to memory
    mem.add((3, 0, 0, 0, 0, 0))  # Line
    mem.add((0, 0, 0, 1, 300, -300))  # Echo

    hexa_memory = HexaMemory(20, 40, cells_radius=50)
    synthe = Synthesizer(mem, hexa_memory)

    # Project egocentric memory to hexa memory
    synthe.act()

    # Create and populate hexa view
    hexaview = HexaView()
    hexaview.extract_and_convert_interactions(hexa_memory)

    pyglet.app.run()
