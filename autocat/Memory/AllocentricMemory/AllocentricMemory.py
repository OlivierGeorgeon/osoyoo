import math
import numpy as np
from pyrr import matrix44
from . Hexagonal_geometry import CELL_RADIUS, point_to_cell, get_neighbors
from . GridCell import GridCell, CELL_UNKNOWN
from ..EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_PLACE
from ..AllocentricMemory.GridCell import CELL_NO_ECHO, CELL_PHENOMENON
from ...Utils import rotate_vector_z
from ..EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PROMPT
from ...Robot.RobotDefine import ROBOT_FRONT_X, ROBOT_SIDE


class AllocentricMemory:
    """The agent's allocentric memory made with an hexagonal grid."""

    def __init__(self, width, height, cell_radius=CELL_RADIUS):
        """Construct the allocentric memory of the robot, child class of HexaGrid
        with the addition of the robot at the center of the grid and a link between the
        software and the real word, cell_radius representing the radius of a cell in the real world (in millimeters)
        """
        # The grid of cells
        self.width = width  # Nb cells width
        self.height = height  # Nb cells height
        self.min_i = -width // 2 + 1
        self.max_i = width // 2
        self.min_j = -height // 2 + 1
        self.max_j = height // 2
        self.cell_radius = cell_radius

        # Allocentric memory is initialized with the robot at its center
        self.robot_point = np.array([0, 0, 0], dtype=float)

        self.focus_i = None
        self.focus_j = None
        self.prompt_i = None
        self.prompt_j = None

        # The affordances
        self.affordances = []

        # Fill the grid with cells
        self.grid = list()
        # Use negative grid index for negative positions
        for i in range(self.width):
            self.grid.append(list())
            if i <= self.width // 2:
                cell_i = i
            else:
                cell_i = -self.width + i
            for j in range(self.height):
                if j <= self.height // 2:
                    cell_j = j
                else:
                    cell_j = -self.height + j
                self.grid[i].append(GridCell(cell_i, cell_j, self.cell_radius))

    def __str__(self):
        output = ""
        for j in range(self.max_j, self.min_j - 1, -1):
            if j % 2 == 1:
                output += "-----"
            for i in range(self.min_i, self.max_i + 1):
                output += str(self.grid[i][j]) + "-----"
                # output += "-----"
            output += "\n"
        return output

    def update_affordances(self, phenomena, clock):
        """Allocate the phenomena to the cells of allocentric memory"""
        # Clear the previous phenomena
        self.clear_phenomena()
        # Place the phenomena again
        for p_id, p in phenomena.items():
            for a in p.affordances.values():
                # Attribute the status of the affordance
                cell_x, cell_y = point_to_cell(a.point+p.point)
                self.apply_status_to_cell(cell_x, cell_y, a.experience.type, a.experience.clock, a.experience.color_index)
                # Attribute this phenomenon to this cell
                self.grid[cell_x][cell_y].phenomenon_id = p_id
            # cell_i, cell_j = point_to_cell(p.point)
            # self.apply_status_to_cell(cell_i, cell_j, CELL_PHENOMENON, clock, None)  # Mark the origin

        # Place the affordances that are not attached to phenomena
        for a in self.affordances:
            cell_x, cell_y = point_to_cell(a.point)
            self.apply_status_to_cell(cell_x, cell_y, a.experience.type, clock, a.experience.color_index)

    def move(self, body_direction_rad, translation, clock, is_egocentric_translation=True):
        """Move the robot in allocentric memory. Mark the traversed cells Free. Returns the new position"""
        # Compute the robot destination point
        if is_egocentric_translation:
            # TODO Translate between the initial direction and the final direction
            destination_point = self.robot_point + rotate_vector_z(translation, body_direction_rad)
        else:
            destination_point = self.robot_point + translation
        # Check that the robot remains within allocentric memory limits
        body_direction_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        self.place_robot_translate(body_direction_matrix, self.robot_point, destination_point, clock)
        # self.place_translation(self.robot_point, destination_point, clock)
        self.robot_point = destination_point

        return np.round(destination_point)

    def place_robot(self, body_memory, clock):
        """Apply the PLACE status to the cells at the position of the robot"""
        # start_time = time.time()
        outline = body_memory.outline() + self.robot_point
        polygon = [p[0:2] for p in outline]
        for c in [c for line in self.grid for c in line if c.is_inside(polygon)]:
            c.status[0] = EXPERIENCE_PLACE
            c.clock_place = clock
        # print("Place robot time:", time.time() - start_time, "seconds")

    def place_robot_translate(self, body_direction_matrix, start, end, clock):
        """Mark the cells traversed by the robot translation"""
        # TODO manage different directions
        p1 = matrix44.apply_to_vector(body_direction_matrix, [ROBOT_FRONT_X, ROBOT_SIDE, 0]) + end
        p2 = matrix44.apply_to_vector(body_direction_matrix, [-ROBOT_FRONT_X, ROBOT_SIDE, 0]) + start
        p3 = matrix44.apply_to_vector(body_direction_matrix, [-ROBOT_FRONT_X, -ROBOT_SIDE, 0]) + start
        p4 = matrix44.apply_to_vector(body_direction_matrix, [ROBOT_FRONT_X, -ROBOT_SIDE, 0]) + end
        outline = np.array([p1, p2, p3, p4])
        polygon = [p[0:2] for p in outline]
        for c in [c for line in self.grid for c in line if c.is_inside(polygon)]:
            c.status[0] = EXPERIENCE_PLACE
            c.clock_place = clock

    def clear_phenomena(self):
        """Reset the phenomena from cells"""
        for c in [c for line in self.grid for c in line if c.phenomenon_id is not None]:
            c.status[0] = CELL_UNKNOWN
            c.status[1] = CELL_UNKNOWN
            c.clock_phenomenon = 0
            c.phenomenon_id = None

    # def place_translation(self, start, end, clock):
    #     """Mark the cells traversed by the robot"""
    #     distance = math.dist(start, end)
    #     if distance == 0:
    #         return
    #     nb_step = int(distance / self.cell_radius)
    #     if nb_step == 0:
    #         return
    #     step_x = int((end[0] - start[0])/nb_step)
    #     step_y = int((end[1] - start[1])/nb_step)
    #     current_pos_x = start[0]
    #     current_pos_y = start[1]
    #     for _ in range(nb_step):
    #         cell_x, cell_y = point_to_cell(np.array([current_pos_x, current_pos_y, 0]), self.cell_radius)
    #         self.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_PLACE, clock)
    #         current_pos_x += step_x
    #         current_pos_y += step_y

    def apply_status_to_cell(self, i, j, status, clock, color_index):
        """Change the cell status"""
        if (self.min_i <= i <= self.max_i) and (self.min_j <= j <= self.max_j):
            if status in [EXPERIENCE_FLOOR, EXPERIENCE_PLACE]:
                self.grid[i][j].status[0] = status
                self.grid[i][j].clock_place = clock
                self.grid[i][j].color_index = color_index
            else:
                self.grid[i][j].status[1] = status
                self.grid[i][j].clock_interaction = clock
        else:
            print("Error: cell out of grid, i:", i, "j:", j, "Status:", status)

    def mark_echo_area(self, affordance):
        """Mark the area covered by the echolocalization sensor in allocentric memory"""
        # start_time = time.time()
        points = affordance.sensor_triangle()
        triangle = [p[0:2] for p in points]
        for c in [c for line in self.grid for c in line if c.is_inside(triangle)]:
            c.status[2] = CELL_NO_ECHO
            c.clock_no_echo = affordance.experience.clock
        # print("Place echo time:", time.time() - start_time, "seconds")

    def update_focus(self, allo_focus, clock):
        """Update the focus in allocentric memory"""
        # Clear the previous focus cell
        if self.focus_i is not None:
            self.grid[self.focus_i][self.focus_j].status[3] = CELL_UNKNOWN
        # Add the new focus cell
        if allo_focus is not None:
            self.focus_i, self.focus_j = point_to_cell(allo_focus, self.cell_radius)
            self.grid[self.focus_i][self.focus_j].status[3] = EXPERIENCE_FOCUS
            self.grid[self.focus_i][self.focus_j].clock_focus = clock

    def update_prompt(self, allo_prompt, clock):
        """Update the prompt in allocentric memory"""
        # Clear the previous focus cell
        if self.prompt_i is not None:
            self.grid[self.prompt_i][self.prompt_j].status[3] = CELL_UNKNOWN
        # Add the new prompt cell
        if allo_prompt is not None:
            self.prompt_i, self.prompt_j = point_to_cell(allo_prompt, self.cell_radius)
            self.grid[self.prompt_i][self.prompt_j].status[3] = EXPERIENCE_PROMPT
            self.grid[self.prompt_i][self.prompt_j].clock_prompt = clock
            print("Prompt in cell", self.prompt_i, ", ", self.prompt_j)

    def save(self, experiences):
        """Retun a clone of allocentric memory for memory snapshot"""
        # Use the list of experiences cloned when saving egocentric memory
        saved_allocentric_memory = AllocentricMemory(self.width, self.height, self.cell_radius)
        saved_allocentric_memory.robot_point = self.robot_point.copy()
        saved_allocentric_memory.focus_i = self.focus_i
        saved_allocentric_memory.focus_j = self.focus_j
        saved_allocentric_memory.prompt_i = self.prompt_i
        saved_allocentric_memory.prompt_j = self.prompt_j
        saved_allocentric_memory.affordances = [a.save(experiences[a.experience.id]) for a in self.affordances]
        saved_allocentric_memory.grid = [[c.save(experiences) for c in line] for line in self.grid]

        return saved_allocentric_memory

    def most_interesting_pool(self, clock):
        """Return the coordinates of the cell that has the most interesting pool value"""
        cells = []
        interests = []

        # for n in range(-2, 2):
        #     for m in range(-2, 2):
        # 3 tours counterclockwise:
        for i in [(2, 0), (-1, 2), (-2, -2), (2, -1), (0, 5), (-2, -1), (2, -2), (1, 2), (-2, 0), (1, -2), (2, 2), (-2, 1),
                  (0, -2), (2, 1), (-2, 2), (-1, -2)]:
            i_even = 3 * i[0] + i[1]
            j_even = -2 * i[0] + 4 * i[1]
            cells.append([i_even, j_even])
            interests.append(self.pool_interest(i_even, j_even, clock))
            i_odd = i_even - 2
            j_odd = j_even + 1
            cells.append([i_odd, j_odd])
            interests.append(self.pool_interest(i_odd, j_odd, clock))
        max_interest = max(interests)
        coord = cells[interests.index(max_interest)]
        # Update the prompt
        if self.prompt_i is not None:
            self.grid[self.prompt_i][self.prompt_j].status[3] = CELL_UNKNOWN
        self.prompt_i, self.prompt_j = coord[0], coord[1]
        self.grid[self.prompt_i][self.prompt_j].status[3] = EXPERIENCE_PROMPT
        self.grid[self.prompt_i][self.prompt_j].clock_prompt = 1  # TODO save the actual clock
        print("Most interesting pool:", coord, "with interest", max_interest)
        return self.grid[self.prompt_i][self.prompt_j].point()

    def pool_interest(self, i, j, clock):
        """Return the sum of interest of neighbors plus this cell"""
        if (self.min_i + 1 <= i <= self.max_i - 1) and (self.min_j + 1 <= j <= self.max_j - 1):
            interest = self.grid[i][j].interest_value(clock)
            for n in get_neighbors(i, j).values():
                interest += self.grid[n[0]][n[1]].interest_value(clock)
            return interest
        else:
            # If not in the grid
            return -20
