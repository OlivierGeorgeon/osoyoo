import math
import numpy as np
from pyrr import Quaternion, Matrix44
import pyglet
from ...Workspace import Workspace
from .CtrlAllocentricView import CtrlAllocentricView
from ...Memory.AllocentricMemory.Geometry import point_to_cell
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_PLACE, \
    EXPERIENCE_FOCUS, EXPERIENCE_FLOOR, EXPERIENCE_ROBOT
from ...Memory.AllocentricMemory.AllocentricMemory import CELL_NO_ECHO
from ...Memory import CELL_RADIUS
from ...Memory.PhenomenonMemory.Affordance import Affordance
from ...Utils import quaternion_translation_to_matrix
from ...Memory.AllocentricMemory import STATUS_FLOOR, STATUS_ECHO, STATUS_2, STATUS_3, STATUS_4, COLOR_INDEX, \
    CLOCK_INTERACTION, CLOCK_NO_ECHO, CLOCK_PLACE, POINT_X, POINT_Y, IS_POOL

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
workspace.memory.allocentric_memory.grid[i][j][STATUS_3] = EXPERIENCE_FOCUS
# Add no echo
workspace.memory.allocentric_memory.grid[1][5][STATUS_2] = CELL_NO_ECHO

# Add place
workspace.memory.allocentric_memory.grid[1][0][STATUS_FLOOR] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[1][2][STATUS_FLOOR] = EXPERIENCE_FLOOR
workspace.memory.allocentric_memory.grid[-1][-2][STATUS_FLOOR] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[-1][-3][STATUS_FLOOR] = EXPERIENCE_PLACE

# Pool cells
workspace.memory.allocentric_memory.grid[-2][1][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[-1][-4][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[0][0][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[0][5][STATUS_ECHO] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[0][-5][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[1][4][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[1][-6][STATUS_FLOOR] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[1][-1][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[2][-2][STATUS_FLOOR] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[2][3][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[3][2][STATUS_FLOOR] = EXPERIENCE_PLACE
workspace.memory.allocentric_memory.grid[3][-2][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[4][2][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[2][-6][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO
workspace.memory.allocentric_memory.grid[3][-7][STATUS_ECHO] = EXPERIENCE_ALIGNED_ECHO

# Other robot
pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(math.radians(170)), [0, 0, 0])
experienceR = Experience(experience_id=2, pose_matrix=pose_matrix, experience_type=EXPERIENCE_ROBOT, clock=-3,
                         body_quaternion=workspace.memory.body_memory.body_quaternion, color_index=2)
affordanceR = Affordance(np.array([500, 500, 0]), EXPERIENCE_ROBOT, -3, 2,
                         experienceR.absolute_quaternion().copy(),
                         experienceR.polar_sensor_point().copy())
workspace.memory.phenomenon_memory.create_phenomenon(affordanceR)

workspace.memory.allocentric_memory.update_grid(workspace.memory)

workspace.memory.allocentric_memory.roll(np.array([50, 0, 0]))

# Display neighboring pools
# neighbors = pool_neighbors(-7, 0)
# for p in range(0, 6):
#     workspace.memory.allocentric_memory.grid[neighbors[p, 0], neighbors[p, 1], STATUS_1] = EXPERIENCE_ALIGNED_ECHO

# Create the view
ctrl_allocentric_view = CtrlAllocentricView(workspace)
ctrl_allocentric_view.update_view()

pyglet.app.run()
