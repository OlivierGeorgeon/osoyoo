import numpy as np
from pyglet.graphics import OrderedGroup
from pyglet.gl import glClearColor
from ...Utils import quaternion_translation_to_matrix
from .CellDisplay import CellDisplay
from ...Memory.AllocentricMemory.Geometry import point_to_cell
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ROBOT
from ..InteractiveDisplay import InteractiveDisplay
from ..PointOfInterest import PointOfInterest, POINT_ROBOT
from ...Memory.AllocentricMemory.AllocentricMemory import CELL_UNKNOWN
from ...Memory.AllocentricMemory import STATUS_FLOOR, STATUS_4

CELL_RADIUS = 50
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


class AllocentricView(InteractiveDisplay):
    """Create the allocentric view"""
    def __init__(self, workspace, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.set_caption("Allocentric Memory")
        self.set_minimum_size(150, 150)

        # glClearColor(0.2, 0.2, 0.7, 1.0)  # Make it look like hippocampus imaging
        glClearColor(0.2, 0.2, 1.0, 1.0)  # For demonstration in Fête de la Science
        # glClearColor(1.0, 1.0, 1.0, 1.0)

        self.groups = [OrderedGroup(1), OrderedGroup(2), OrderedGroup(3), OrderedGroup(4)]

        self.zoom_level = 3

        self.workspace = workspace
        self.hexagons = [[None for _ in range(workspace.memory.allocentric_memory.height)]
                         for _ in range(workspace.memory.allocentric_memory.width)]
        self.robot_poi = None  # The other robot point of interest
        self.body_poi = None

    def update_hexagon(self, i, j, cell):
        """Create or update or delete an hexagon in allocentric view."""
        if self.hexagons[i][j] is None:
            if not np.all(cell[STATUS_FLOOR:STATUS_4 + 1] == CELL_UNKNOWN):
                # The hexagon does not exist but the cell is known then create the hexagon
                self.hexagons[i][j] = CellDisplay(cell, self.polar_batch, self.groups, self.workspace.memory.clock)
        else:
            if not np.all(cell[STATUS_FLOOR:STATUS_4 + 1] == CELL_UNKNOWN):
                # The hexagon exists and the cell is known then update the hexagon
                self.hexagons[i][j].update_color(cell, self.workspace.memory.clock)
            else:
                # The hexagon exists and the cell is unknown then delete the hexagon
                self.hexagons[i][j].delete()
                self.hexagons[i][j] = None

    def on_mouse_motion(self, x, y, dx, dy):
        """Display the position in allocentric memory and the cell in the grid"""
        self.mouse_coordinate_to_cell(x, y)

    def mouse_coordinate_to_cell(self, x, y):
        """ Computes the cell coordinates from the screen coordinates """
        mouse_point = self.mouse_coordinates_to_point(x, y)
        cell_x, cell_y = point_to_cell(mouse_point)
        self.label3.text = "Mouse pos.: " + str(mouse_point[0]) + ", " + str(mouse_point[1])
        self.label3.text += ", Cell: " + str(cell_x) + ", " + str(cell_y)
        return cell_x, cell_y

    def update_robot_poi(self, phenomenon):
        """Update the other robot point of interest if it exists"""
        if self.robot_poi is not None:
            self.robot_poi.delete()
            self.robot_poi = None
            self.body_poi.delete()
            self.body_poi = None
        if phenomenon is not None:
            pose_matrix = quaternion_translation_to_matrix(phenomenon.latest_added_affordance().quaternion,
                                                           phenomenon.point +
                                                           phenomenon.latest_added_affordance().point)
            self.body_poi = PointOfInterest(pose_matrix, self.polar_batch, self.forefront, POINT_ROBOT,
                                            phenomenon.latest_added_affordance().clock)
            self.robot_poi = PointOfInterest(pose_matrix, self.polar_batch, self.forefront, EXPERIENCE_ROBOT,
                                             phenomenon.latest_added_affordance().clock,
                                             color_index=phenomenon.latest_added_affordance().color_index)
