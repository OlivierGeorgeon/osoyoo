# from .HexaGrid import HexaGrid
from .AllocentricMemory import AllocentricMemory
from .Hexagonal_geometry import CELL_RADIUS
from .test_AllocentricMemory import test_move, test_convert_pos_in_cell

# Testing Allocentric Memory
# py -m autocat.Memory.AllocentricMemory

allocentric_memory = AllocentricMemory(10, 11, CELL_RADIUS)
# Displaying the hexagonal grid in the console.
print(allocentric_memory)

# print("Copy: ")
# print(allocentric_memory.save())
# print("North neighbor of (2,2):", hx.get_neighbor_in_direction(2, 2, 0))
# print("All neighbors of 2,2 : ", hx.get_all_neighbors(2, 2))

error = 0
try:
    error = test_convert_pos_in_cell()
    assert (error == 0)
    print("Every test in test_convert_pos_in_cell(hx.robot_pos_x, hx.robot_pos_y) passed without error")
except AssertionError:
    print("test_convert_robot_pos_in_robot_cell failed with error : ", error)

try:
    error = test_move()
    assert (error == 0)
    print("Every test in test_move passed without error")
except AssertionError:
    print("test_move failed with error : ", error)

