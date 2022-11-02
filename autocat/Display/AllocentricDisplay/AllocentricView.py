import pyglet
from pyglet.gl import *
from ..EgocentricDisplay.OsoyooCar import OsoyooCar
from .HexagonalCell import HexagonalCell
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS
from ...Memory.AllocentricMemory.GridCell import CELL_UNKNOWN
from ..InteractiveDisplay import InteractiveDisplay
# from ...Workspace import TRUST_POSITION_ROBOT


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
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)

        self.robot_batch = pyglet.graphics.Batch()
        self.robot = OsoyooCar(self.robot_batch, self.background)  # Rectangles seem not to respect ordered groups

        # self.test_cell = Cell(0, 100, self.robot_batch, self.foreground, 50, 'Free')

        self.zoom_level = 4
        self.mouse_press_angle = 0
        self.window = None

        self.memory = memory
        self.nb_cell_x = memory.allocentric_memory.width
        self.nb_cell_y = memory.allocentric_memory.height
        self.cell_radius = memory.allocentric_memory.cell_radius

        self.cell_table = [[None for y in range(self.nb_cell_y)] for x in range(self.nb_cell_x)]
        self.focus_cell = None

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

    def add_cell(self, i: int, j: int):
        """Add a new grid cell to allocentric view. Called by CtrlAllocentricView"""
        cell = self.memory.allocentric_memory.grid[i][j]
        radius = self.memory.allocentric_memory.cell_radius
        if cell.status != CELL_UNKNOWN:
            new_cell = HexagonalCell(i, j, self.batch, self.background, radius, cell.status, 0.8)
            self.cell_table[i][j] = new_cell

    def remove_focus_cell(self):
        """Remove the focus cell from allocentric view"""
        if self.focus_cell is not None:
            self.focus_cell.shape.delete()
        self.focus_cell = None

    def add_focus_cell(self, cell_x, cell_y):
        """Add the focus cell to allocentric view"""
        radius = self.memory.allocentric_memory.cell_radius
        self.focus_cell = HexagonalCell(cell_x, cell_y, self.batch, self.foreground, radius, EXPERIENCE_FOCUS, 0.5)

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
        glTranslatef(-tx, -ty, 0)

        # Draw the grid
        self.batch.draw()

        # Stack the transformation to position the robot
        glTranslatef(tx + self.memory.allocentric_memory.robot_pos_x, ty + self.memory.allocentric_memory.robot_pos_y, 0)
        glRotatef(90 - self.memory.body_memory.body_azimuth(), 0.0, 0.0, 1.0)
        # Draw the robot
        self.robot.rotate_head(self.memory.body_memory.head_direction_degree())
        self.robot_batch.draw()

        # Draw the text at the bottom left corner
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        self.label_batch.draw()
        # self.label.draw()
        # self.label_trust_mode.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        # Find the cell
        cell_x, cell_y = self.cell_from_screen_coordinate(x, y)
        self.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)

    def cell_from_screen_coordinate(self, x, y):
        """ Computes the cell coordinates from the screen coordinates """
        mouse_x = int((x - self.width/2) * self.zoom_level * 2)
        mouse_y = int((y - self.height/2) * self.zoom_level * 2)
        cell_x, cell_y = self.memory.allocentric_memory.convert_pos_in_cell(mouse_x, mouse_y)
        self.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)
        return cell_x, cell_y
