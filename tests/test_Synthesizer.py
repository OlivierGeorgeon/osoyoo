import pyglet
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Synthesizer import Synthesizer
from MemoryV1 import MemoryV1
from HexaMemory import HexaMemory
from HexaView import HexaView
from EgoMemoryWindowNew import EgoMemoryWindowNew




# Testing the synthesiser
if __name__ == '__main__':
    # Initialize memory
    mem = MemoryV1()
    # Add interactions to memory
    mem.add((3, 0, 0, 0, 0, 0))  # Line
    mem.add((0, 0, 0, 1, 300, -300))  # Echo

    hexa_memory = HexaMemory(20, 60, cells_radius=40)
    synthesizer = Synthesizer(mem, hexa_memory)
    synthesizer.act()

    # Create and populate hexa view
    hexaview = HexaView()
    # hexa_memory.move(30, 0, 0)
    hexaview.extract_and_convert_interactions(hexa_memory)

    @hexaview.event
    def on_text(text):
        """ Receiving the action from the window and updating the position of the environment """
        translation = [0, 0]
        rotation = 0
        if text == "8":  # Move forward
            translation[0] = 180
        if text == "2":  # Move forward
            translation[0] = -180
        if text == "1":  # Turn left
            rotation = 60
        if text == "3":  # Turn right
            rotation = -60

        hexa_memory.move(rotation, translation[0], translation[1])
        synthesizer.act()
        hexaview.extract_and_convert_interactions(hexa_memory)

    pyglet.app.run()
