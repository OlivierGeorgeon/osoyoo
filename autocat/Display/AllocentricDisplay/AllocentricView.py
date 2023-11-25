import pyglet
from pyglet.gl import *
from pyrr import Matrix44, Quaternion
from ...Utils import quaternion_translation_to_matrix
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from .CellDisplay import CellDisplay
from ...Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ROBOT
from ..InteractiveDisplay import InteractiveDisplay
from ..PointOfInterest import PointOfInterest


NB_CELL_WIDTH = 30
NB_CELL_HEIGHT = 100
CELL_RADIUS = 50


class AllocentricView(InteractiveDisplay):
    """Create the allocentric view"""
    def __init__(self, workspace, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Allocentric Memory")
        self.set_minimum_size(150, 150)

        # glClearColor(0.2, 0.2, 0.7, 1.0)  # Make it look like hippocampus imaging
        glClearColor(0.2, 0.2, 1.0, 1.0)  # For demonstration in Fête de la Science
        # glClearColor(1.0, 1.0, 1.0, 1.0)

        self.groups = [pyglet.graphics.OrderedGroup(1),
                       pyglet.graphics.OrderedGroup(2),
                       pyglet.graphics.OrderedGroup(3),
                       pyglet.graphics.OrderedGroup(4)]
        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.forefront)  # Rectangles seem not to respect ordered groups

        self.zoom_level = 4
        self.mouse_press_angle = 0
        # self.window = None

        self.workspace = workspace
        self.nb_cell_x = workspace.memory.allocentric_memory.width
        self.nb_cell_y = workspace.memory.allocentric_memory.height
        self.cell_radius = workspace.memory.allocentric_memory.cell_radius

        self.hexagons = [[None for _ in range(self.nb_cell_y)] for _ in range(self.nb_cell_x)]
        self.robot_poi = None  # The other robot point of interest

        self.mouse_press_x = 0
        self.mouse_press_y = 0

        # The text at the bottom left
        self.label_batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)  # y=30
        self.label.color = (255, 255, 255, 255)
        self.label.batch = self.label_batch

    def update_hexagon(self, cell):
        """Create or update or delete an hexagon in allocentric view."""
        if self.hexagons[cell.i][cell.j] is None:
            if cell.is_known():
                # Create the hexagon
                self.hexagons[cell.i][cell.j] = CellDisplay(cell, self.batch, self.groups, self.workspace.clock)
        else:
            if cell.is_known():
                # Update the hexagon
                self.hexagons[cell.i][cell.j].update_color(cell, self.workspace.clock)
            else:
                # Delete the hexagon
                self.hexagons[cell.i][cell.j].delete()
                self.hexagons[cell.i][cell.j] = None

    def on_draw(self):
        """ Drawing the window """
        glClear(GL_COLOR_BUFFER_BIT)

        # The transformations are stacked, and applied backward to the vertices
        glLoadIdentity()

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Draw the grid
        self.batch.draw()

        # Stack the transformation to position the robot
        # glTranslatef(self.workspace.memory.allocentric_memory.robot_point[0],
        #              self.workspace.memory.allocentric_memory.robot_point[1], 0)
        glTranslatef(*self.workspace.memory.allocentric_memory.robot_point)
        glRotatef(90 - self.workspace.memory.body_memory.body_azimuth(), 0.0, 0.0, 1.0)
        # Draw the robot
        self.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.robot.emotion_color(self.workspace.memory.emotion_code)
        self.robot_batch.draw()

        # Draw the text at the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label_batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Display the position in allocentric memory and the cell in the grid"""
        self.mouse_coordinate_to_cell(x, y)

    def mouse_coordinate_to_cell(self, x, y):
        """ Computes the cell coordinates from the screen coordinates """
        prompt_point = self.mouse_coordinates_to_point(x, y)
        cell_x, cell_y = point_to_cell(prompt_point)
        self.label.text = "Mouse pos.: " + str(prompt_point[0]) + ", " + str(prompt_point[1])
        self.label.text += ", Cell: " + str(cell_x) + ", " + str(cell_y)
        return cell_x, cell_y

    def update_robot_poi(self, phenomenon):
        """Update the other robot point of interest if it exists"""
        if self.robot_poi is not None:
            self.robot_poi.delete()
            self.robot_poi = None
        if phenomenon is not None:
            quaternion = Quaternion.from_z_rotation(phenomenon.current().experience.absolute_direction_rad)
            pose_matrix = quaternion_translation_to_matrix(quaternion, phenomenon.point)
            self.robot_poi = PointOfInterest(pose_matrix, self.batch, self.forefront,
                                             EXPERIENCE_ROBOT, phenomenon.current().experience.clock,
                                             color_index=phenomenon.current().experience.color_index)
            # rotation = Matrix44.from_z_rotation(-phenomenon.current().experience.absolute_direction_rad)
            # displacement_matrix = Matrix44.from_translation(phenomenon.point) * rotation
            # self.robot_poi.displace(displacement_matrix)
            # q = Quaternion.from_z_rotation(phenomenon.current().experience.absolute_direction_rad)
            # self.robot_poi.displace(quaternion_translation_to_matrix(q, phenomenon.point))
