import matplotlib.path as mpath
import time
import numpy as np
from pyrr import quaternion

from . import STATUS_0, STATUS_1, STATUS_2, STATUS_3, STATUS_4, PHENOMENON_ID, COLOR_INDEX, CLOCK_FOCUS, \
    CLOCK_INTERACTION, CLOCK_PROMPT, CLOCK_PHENOMENON, CLOCK_NO_ECHO, CLOCK_PLACE, POINT_X, POINT_Y, IS_POOL, \
    PLACE_CELL_ID
from ..EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_PLACE, EXPERIENCE_FOCUS, EXPERIENCE_PROMPT, \
    EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT
from ...Robot.RobotDefine import CHECK_OUTSIDE
from ...Memory.PhenomenonMemory.PhenomenonMemory import TER, ROBOT1
from ..PhenomenonMemory import PHENOMENON_RECOGNIZABLE_CONFIDENCE, PHENOMENON_ENCLOSED_CONFIDENCE
from .Geometry import is_inside_rectangle, cell_to_point, point_to_cell, is_pool

CELL_UNKNOWN = 0
CELL_NO_ECHO = -4


class AllocentricMemory:
    """The agent's allocentric memory made with an hexagonal grid."""

    def __init__(self, width, height, cell_radius):
        """Construct the allocentric memory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        # The grid of cells
        self.width = width  # Nb cells width
        self.height = height  # Nb cells height
        self.min_i = -width // 2 + 1
        self.max_i = width // 2 + 1
        self.min_j = -height // 2 + 1
        self.max_j = height // 2 + 1
        self.cell_radius = cell_radius

        # Allocentric memory is initialized with the robot at its center
        self.robot_point = np.array([0, 0, 0], dtype=float)

        self.focus_i = None
        self.focus_j = None
        self.prompt_i = None
        self.prompt_j = None

        # The affordances
        self.affordances = []

        # The hexagonal grid
        start_time = time.time()
        self.grid = np.zeros((width, height, 17), dtype=int)
        # Indexes after max_i and max_j are used for negative positions
        i_range = np.concatenate((np.arange(0, self.max_i), np.arange(self.min_i, 0)))
        j_range = np.concatenate((np.arange(0, self.max_j), np.arange(self.min_j, 0)))
        mesh_i, mesh_j = np.meshgrid(i_range, j_range, indexing='ij')
        self.grid[:, :, POINT_X: POINT_Y + 1] = cell_to_point(mesh_i, mesh_j, cell_radius)
        self.grid[:, :, PHENOMENON_ID] = -1
        self.grid[:, :, IS_POOL] = is_pool(mesh_i, mesh_j)
        # print(f"Init Grid time: {time.time() - start_time:.4f} seconds")

        self.user_cells = []  # List of immutable tuples to be easily copied

    def __str__(self):
        output = ""
        for j in range(self.max_j, self.min_j - 1, -1):
            if j % 2 == 1:
                output += "-----"
            for i in range(self.min_i, self.max_i + 1):
                output += f"({self.grid[i][j][POINT_X]:4d}, {self.grid[i][j][POINT_Y]:4d})-----"
                # output += "-----"
            output += "\n"
        return output

    def update_grid(self, memory):
        """Allocate the phenomena to the cells of allocentric memory"""
        # start_time = time.time()
        # Clear the previous phenomena
        self.clear_grid_status()
        # Place the phenomena again
        for p_id, p in memory.phenomenon_memory.phenomena.items():
            # Mark the cells outside the terrain (for BICA 2023 paper)
            if CHECK_OUTSIDE == 1:
                if p_id == TER and p.confidence >= PHENOMENON_RECOGNIZABLE_CONFIDENCE and p.path is not None:
                    for i in range(self.min_i, self.max_i):
                        for j in range(self.min_j, self.max_j):
                            if p.is_inside(self.grid[i][j][POINT_X:POINT_Y + 1]):
                                self.grid[i][j][STATUS_0] = EXPERIENCE_FLOOR
                                self.grid[i][j][PHENOMENON_ID] = TER
                                self.grid[i][j][CLOCK_PLACE] = memory.clock

            # If terrain is enclosed
            if p_id == TER and p.confidence >= PHENOMENON_ENCLOSED_CONFIDENCE:  # PHENOMENON_RECOGNIZE_CONFIDENCE:  # TERRAIN_ORIGIN_CONFIDENCE:
                # Draw the terrain from its shape
                for point in p.shape:
                    cell_x, cell_y = point_to_cell(point + p.point)
                    self.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_FLOOR, p.last_origin_clock, 0)
                    # Attribute this phenomenon to this cell
                    if (self.min_i <= cell_x <= self.max_i) and (self.min_j <= cell_y <= self.max_j):
                        self.grid[cell_x][cell_y][PHENOMENON_ID] = p_id
                # Draw the color floor affordances
                for a in p.affordances.values():
                    if a.color_index != 0:
                        # Attribute the status of the affordance
                        cell_x, cell_y = point_to_cell(a.point+p.point)
                        self.apply_status_to_cell(cell_x, cell_y, a.type, a.clock, a.color_index)
                        # Attribute this phenomenon to this cell
                        if (self.min_i <= cell_x <= self.max_i) and (self.min_j <= cell_y <= self.max_j):
                            self.grid[cell_x][cell_y][PHENOMENON_ID] = p_id

            else:
                if p_id == ROBOT1:
                    # Draw the other robot from its shape
                    for point in p.shape:
                        cell_x, cell_y = point_to_cell(point + p.point)
                        self.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_ALIGNED_ECHO, p.last_origin_clock, 0)
                        self.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_IMPACT, p.last_origin_clock, 0)
                        # Attribute this phenomenon to this cell
                        if (self.min_i <= cell_x <= self.max_i) and (self.min_j <= cell_y <= self.max_j):
                            self.grid[cell_x][cell_y][PHENOMENON_ID] = p_id

                # Mark the affordances of this phenomenon
                for a in p.affordances.values():
                    if (p_id != TER or p.confidence < PHENOMENON_RECOGNIZABLE_CONFIDENCE or a.color_index != 0
                        or CHECK_OUTSIDE == 0) and a.type != EXPERIENCE_PLACE:
                        # Attribute the status of the affordance
                        cell_x, cell_y = point_to_cell(a.point+p.point)
                        self.apply_status_to_cell(cell_x, cell_y, a.type, a.clock, a.color_index)
                        # Attribute this phenomenon to this cell
                        if (self.min_i <= cell_x <= self.max_i) and (self.min_j <= cell_y <= self.max_j):
                            self.grid[cell_x][cell_y][PHENOMENON_ID] = p_id

        # Place the affordances that are not attached to phenomena
        for a in self.affordances:
            cell_x, cell_y = point_to_cell(a.point)
            self.apply_status_to_cell(cell_x, cell_y, a.type, memory.clock, a.color_index)

        # Place the place cells again
        for place_cell_id, place_cell in memory.place_memory.place_cells.items():
            cell_x, cell_y = point_to_cell(place_cell.point)
            print(f"Place cell {place_cell}")
            if (self.min_i <= cell_x <= self.max_i) and (self.min_j <= cell_y <= self.max_j):
                self.grid[cell_x][cell_y][PLACE_CELL_ID] = place_cell_id

        # print("Update allocentric time:", time.time() - start_time, "seconds")

    def move(self, direction_quaternion, trajectory, clock):
        """Move the robot in allocentric memory. Mark the traversed cells Free. Returns the new position
        If body_quaternion is identity then the translation is allocentric"""

        # Mark the cells traversed by the robot
        alo_covered_area = trajectory.covered_area + self.robot_point
        inside_ij = np.where(is_inside_rectangle(self.grid[:, :, POINT_X], self.grid[:, :, POINT_Y], alo_covered_area))
        self.grid[:, :, STATUS_0][inside_ij] = EXPERIENCE_PLACE
        self.grid[:, :, CLOCK_PLACE][inside_ij] = clock
        # The new position of the robot
        self.robot_point += quaternion.apply_to_vector(direction_quaternion, trajectory.translation)

    def roll(self, point):
        """Roll allocentric memory to place the point at the center"""
        i, j = point_to_cell(point)
        xy = self.grid[i, j, POINT_X:POINT_Y + 1]
        self.grid = np.roll(self.grid, (-i, -j), axis=(0, 1))
        self.grid[:, :, POINT_X:POINT_Y + 1] -= xy
        self.robot_point[0:2] -= xy

    def place_robot(self, body_memory, clock):
        """Apply the PLACE status to the cells at the position of the robot"""
        start_time = time.time()
        outline = body_memory.outline() + self.robot_point
        inside_ij = np.where(is_inside_rectangle(self.grid[:, :, POINT_X], self.grid[:, :, POINT_Y], outline))
        self.grid[:, :, STATUS_0][inside_ij] = EXPERIENCE_PLACE
        self.grid[:, :, CLOCK_PLACE][inside_ij] = clock
        # print("Place robot time:", time.time() - start_time, "seconds")

    def clear_grid_status(self):
        """Reset the status of cells where there is a phenomenon, except PLACE status"""
        phenomena_ij = np.where(self.grid[:, :, PHENOMENON_ID] != -1)
        self.grid[:, :, STATUS_1][phenomena_ij] = CELL_UNKNOWN
        self.grid[:, :, CLOCK_PHENOMENON][phenomena_ij] = 0
        self.grid[:, :, PHENOMENON_ID][phenomena_ij] = -1
        self.grid[:, :, STATUS_0][phenomena_ij] = np.where(self.grid[:, :, STATUS_0][phenomena_ij] != EXPERIENCE_PLACE,
                                                           CELL_UNKNOWN, self.grid[:, :, STATUS_0][phenomena_ij])
        self.grid[:, :, PLACE_CELL_ID] = 0

    def apply_status_to_cell(self, i, j, status, clock, color_index):
        """Change the cell status. Keep the max clock"""
        if (self.min_i <= i <= self.max_i) and (self.min_j <= j <= self.max_j):
            if status in [EXPERIENCE_FLOOR, EXPERIENCE_PLACE]:
                self.grid[i][j][STATUS_0] = status
                self.grid[i][j][CLOCK_PLACE] = max(clock, self.grid[i][j][CLOCK_PLACE])
                self.grid[i][j][COLOR_INDEX] = color_index
            else:
                self.grid[i][j][STATUS_1] = status
                self.grid[i][j][CLOCK_INTERACTION] = max(clock, self.grid[i][j][CLOCK_INTERACTION])
        else:
            pass
            # print("Error: cell out of grid, i:", i, "j:", j, "Status:", status)

    def clear_cell(self, i, j, clock):
        """Reset status_0, color, and phenomenon of that cell"""
        if (self.min_i <= i <= self.max_i) and (self.min_j <= j <= self.max_j):
            self.grid[i][j][STATUS_0] = CELL_UNKNOWN
            self.grid[i][j][CLOCK_PLACE] = clock
            self.grid[i][j][COLOR_INDEX] = 0
            self.grid[i][j][PHENOMENON_ID] = -1

    def mark_echo_area(self, affordance):
        """Mark the area covered by the echolocalization sensor in allocentric memory"""
        # start_time = time.time()
        points = affordance.sensor_triangle()
        triangle = [p[0:2] for p in points]
        path = mpath.Path(triangle)
        for i in range(self.min_i, self.max_i):
            for j in range(self.min_j, self.max_j):
                if path.contains_point(self.grid[i][j][POINT_X:POINT_Y + 1]):
                    self.grid[i][j][STATUS_2] = CELL_NO_ECHO
                    self.grid[i][j][CLOCK_NO_ECHO] = affordance.clock
        # print("Place echo time:", time.time() - start_time, "seconds")

    def update_focus(self, allo_focus, clock):
        """Update the focus in allocentric memory"""
        # Clear the previous focus cell
        if self.focus_i is not None:
            # if (self.min_i <= self.focus_i <= self.max_i) and (self.min_j <= self.focus_j <= self.max_j):
            self.grid[self.focus_i][self.focus_j][STATUS_3] = CELL_UNKNOWN
        # Add the new focus cell
        if allo_focus is not None:
            self.focus_i, self.focus_j = point_to_cell(allo_focus, self.cell_radius)
            if (self.min_i <= self.focus_i <= self.max_i) and (self.min_j <= self.focus_j <= self.max_j):
                self.grid[self.focus_i][self.focus_j][STATUS_3] = EXPERIENCE_FOCUS
                self.grid[self.focus_i][self.focus_j][CLOCK_FOCUS] = clock

    def update_prompt(self, allo_prompt, clock):
        """Update the prompt in allocentric memory"""
        # Clear the previous prompt cell
        if self.prompt_i is not None:
            # if (self.min_i <= self.prompt_i <= self.max_i) and (self.min_j <= self.prompt_j <= self.max_j):
            self.grid[self.prompt_i][self.prompt_j][STATUS_4] = CELL_UNKNOWN
        # Add the new prompt cell
        if allo_prompt is not None:
            self.prompt_i, self.prompt_j = point_to_cell(allo_prompt, self.cell_radius)
            if (self.min_i <= self.prompt_i <= self.max_i) and (self.min_j <= self.prompt_j <= self.max_j):
                self.grid[self.prompt_i][self.prompt_j][STATUS_4] = EXPERIENCE_PROMPT
                self.grid[self.prompt_i][self.prompt_j][CLOCK_PROMPT] = clock
                # print("Prompt in cell", self.prompt_i, ", ", self.prompt_j)

    def save(self):
        """Return a clone of allocentric memory for memory snapshot"""
        saved_allocentric_memory = AllocentricMemory(self.width, self.height, self.cell_radius)
        saved_allocentric_memory.robot_point[:] = self.robot_point
        saved_allocentric_memory.focus_i = self.focus_i
        saved_allocentric_memory.focus_j = self.focus_j
        saved_allocentric_memory.prompt_i = self.prompt_i
        saved_allocentric_memory.prompt_j = self.prompt_j
        saved_allocentric_memory.affordances = [a.save() for a in self.affordances]
        saved_allocentric_memory.grid[:, :, :] = self.grid
        saved_allocentric_memory.user_cells = [e for e in self.user_cells]

        return saved_allocentric_memory
