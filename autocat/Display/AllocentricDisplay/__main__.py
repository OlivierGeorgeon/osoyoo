import math
import numpy as np
from pyrr import Quaternion
import pyglet
from ...Workspace import Workspace
from .CtrlAllocentricView import CtrlAllocentricView
from ...Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_PLACE, \
    EXPERIENCE_FOCUS, EXPERIENCE_FLOOR, EXPERIENCE_ROBOT
from ...Memory.AllocentricMemory.GridCell import CELL_NO_ECHO
from ...Memory.AllocentricMemory.Hexagonal_geometry import CELL_RADIUS
from ...Memory.PhenomenonMemory.Affordance import Affordance

# Testing CtrlAllocentricView by displaying Allocentric Hexagonal Memory
# Hover the grid to display the mouse position
# py -m autocat.Display.AllocentricDisplay

workspace = Workspace('PetiteIA', '3')
# workspace.memory.body_memory.set_body_direction_from_azimuth(60)
workspace.memory.body_memory.body_quaternion = Quaternion.from_z_rotation(math.pi / 4)

# Add an echo
# i, j = workspace.memory.allocentric_memory.convert_pos_in_cell(250, 200)
i, j = point_to_cell([250, 200], CELL_RADIUS)
workspace.memory.allocentric_memory.apply_status_to_cell(i, j, EXPERIENCE_ALIGNED_ECHO, 0, 0)
# Add focus
workspace.memory.allocentric_memory.grid[i][j].status[3] = EXPERIENCE_FOCUS
# Add no echo
workspace.memory.allocentric_memory.grid[1][5].status[2] = CELL_NO_ECHO

# Add place
workspace.memory.allocentric_memory.grid[1][0].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[1][2].status[0] = EXPERIENCE_FLOOR
workspace.memory.allocentric_memory.grid[-1][-2].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[-1][-3].status[0] = EXPERIENCE_PLACE

# Pool cells
workspace.memory.allocentric_memory.grid[-2][1].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[-1][-4].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[0][0].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[0][5].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[0][-5].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[1][4].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[1][-6].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[1][-1].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[2][-2].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[2][3].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[3][2].status[0] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[3][-2].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[4][2].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[2][-6].status[0] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[3][-7].status[0] = EXPERIENCE_ALIGNED_ECHO

# Interesting pool
workspace.memory.allocentric_memory.most_interesting_pool(0)

# Other robot
experienceR = Experience([200, 200, 0],  EXPERIENCE_ROBOT, math.radians(-135), -3, experience_id=2, color_index=2)
affordanceR = Affordance(np.array([500, 500, 0]), experienceR)
workspace.memory.phenomenon_memory.create_phenomenon(affordanceR)

view_controller = CtrlAllocentricView(workspace)
view_controller.update_view()

pyglet.app.run()
