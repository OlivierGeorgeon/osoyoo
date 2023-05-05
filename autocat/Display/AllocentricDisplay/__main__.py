import math
import pyglet
from ...Workspace import Workspace
from .CtrlAllocentricView import CtrlAllocentricView
from ...Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_PLACE, EXPERIENCE_FOCUS, EXPERIENCE_FLOOR
from ...Memory.AllocentricMemory.GridCell import CELL_NO_ECHO
from ...Memory.AllocentricMemory.AllocentricMemory import CELL_RADIUS

# Testing CtrlAllocentricView by displaying Allocentric Hexagonal Memory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay

workspace = Workspace()
# workspace.memory.body_memory.set_body_direction_from_azimuth(60)
workspace.memory.body_memory.body_direction_rad = math.pi / 4

# Add an echo
# i, j = workspace.memory.allocentric_memory.convert_pos_in_cell(250, 200)
i, j = point_to_cell([250, 200], CELL_RADIUS)
workspace.memory.allocentric_memory.apply_status_to_cell(i, j, EXPERIENCE_ALIGNED_ECHO, 0)
# Add focus
workspace.memory.allocentric_memory.grid[i][j].status[3] = EXPERIENCE_FOCUS
# Add no echo
workspace.memory.allocentric_memory.grid[1][5].status[2] = CELL_NO_ECHO

# Add place
workspace.memory.allocentric_memory.grid[1][0].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[1][2].status[0] = EXPERIENCE_FLOOR
workspace.memory.allocentric_memory.grid[-1][-2].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[-1][-3].status[0] = EXPERIENCE_PLACE

view_controller = CtrlAllocentricView(workspace)
view_controller.update()

pyglet.app.run()
