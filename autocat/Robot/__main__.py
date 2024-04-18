from pyrr import matrix44
from ..Utils import head_angle_distance_to_matrix

# Testing CtrlRobot
# py -m autocat.Robot

print(matrix44.apply_to_vector(head_angle_distance_to_matrix(0, 100), [0, 0, 0]))
print(matrix44.apply_to_vector(head_angle_distance_to_matrix(90, 100), [0, 0, 0]))
print(matrix44.apply_to_vector(head_angle_distance_to_matrix(-90, 100), [0, 0, 0]))