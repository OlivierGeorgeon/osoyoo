from pyglet.gl import *
from pyglet import shapes
from webcolors import name_to_rgb
import math
import random

"""Utils to make the project more modulable, if you decide to change the package
used for the view you should just have to create a phenomList_to_whatev 
and a phenom_to_whatev function and use it instead.
"""

def world_to_pyglet(world,batch):
    """BLABLOA LINTER"""
    grid = world.grid
    shapesList = []
    x0 = 0
    y0 = 0
    radius = 2

    
    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    for i,bidule in enumerate(grid):
        for j,cell in enumerate(grid[i]):
            color_debug = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            #cell = grid[i][j]
            color = name_to_rgb("grey")
            if(cell.status == "Free"):
                color = name_to_rgb("white")
            elif(cell.status == "Occupied"):
                color = name_to_rgb("lime")
            elif(cell.status == "Blocked"):
                color = name_to_rgb("red")
            elif(cell.status == "Frontier"):
                color = name_to_rgb("black")
            elif(cell.status == "Something"):
                color = name_to_rgb("orange")
            elif(cell.status == "Robot"):
                color = name_to_rgb("lime")

            x = radius*i
            y = radius*j
            square = shapes.Rectangle(x,y, radius, radius,color = color, batch = batch)            
            shapesList.append(square)

    return shapesList