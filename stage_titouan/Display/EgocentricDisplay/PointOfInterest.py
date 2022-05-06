from pyglet import shapes, gl
import math
from pyrr import matrix44, Quaternion
from webcolors import name_to_rgb
from ... Memory.EgocentricMemory.Interactions.Interaction import *

POINT_ECHO = INTERACTION_ECHO  # 1
POINT_TINY_ECHO = 1  # INTERACTION_ECHO
POINT_TRESPASS = INTERACTION_TRESPASSING
POINT_SHOCK = INTERACTION_SHOCK
POINT_PUSH = INTERACTION_BLOCK
POINT_PLACE = 4
POINT_PHENOMENON = 5
POINT_COMPASS = 6


class PointOfInterest:
    def __init__(self, x, y, batch, group, point_type):
        self.x = x
        self.y = y
        self.batch = batch
        self.group = group
        self.type = point_type
        self.is_selected = False
        self.reference = None

        if self.type == POINT_PLACE:
            # Place: LightGreen triangle
            self.shape = self.batch.add(3, gl.GL_TRIANGLES, self.group, ('v2i', [20, 0, -20, -20, -20, 20]),
                                        ('c3B', 3 * name_to_rgb("LightGreen") ))
        if self.type == POINT_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("orange"), batch=self.batch)
            self.shape.group = group
        if self.type == POINT_TINY_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(x, y, 7, color=name_to_rgb("orange"), batch=self.batch)
        if self.type == POINT_TRESPASS:
            # Trespassing: black dash
            self.shape = shapes.Rectangle(x, y, 10, 60, color=name_to_rgb("black"), batch=self.batch)
            self.shape.anchor_position = 5, 30
        if self.type == POINT_SHOCK:
            # Chock interaction: red triangle
            self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("red"), batch=self.batch)
        if self.type == POINT_PUSH:
            # Pushing: yellow triangle
            self.shape = shapes.Triangle(x, y, x+40, y-30, x+40, y+30, color=name_to_rgb("salmon"), batch=self.batch)
        if self.type == POINT_PHENOMENON:
            # Phenomenon: tomato
            self.shape = self.batch.add_indexed(6, gl.GL_TRIANGLES, group, [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
                            ('v2i', [x+40, y+0, x+20, y+34, x-20, y+34, x-40, y, x-20, y-34, x+20, y-34]),
                            ('c4B', 6 * (*name_to_rgb("tomato"), 128)))
        if self.type == POINT_COMPASS:
            # Place: LightGreen triangle
            self.shape = self.batch.add_indexed(4, gl.GL_TRIANGLES, self.group, [0,1,2,1,2,3],
                            ('v2i', [x+10, y, x, y-10, x, y+10, x-10, y]),
                            ('c3B', 4 * name_to_rgb("RoyalBlue") ))

    def set_color(self, color_name=None):

        if color_name is None:
            if self.type == POINT_PLACE:
                # Place: Blue circle
                self.shape.colors[0:9] = [144, 238, 144, 144, 238, 144, 144, 238, 144]
            if self.type == POINT_ECHO:
                # Echo: Orange circle
                self.shape.color = name_to_rgb("orange")
            if self.type == POINT_TINY_ECHO:
                # Echo: Orange circle
                self.shape.color = name_to_rgb("orange")
            if self.type == POINT_TRESPASS:
                # Trespassing: black dash
                self.shape.color = name_to_rgb("black")
            if self.type == POINT_SHOCK:
                # Chock interaction: red triangle
                self.shape.color = name_to_rgb("red")
            if self.type == POINT_PUSH:
                # Pushing: yellow triangle
                self.shape.color = name_to_rgb("yellow")
            if self.type == POINT_PHENOMENON:
                self.shape.colors[0:24] = 6 * (*name_to_rgb("tomato"), 128)
        else:
            if self.type == POINT_PLACE:
                self.shape.colors[0:9] = 3 * name_to_rgb(color_name)
            elif self.type == POINT_PHENOMENON:
                self.shape.colors[0:24] = 6 * (*name_to_rgb(color_name), 200)
            else:
                self.shape.color = name_to_rgb(color_name)

    def displace(self, displacement_matrix):
        """ Applying the displacement matrix to the phenomenon """
        #  Rotate and translate the position
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        self.x, self.y = v[0], v[1]

        # If compass don't displace
        if self.type == POINT_COMPASS:
            return

        # If the shape has a list of vertices (POINT PLACE)
        if hasattr(self.shape, 'vertices'):
            for i in range(0, len(self.shape.vertices)-1, 2):
                v = matrix44.apply_to_vector(displacement_matrix, [self.shape.vertices[i], self.shape.vertices[i+1], 0])
                self.shape.vertices[i], self.shape.vertices[i+1] = int(v[0]), int(v[1])
            return

        # Other points of interest have x and y
        self.shape.x, self.shape.y = self.x, self.y

        # Rotate the shapes
        if self.type == POINT_TRESPASS:  # Rotate the rectangle
            q = Quaternion(displacement_matrix)
            if q.axis[2] > 0:  # Rotate around z axis upwards
                self.shape.rotation += math.degrees(q.angle)
            else:  # Rotate around z axis downward
                self.shape.rotation += math.degrees(-q.angle)
        if self.type == POINT_PUSH or self.type == POINT_SHOCK :
            # Rotate and translate the other points of the triangle
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x2, self.shape.y2, 0])
            self.shape.x2, self.shape.y2 = v[0], v[1]
            v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x3, self.shape.y3, 0])
            self.shape.x3, self.shape.y3 = v[0], v[1]

    def delete(self):
        """ Delete the shape to remove it from the batch """
        self.shape.delete()  # Not sure whether it is necessary or not

    def select_if_near(self, x, y):
        """ If the point is near the x y coordinate, select this point and return True """
        # is_near = math.dist([x, y], [self.x, self.y]) < 20
        if math.dist([x, y], [self.x, self.y]) < 20:
            self.set_color('red')
            self.is_selected = True
        else:
            self.set_color()
            self.is_selected = False
