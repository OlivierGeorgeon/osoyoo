from pyglet.gl import *
from pyglet import shapes
from Interaction import *
from webcolors import name_to_rgb
import math
import random

"""Utils to make the project more modulable, if you decide to change the package
used for the view you should just have to create a phenomList_to_whatev 
and a phenom_to_whatev function and use it instead.
"""


def interactionList_to_pyglet(liste,batch):
    shapesList = []
    for i in range(len(liste)):
        print
        shapesList.append(interaction_to_pyglet(liste[i],batch))
    return shapesList

def interaction_to_pyglet(interaction,batch):
    p = interaction
    x = p.x
    y = p.y
    width = p.width
    height = p.height
    shape = p.shape
    final = None
    if shape == 'Circle':
        # Green circle: Echo
        final = shapes.Circle(x, y, width, color=p.rgb, batch=batch,)
    elif shape == 'Rectangle':
        # Red dash: black line
        final = shapes.Rectangle(x, y, width, height, color=p.rgb, batch=batch)
        final.anchor_position = 10, 30
    elif shape == 'Star':
        # Triangle: collision
        # Pressing interaction: orange triangle
        final = shapes.Star(x, y, width, height, num_spikes = p.starArgs, color=p.rgb, batch=batch)
    final.opacity = (p.actual_durability/p.durability * 255)
    return final

def rotate(x,y, radians):
    """Only rotate a point around the origin (0, 0)."""
    xx = x * math.cos(radians) + y * math.sin(radians)
    yy = -x * math.sin(radians) + y * math.cos(radians)

    return xx, yy


def hexaMemory_to_pyglet(hexaMemory,batch):
    grid = hexaMemory.grid
    shapesList = []
    x0 = 0
    y0 = 0
    radius = 20

    
    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    for i in range(0, len(grid)):
        for j in range(0, len(grid[0])):
            color_debug = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            cell = grid[i][j]
            color = name_to_rgb("pink")
            if(cell.status == "Free"):
                color = name_to_rgb("white")
            elif(cell.status == "Occupied"):
                color = name_to_rgb("green")
            elif(cell.status == "Blocked"):
                color = name_to_rgb("red")

            x1 = x0
            y1 = y0
            if(j%2 == 0):
                x1 = x0 + i * 3 * radius
                y1 =y0 +  hauteur * (j/2)
            else :
                x1 = x0 + (1.5 * radius) + i * 3 * radius
                y1 = y0 + (hauteur/2) + (j-1)/2 * hauteur

                
            
            theta = 0
            theta = math.radians(theta)
            point1 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius] 
            theta = 60
            theta = math.radians(theta)
            point2 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius] 
            theta = 120
            theta = math.radians(theta)
            point3 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius] 
            theta = 180
            theta = math.radians(theta)
            point4 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]
            theta = 240
            theta = math.radians(theta)
            point5 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]
            theta = 300
            theta = math.radians(theta)
            point6 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]

            hexagon = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = color_debug, batch = batch)            
            shapesList.append(hexagon)

    return shapesList

# DEPRECATED
"""
def phenomList_to_pyglet(liste,batch):
    shapesList = []
    for i in range(len(liste)):
        shapesList.append(phenom_to_pyglet(liste[i],batch))
    return shapesList



def phenom_to_pyglet(phenom,batch):
    p = phenom
    x = p.x
    y = p.y
    width = p.width
    height = p.height
    shape = p.shape
    color = p.color
    final = None
    if shape == 0:
        # Green circle: Echo
        final = shapes.Circle(x, y, width, color=p.rgb, batch=batch)
    elif shape == 1:
        # Red dash: black line
        final = shapes.Rectangle(x, y, width, height, color=p.rgb, batch=batch)
        final.anchor_position = 10, 30
    elif shape == 2:
        # Triangle: collision
        # Pressing interaction: orange triangle
        final = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=p.rgb, batch=batch)
    return final
""" 