import pyglet
from ...Workspace import Workspace
from .CtrlAllocentricView import CtrlAllocentricView

# Testing CtrlAllocentricView by displaying Allocentric Hexagonal Memory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay

workspace = Workspace()
workspace.memory.body_memory.set_body_direction_degree(60)

# Add an echo
x, y = workspace.memory.allocentric_memory.convert_pos_in_cell(250, 0)
workspace.memory.allocentric_memory.apply_status_to_cell(x, y, "Echo")

view_controller = CtrlAllocentricView(workspace)
view_controller.extract_and_convert_interactions()

pyglet.app.run()
