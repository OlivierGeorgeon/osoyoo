from pyglet.gl import *
from pyglet import shapes
from .. Memory.EgocentricMemory.Interactions.Interaction import Interaction,EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO,EXPERIENCE_LOCAL_ECHO, EXPERIENCE_BLOCK, EXPERIENCE_SHOCK
from webcolors import name_to_rgb
import math
import random
#from .. Model.Interactions.Interaction import INTERACTION_TRESPASSING, INTERACTION_ECHO, INTERACTION_BLOCK, INTERACTION_SHOCK

"""Utils to make the project more modulable, if you decide to change the package
used for the view you should just have to create a phenomList_to_whatev 
and a phenom_to_whatev function and use it instead.
"""

# def memory_to_pyglet(memory,batch):
#     print("memoire len",len(memory.interactions))
#     return interactionList_to_pyglet(memory.interactions,batch)

# def interactionList_to_pyglet(liste,batch):
#      shapesList = []
#      for i in range(len(liste)):
#          shapesList.append(interaction_to_pyglet(liste[i],batch))
#      return shapesList

# def interaction_to_pyglet(interaction,batch):
#      p = interaction
#      x = p.x
#      y = p.y
#      width = p.width
#      height = p.height
#      shape = p.shape
#      final = None
#      if shape == 'Circle':
#          # Green circle: Echo
#          final = shapes.Circle(x, y, width, color=p.rgb, batch=batch,)
#      elif shape == 'Rectangle':
#          # Red dash: black line
#          final = shapes.Rectangle(x, y, width, height, color=p.rgb, batch=batch)
#          final.anchor_position = 0, height/2  # 10, 30
#      elif shape == 'Star':
#          # Triangle: collision
#          # Pressing interaction: orange triangle
#          final = shapes.Star(x, y, width, height, num_spikes = p.starArgs, color=p.rgb, batch=batch)
#      final.opacity = (p.durability / p.durability * 255)
#
#      final.rotation = p.rotation
#      return final
#
# def rotate(x,y, radians):
#     """Only rotate a point around the origin (0, 0)."""
#     xx = x * math.cos(radians) + y * math.sin(radians)
#     yy = -x * math.sin(radians) + y * math.cos(radians)
#
#     return xx, yy
#

def hexaMemory_to_pyglet(hexaMemory,batch):
    """Convert the given hexaMemory to pyglet shapes"""
    grid = hexaMemory.grid
    shapesList = []
    x0 = 0
    y0 = 0
    #radius = 20
    radius = hexaMemory.cell_radius
    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    for i in range(0, len(grid)):
        for j in range(0, len(grid[0])):
            robot = False
            color_debug = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            cell = grid[i][j]

            if cell.occupied :
                color = name_to_rgb("slateBlue")
                robot = True
            else : 
                color = name_to_rgb("white")
                if(cell.status == "Free"):
                    color = name_to_rgb("lightgreen")
                elif(cell.status == "Occupied"):
                    color = name_to_rgb("yellow")
                    robot = True
                
                elif(cell.status == "Blocked"):
                    color = name_to_rgb("red")
                elif(cell.status == "Frontier"):
                    color = name_to_rgb("black")
                elif(cell.status == "Something"):
                    color = name_to_rgb("orange")
                    r,g,b = color
                    confidence = hexaMemory.grid[i][j].confidence
                    factor = 10
                    r = min(255,r + confidence*factor)
                    g = min(255,g + confidence*factor)
                    b = min(255,b + confidence*factor)
                    color = r,g,b

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

            hexagon = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = color, batch = batch)            
            shapesList.append(hexagon)
            if(robot):
                theta = math.radians(hexaMemory.robot_angle)
                x2 = radius * math.cos(theta) + x1
                y2 = radius * math.sin(theta) + y1
                line = shapes.Line(x1,y1,x2,y2,width = 15,color = name_to_rgb("yellow"), batch = batch)
                shapesList.append(line)

    return shapesList

def recently_changed_to_pyglet(hexaMemory,batch,to_reset = [],projections = []):
    """Convert the cells in hexaMemory.cells_changed_recently,to_reset and projections 
    to pyglet shapes"""
    cell_list = hexaMemory.cells_changed_recently + to_reset + projections
    shapesList = []
    x0 = 0
    y0 = 0
    #radius = 20
    radius = hexaMemory.cell_radius
    grid = hexaMemory.grid
    
    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    for (i,j) in cell_list :
            robot = False
            color_debug = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            cell = grid[i][j]

            if cell.occupied :
                color = name_to_rgb("darkslateBlue")
                robot = True
            else : 
                color = name_to_rgb("white")
                if(cell.status == "Free"):
                    color = name_to_rgb("lightgreen")
                elif(cell.status == "Occupied"):
                    color = name_to_rgb("yellow")
                    robot = True
                
                elif(cell.status == "Blocked"):
                    color = name_to_rgb("red")
                elif(cell.status == "Frontier"):
                    color = name_to_rgb("black")
                elif(cell.status == "Something"):
                    color = name_to_rgb("orange")
                    r,g,b = color
                    confidence = hexaMemory.grid[i][j].confidence
                    factor = 10
                    r = min(255,r + confidence*factor)
                    g = min(255,g + confidence*factor)
                    b = min(255,b + confidence*factor)
                    color = r,g,b

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
            if (i,j) in projections :
                color = name_to_rgb("pink")
                print("PINKKKKKKKKKKKKK")
            hexagon = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = color, batch = batch)            
            shapesList.append(hexagon)
            if(robot):
                theta = math.radians(hexaMemory.robot_angle)
                x2 = radius * math.cos(theta) + x1
                y2 = radius * math.sin(theta) + y1
                line = shapes.Line(x1,y1,x2,y2,width = 15,color = name_to_rgb("yellow"), batch = batch)
                shapesList.append(line)

    return shapesList

def translate_interaction_type_to_cell_status(type):
    """Free Blocked Occupied Frontier Something"""
    if(type == EXPERIENCE_FLOOR):
        return "Frontier"
    elif(type == EXPERIENCE_SHOCK or type == EXPERIENCE_BLOCK):
        return "Blocked"
    elif(type == EXPERIENCE_ALIGNED_ECHO):
        return "Something"
    elif(type == EXPERIENCE_LOCAL_ECHO):
        return "Something"
    print("Problemo problemo utils translate mauvaise interaction type : ", type)
    return "Free"


def translate_indecisive_cell_to_pyglet(indecisive_cell,hexaMemory,batch):
    """blabla"""
    x0 = 0
    y0 = 0
    (coord_x, coord_y),_, status = indecisive_cell
    radius = hexaMemory.cell_radius
    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    if(coord_y%2 == 0):
        x1 = x0 + coord_x * 3 * radius
        y1 =y0 +  hauteur * (coord_y/2)
    else :
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
    if(status == "Free"):
        color = name_to_rgb("lightgreen")
    elif(status == "Occupied"):
        color = name_to_rgb("yellow")
    elif(status == "Blocked"):
        color = name_to_rgb("red")
    elif(status == "Frontier"):
        color = name_to_rgb("black")
    elif(status == "Something"):
        color = name_to_rgb("orange")

    lines = []
    lines.append(shapes.Line(point1[0],point1[1],point2[0],point2[1],width = 5,color = color, batch = batch))
    lines.append(shapes.Line(point2[0],point2[1],point3[0],point3[1],width = 5,color = color, batch = batch))
    lines.append(shapes.Line(point3[0],point3[1],point4[0],point4[1],width = 5,color = color, batch = batch))
    lines.append(shapes.Line(point4[0],point4[1],point5[0],point5[1],width = 5,color = color, batch = batch))
    lines.append(shapes.Line(point5[0],point5[1],point6[0],point6[1],width = 5,color = color, batch = batch)) 
    lines.append(shapes.Line(point6[0],point6[1],point1[0],point1[1],width = 5,color = color, batch = batch))
    return lines
    
