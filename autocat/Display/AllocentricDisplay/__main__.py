import math
import pyglet
from ...Workspace import Workspace
from .CtrlAllocentricView import CtrlAllocentricView
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO

# Testing CtrlAllocentricView by displaying Allocentric Hexagonal Memory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay

workspace = Workspace()
# workspace.memory.body_memory.set_body_direction_from_azimuth(60)
workspace.memory.body_memory.body_direction_rad = math.pi / 4

# Add an echo
x, y = workspace.memory.allocentric_memory.convert_pos_in_cell(250, 200)
workspace.memory.allocentric_memory.apply_status_to_cell(x, y, EXPERIENCE_ALIGNED_ECHO)

view_controller = CtrlAllocentricView(workspace)
view_controller.extract_and_convert_interactions()

pyglet.app.run()
