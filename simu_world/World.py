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

        self.x_robot = width//2
        self.y_robot = height//2
        self.robot_angle = 0
        self.robot_width = 200
        self.robot_height = 200
        self.add_object(self.x_robot,self.y_robot,
                        self.robot_width,self.robot_height,'Robot')

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
        height = int(height//self.cell_size)
      
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
            The real rotation that happened, the outcome (0 : no problem, 1 : impossible to rotate all the way) 
        """
        ROTATION_STEP = math.radians(5)
        real_rotation = 0
        x_min = self.x_robot - self.robot_width//2
        x_max = self.x_robot + self.robot_width//2
        y_min = self.y_robot - self.robot_height//2
        y_max = self.y_robot + self.robot_height//2
        rotation_start = math.radians(self.robot_angle)
        rotation_end = rotation_start + math.radians(rotation)
        tmp_endpoints = []
        end_endpoints = []
        outcome = 0
        while (rotation_start != rotation_end) :
            step = ROTATION_STEP
            if(rotation_end - rotation_start < ROTATION_STEP):
                step = rotation_end - rotation_start

            for i in range (x_min,x_max):
                for j in range (y_min,y_max):
                    angle = rotation_start + step
                    cos = math.cos(angle)
                    sin = math.sin(angle)
                    x_prime = int( ((i-self.x_robot) * cos - (j-self.y_robot) * sin) + self.x_robot )
                    y_prime = int ( ((j-self.y_robot) * cos - (i-self.x_robot) * sin ) + self.y_robot )
                    if(self.grid[x_prime][y_prime].status != 'Free'
                    and self.grid[x_prime][y_prime].status != 'Robot'):
                        print("Robot was blocked by something when rotating")
                        outcome = 1
                        self.apply_status(end_endpoints,'Robot')
                        return real_rotation, outcome, end_endpoints
                    tmp_endpoints.append((x_prime, y_prime))
                    real_rotation += step
                    rotation_start += step
            end_endpoints = tmp_endpoints
        self.remove_all_objects_of_type('Robot')
        self.apply_status(end_endpoints, 'Robot')
        return real_rotation, outcome, end_endpoints

    def apply_status(self,points_list,status):
        """ Apply the given type to all the points in the list
        """
        for _,points in enumerate(points_list):
            x,y = points
            self.grid[x][y].status = status


    def move_robot(self,rotation, distance_x,distance_y):
        """Move the robot in the world """
        real_rotation, outcome_rotation, robot_points = self.rotate_robot(rotation)
        self.robot_angle = (self.robot_angle + rotation) % 360
        rotation = math.radians(self.robot_angle)
        distance_x_prime = distance_x * math.cos(rotation) - distance_y * math.sin(rotation)
        distance_y_prime = distance_y * math.cos(rotation) - distance_x * math.sin(rotation)
        print("len robot points: ", len(robot_points))
        real_distance_x, real_distance_y, outcome_forward, end_endpoints = self.robot_go_forward(distance_x_prime, distance_y_prime, robot_points)
        return real_rotation,outcome_rotation, real_distance_x, real_distance_y, outcome_forward

    def robot_go_forward(self, distance_x, distance_y, robot_points):
        """Make the robot go forward in the distances given
        """
        FORWARD_STEP_NUMBER = 1
        real_distance_x = 0
        real_distance_y = 0
        outcome = 0
        end_x = self.x_robot + distance_x
        end_y = self.y_robot + distance_y
        start_x = self.x_robot
        start_y = self.y_robot
        step_x = distance_x // FORWARD_STEP_NUMBER
        step_y = distance_y // FORWARD_STEP_NUMBER
        print("step_x :", step_x, "step_y :", step_y)
        fini = end_x == start_x and end_y == start_y
        tmp_endpoints = robot_points
        tmp_endpoints_next =[]
        end_endpoints = []
        while not fini:
            print("start_x", start_x," end_x ,",end_x)
            #ajouter if step trop grand
            for _,point in enumerate(tmp_endpoints):
                x,y = point
                next_x = x + step_x
                next_y = y + step_y
                next_cell = self.grid[next_x][next_y]
                if next_cell.status != 'Free' and next_cell.status != 'Robot' :
                    print("Robot hit something while moving forward")
                    outcome = 1
                    fini = True
                    break
                real_distance_x += step_x
                real_distance_y += step_y
                tmp_endpoints_next.append((next_x,next_y))
            fini = end_x == start_x and end_y == start_y
            #print("fini : ",fini)
            start_x = start_x + step_x
            start_y = start_y + step_x
            end_endpoints = tmp_endpoints_next
            tmp_endpoints = end_endpoints

        self.remove_all_objects_of_type('Robot')
        self.x_robot = start_x
        self.y_robot = start_y
        self.apply_status(end_endpoints, 'Robot')
        print("len end points", len(end_endpoints))
        for _,listo in enumerate(self.grid):
            for _,cell in enumerate(listo):
                if cell.status == 'Robot':
                    print('Robot')
        return real_distance_x, real_distance_y, outcome, end_endpoints