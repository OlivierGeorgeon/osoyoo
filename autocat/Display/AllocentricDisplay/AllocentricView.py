import pyglet
from pyglet.gl import *
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from .HexagonalCell import HexagonalCell
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS
from ...Memory.AllocentricMemory.GridCell import CELL_UNKNOWN
from ..InteractiveDisplay import InteractiveDisplay


NB_CELL_WIDTH = 30
NB_CELL_HEIGHT = 100
CELL_RADIUS = 50
ZOOM_IN_FACTOR = 1.2


class AllocentricView(InteractiveDisplay):
    """Create the allocentric view"""
    def __init__(self, memory, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Allocentric Memory")
        self.set_minimum_size(150, 150)
        # glClearColor(0.2, 0.2, 0.7, 1.0)  # Make it look like hippocampus imaging
        glClearColor(0.2, 0.2, 1.0, 1.0)  # For demonstration in Fête de la Science
        # glClearColor(1.0, 1.0, 1.0, 1.0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.batch = pyglet.graphics.Batch()
        self.group1 = pyglet.graphics.OrderedGroup(1)
        self.group2 = pyglet.graphics.OrderedGroup(2)
        self.foreground = pyglet.graphics.OrderedGroup(3)

        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.foreground)  # Rectangles seem not to respect ordered groups

        # self.test_cell = Cell(0, 100, self.robot_batch, self.foreground, 50, 'Free')

        self.zoom_level = 4
        self.mouse_press_angle = 0
        self.window = None

        self.memory = memory
        self.nb_cell_x = memory.allocentric_memory.width
        self.nb_cell_y = memory.allocentric_memory.height
        self.cell_radius = memory.allocentric_memory.cell_radius

        self.hexagons = [[None for _ in range(self.nb_cell_y)] for _ in range(self.nb_cell_x)]

        self.mouse_press_x = 0
        self.mouse_press_y = 0

        # The text at the bottom left
        self.label_batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)  # y=30
        self.label.color = (255, 255, 255, 255)
        self.label.batch = self.label_batch
        # self.label_trust_mode = pyglet.text.Label('Trust position: ', font_name='Verdana', font_size=10, x=10, y=10)
        # self.label_trust_mode.color = (255, 255, 255, 255)
        # self.label_trust_mode.batch = self.label_batch

    def update_hexagon(self, i: int, j: int):
        """Update or create an hexagon in allocentric view."""
        cell = self.memory.allocentric_memory.grid[i][j]
        if self.hexagons[i][j] is not None:
            self.hexagons[i][j].update_color()
        else:
            if cell.status[1] != CELL_UNKNOWN or cell.status[2] != CELL_UNKNOWN:
                self.hexagons[i][j] = HexagonalCell(cell, self.batch, self.group1, self.group2)

    def remove_focus_cell(self):
        """Remove the focus cell from allocentric view"""
        if self.focus_cell is not None:
            self.memory.allocentric_memory.grid[self.focus_cell[0]][self.focus_cell[1]].status[3] = CELL_UNKNOWN
        self.focus_cell = None

    def add_focus_cell(self, i, j):
        """Add the focus cell to allocentric view"""
        self.memory.allocentric_memory.grid[i][j].status[3] = EXPERIENCE_FOCUS
        self.update_hexagon(i, j)
        self.focus_cell = (i, j)
        #self.focus_cell = HexagonalCell(cell_x, cell_y, self.batch, self.group1, self.group2, radius, EXPERIENCE_FOCUS)

    def on_draw(self):
        """ Drawing the window """
        glClear(GL_COLOR_BUFFER_BIT)

        # The transformations are stacked, and applied backward to the vertices
        glLoadIdentity()

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the translation to center the grid in the widow
        tx = self.nb_cell_x * 30 * self.cell_radius / 20
        ty = self.nb_cell_y * 8.66 * self.cell_radius / 20
        # glTranslatef(-tx, -ty, 0)

        # Draw the grid
        self.batch.draw()

        # Stack the transformation to position the robot
        glTranslatef(self.memory.allocentric_memory.robot_point[0],
                     self.memory.allocentric_memory.robot_point[1], 0)
        glRotatef(90 - self.memory.body_memory.body_azimuth(), 0.0, 0.0, 1.0)
        # Draw the robot
        self.robot.rotate_head(self.memory.body_memory.head_direction_degree())
        self.robot_batch.draw()

        # Draw the text at the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label_batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Display the position in allocentric memory and the cell in the grid"""
        self.cell_from_screen_coordinate(x, y)

    def cell_from_screen_coordinate(self, x, y):
        """ Computes the cell coordinates from the screen coordinates """
        mouse_x = int((x - self.width/2) * self.zoom_level * 2)
        mouse_y = int((y - self.height/2) * self.zoom_level * 2)
        cell_x, cell_y = self.memory.allocentric_memory.convert_pos_in_cell(mouse_x, mouse_y)
        self.label.text = "Mouse pos.: " + str(round(mouse_x)) + ", " + str(round(mouse_y))
        self.label.text += ", Cell: " + str(cell_x) + ", " + str(cell_y)
        self.label.text += ", Cell Pos.: " + str(round(self.memory.allocentric_memory.grid[cell_x][cell_y].point[0])) + ", " + \
                           str(round(self.memory.allocentric_memory.grid[cell_x][cell_y].point[1]))
        return cell_x, cell_y
