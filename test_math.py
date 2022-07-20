import math
import numpy as np
from stage_titouan import HexaMemory
import random

array = [(0,0),(0,5)]
print(np.mean(array,axis=0))
print( math.dist(array[0],array[1]) )

hexa = HexaMemory(100,100)
for i in range(1000):
    ego_x, ego_y = random.randint(0,100), random.randint(0,100)
    hexa.robot_angle = random.randint(0,360)
    hexa.robot_pos_x = random.randint(0,200)
    hexa.robot_pos_y = random.randint(0,200)
    allo_x,allo_y = hexa.convert_egocentric_position_to_allocentric(ego_x, ego_y)
    #print(allo_x,allo_y)
    ego2_x, ego2_y = hexa.convert_allocentric_position_to_egocentric_translation(allo_x, allo_y)
    #print(ego2_x,ego2_y)
    if not (ego_x == ego2_x and ego_y == ego2_y) :
        print("MERDE : ego_x, ego_y, ego2_x, ego2_y : ",ego_x, ego_y, ego2_x, ego2_y)