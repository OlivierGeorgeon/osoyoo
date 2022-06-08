import sys
import random
from stage_titouan import *

cell_radius = random.randint(0,200)
hexamem = HexaMemory(200,200,cell_radius = cell_radius)
for i in range(1000000):

    x= random.randint(0,199)
    y = random.randint(0,199)
    cell_x,cell_y = hexamem.convert_pos_in_cell(x,y)
    #print("x = ",x," y = ",y," cell_x = ",cell_x," cell_y = ",cell_y)
    x_p,y_p = hexamem.convert_cell_to_pos(cell_x,cell_y)
    #print("x_p = ",x_p," y_p = ",y_p)
    if abs(x_p - x) > cell_radius :
        print("x diff : ", x_p-x, "cell_radius :", cell_radius)

    if abs(y_p - y) >  cell_radius :
        print("y diff : ", y_p-y, "cell_radius :", cell_radius)
print("fini")