import pyglet
from ...Memory.HexaMemory.HexaMemory import HexaMemory
from .AllocentricView import AllocentricView

# Testing AllocentricView by displaying HexaMemory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay
if __name__ == "__main__":

    # Create the hexa grid
    hexagonal_memory = HexaMemory(width=30, height=100, cell_radius=50)

    allocentric_view = AllocentricView(hexa_memory=hexagonal_memory)

    # Create the shapes to draw the cells
    allocentric_view.extract_and_convert_interactions(hexagonal_memory)

    pyglet.app.run()
