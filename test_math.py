import math
"""
robot_angle = 45
scan_dist = 100
robot_pos_x = 0
robot_pos_y = 0
angle_calcul = math.radians(90+ robot_angle)
x1 = math.cos(angle_calcul) * scan_dist
y1= math.sin(angle_calcul) * scan_dist
line_slope = (y1-robot_pos_y)/(x1-robot_pos_x)
line_intercept = robot_pos_y - line_slope * robot_pos_x

print(x1,",",y1)





print("line_slope : ",line_slope,"\nline_intercept : ",line_intercept)
x2 = 15

print("y2 = ",x2 * line_slope + line_intercept)

"""

allo_angle = 20
#print (allo_angle - (robot_angle-90))


robot_angle = 45
x_robot = 0
y_robot = 0
x_obstacle = - 100
y_obstacle = 20

robot_angle = math.radians(45)
x_second = (x_obstacle-x_robot) * math.cos(robot_angle) - (y_obstacle-y_robot) * math.sin(robot_angle)
y_second = (x_obstacle-x_robot) * math.sin(robot_angle) + (y_obstacle-y_robot) * math.cos(robot_angle)
print("x_second : ",x_second,"\ny_second : ",y_second)