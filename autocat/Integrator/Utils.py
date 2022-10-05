from pyglet import shapes
from webcolors import name_to_rgb
import math


def translate_indecisive_cell_to_pyglet(indecisive_cell, hexaMemory, batch):
    """Create a shape in the batch for the indecisive_cell"""
    x0 = 0
    y0 = 0
    (coord_x, coord_y), _, status = indecisive_cell
    radius = hexaMemory.cell_radius
    hauteur = math.sqrt((2*radius)**2 - radius**2)
    if coord_y % 2 == 0:
        x1 = x0 + coord_x * 3 * radius
        y1 = y0 + hauteur * (coord_y/2)
    else:
        x1 = x0 + (1.5 * radius) + coord_x * 3 * radius
        y1 = y0 + (hauteur/2) + (coord_y-1)/2 * hauteur

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

    color = name_to_rgb("white")
    if status == "Free":
        color = name_to_rgb("lightgreen")
    elif status == "Occupied":
        color = name_to_rgb("yellow")
    elif status == "Blocked":
        color = name_to_rgb("red")
    elif status == "Frontier":
        color = name_to_rgb("black")
    elif status == "Something":
        color = name_to_rgb("orange")

    lines = [shapes.Line(point1[0], point1[1], point2[0], point2[1], width=5, color=color, batch=batch),
             shapes.Line(point2[0], point2[1], point3[0], point3[1], width=5, color=color, batch=batch),
             shapes.Line(point3[0], point3[1], point4[0], point4[1], width=5, color=color, batch=batch),
             shapes.Line(point4[0], point4[1], point5[0], point5[1], width=5, color=color, batch=batch),
             shapes.Line(point5[0], point5[1], point6[0], point6[1], width=5, color=color, batch=batch),
             shapes.Line(point6[0], point6[1], point1[0], point1[1], width=5, color=color, batch=batch)]
    return lines
    
