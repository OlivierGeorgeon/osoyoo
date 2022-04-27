from pyglet import shapes, gl
import math
from pyrr import matrix44, Quaternion
from webcolors import name_to_rgb

POINT_ECHO = 0
POINT_TRESPASS = 1
POINT_SHOCK = 2
POINT_PUSH = 3
POINT_PLACE = 4
POINT_PHENOMENON = 5


class Phenomenon:
    def __init__(self, x, y, batch, group, point_type):
        self.batch = batch
        self.group = group
        self.type = point_type
        self.is_selected = False

        if self.type == POINT_PLACE:
            # Place: Blue circle
            # self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("LightGreen"), batch=self.batch)
            self.shape = self.batch.add(3, gl.GL_TRIANGLES, self.group, ('v2i', [20, 0, -20, -20, -20, 20]),
                                        ('c3B', (144, 238, 144, 144, 238, 144, 144, 238, 144)))
        if self.type == POINT_ECHO:
            # Echo: Orange circle
            self.shape = shapes.Circle(x, y, 20, color=name_to_rgb("orange"), batch=self.batch)
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
            self.shape = shapes.Circle(x, y, 40, color=name_to_rgb("tomato"), batch=self.batch)
            # I can't find a way to access the points to move the polygon
            # self.shape = shapes.Polygon([x+20,y+0], [x+10, y+17], [x-10, y+17], [x-20, y], [x-10, y-17], [x+10, y-17],color = name_to_rgb("tomato"), batch=self.batch)

    def set_color(self, color_name=None):

        if color_name is None:
            if self.type == POINT_PLACE:
                # Place: Blue circle
                self.shape.color = name_to_rgb("LightGreen")
            if self.type == POINT_ECHO:
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
                # Pushing: yellow triangle
                self.shape.color = name_to_rgb("tomato")
        else:
            self.shape.color = name_to_rgb(color_name)

    def displace(self, displacement_matrix):
        """ Applying the displacement matrix to the phenomenon """
        # POINT PLACE are vertex list
        if self.type == POINT_PLACE:
            for i in range(0, len(self.shape.vertices)-1, 2):
                v = matrix44.apply_to_vector(displacement_matrix, [self.shape.vertices[i], self.shape.vertices[i+1], 0])
                self.shape.vertices[i], self.shape.vertices[i+1] = int(v[0]), int(v[1])
            return

        #  Rotate and translate the position
        v = matrix44.apply_to_vector(displacement_matrix, [self.shape.x, self.shape.y, 0])
        self.shape.x, self.shape.y = v[0], v[1]

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
        self.shape.delete()

    def is_near(self, x, y):
        """ If the point is near the x y coordinate, select this point and return True """
        is_near = math.dist([x, y], [self.shape.x, self.shape.y]) < 50
        if is_near:
            self.is_selected = True
        else:
            self.is_selected = False
        return is_near
