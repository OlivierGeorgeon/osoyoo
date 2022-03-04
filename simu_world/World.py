import math
from turtle import distance


class Cell():
    """Cell used in the World class."""

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.status = 'Empty'

class World():
    """A simulation world, in the form of grid containing cells, which can have various status
    `Author : `TKnockaert
    """

    def __init__(self,width,height,cell_size = 5):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = []
        for i in range (width):
            self.grid.append([])
            for j in range (height):
                self.grid[i].append(Cell(i,j))

        self.robot_pos_x = width//2
        self.robot_pos_y = height//2
        self.robot_angle = 0
        self.robot_width = 200
        self.robot_height = 200
        self.add_object(self.robot_pos_x,self.robot_pos_y,self.robot_width,self.robot_height,'Robot')

    def add_object(self, x, y, width, height,object_type):
        """Add an object in the world

        `Parameters : `
                `object_type` : String
                    type of the object, such as 'Line', 'Obstacle', 'Wall'
                `x` : int
                    position of the center of the object on the x axis in mm,
                    translated to cell number by the function
                `y` : int
                    position of the center of the object on the y axis in mm,
                    translated to cell number by the function
        """
        x = int(x//self.cell_size)
        y = int(y//self.cell_size)
        width = int(width//self.cell_size)
        height = int(height//self)
        
        error = 0
        if(x >= self.width or x < 0):
            error = 1
            print("Error in World.py, function add object : invalid x")
            return error
        if(y >= self.height or y < 0):
            error = 2
            print("Error in World.py, function add object : invalid y")
            return error
        if( x + width//2 >= self.width or x - width//2 < 0):
            error = 3
            print("Error in World.py, function add object : object too wide for his position")
            return error
        if(y + height >= self.height//2 or y - height//2 < 0):
            error = 4
            print("Error in World.py, function add object : object too tall for his position")
            return error
        if not isinstance(object_type, str):
            error = 5
            print("Error in World.py, function add object : ",
            "invalid object-type, must be a string, instead was : ", type(str))
            return error
        for i in range(x -width//2,x + width//2):
            for j in range(y - height//2,y + height//2):
                self.grid[i][j].status = object_type

        return error

    def remove_all_objects_of_type(self,object_type):
        """ Remove all objects of the given object_type on the grid. """
        error = 0
        removed_count = 0
        if not isinstance(object_type, str):
            error = 1
            print("Error in World.py, function remove_all_objects_of_type : ",
            "invalid object-type, must be a string, instead was : ", type(str))
            return error, removed_count
        
        for i in range (self.width):
            for j in range (self.height):
                if self.grid[i][j].status == object_type :
                    self.grid[i][j].status = 'Empty'
                    removed_count += 1
        return error, removed_count

    def rotate_robot(self,rotation):
        """Rotate the robot in the world.
        Return the real rotation that happened (i.e. if the robot hit something while rotating)

        `Parameters : `
            `rotation` : rotation in degrees

        `Return :`
            The real rotation that happened
        """
        real_rotation = 0
        while rotation > 0 :
            ""
        return real_rotation

    def move_robot(self,rotation, distance_x,distance_y):
        """Move the robot in the world """
        real_rotation = self.rotate_robot(rotation)
        self.robot_angle = (self.robot_angle + rotation) % 360
        rotation = math.radians(self.robot_angle)
        distance_x_prime = distance_x * math.cos(rotation) - distance_y * math.sin(rotation)
        distance_y_prime = distance_y * math.cos(rotation) - distance_x * math.sin(rotation)


