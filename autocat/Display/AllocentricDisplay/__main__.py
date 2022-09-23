import pyglet
from ...Memory.HexaMemory.HexaMemory import HexaMemory
from .AllocentricView import AllocentricView

# Testing AllocentricView by displaying HexaMemory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay
if __name__ == "__main__":

    # Create the hexa grid
    allocentric_memory = HexaMemory(width=30, height=100, cell_radius=50)
    # allocentric_memory.rotate_robot(-90)  # Rotate clockwise to align with x axis (no effect due to azimuth)

    allocentric_view = AllocentricView(hexa_memory=allocentric_memory)

    # Create the shapes to draw the cells
    allocentric_view.extract_and_convert_interactions(allocentric_memory)

    pyglet.app.run()
