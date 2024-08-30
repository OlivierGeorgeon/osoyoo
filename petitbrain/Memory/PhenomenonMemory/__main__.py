import matplotlib.pyplot as plt
from .PhenomenonCategory import oval_shape, rectangular_shape
from ...Utils import azimuth_to_quaternion
from ...Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_OUTSIDE_Y, ROBOT_CHASSIS_X, ROBOT_CHASSIS_Y

# Testing the phenomenon category shapes
# py -m autocat.Memory.PhenomenonMemory


circle_points = oval_shape(1100, 800, azimuth_to_quaternion(20))
robot_points = rectangular_shape(ROBOT_FLOOR_SENSOR_X, ROBOT_OUTSIDE_Y)

# Plot the circle
plt.figure(figsize=(6, 6))
plt.plot(circle_points[:, 0], circle_points[:, 1], marker='o', linestyle='', color='k', label='terrain points')
plt.plot(robot_points[:, 0], robot_points[:, 1], marker='o', linestyle='', color='c', label='robot points')

# Set plot properties
plt.title('terrain')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(color='gray', linestyle='--', linewidth=0.5)
plt.legend()
plt.axis('equal')  # Ensure equal scaling of axes

# Show the plot
plt.show()
