from pyglet.gl import *
from pyglet import shapes
from Interaction import *
from webcolors import name_to_rgb
import math

"""Utils to make the project more modulable, if you decide to change the package
used for the view you should just have to create a phenomList_to_whatev 
and a phenom_to_whatev function and use it instead.
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



def rotate(x,y, radians):
    """Only rotate a point around the origin (0, 0)."""
    xx = x * math.cos(radians) + y * math.sin(radians)
    yy = -x * math.sin(radians) + y * math.cos(radians)

    return xx, yy