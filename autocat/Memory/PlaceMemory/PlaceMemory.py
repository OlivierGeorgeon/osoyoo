import numpy as np
import networkx as nx
from pyrr import Matrix44
import copy
from ...Memory.PlaceMemory.PlaceCell import PlaceCell
from ...Memory.PlaceMemory.Cue import Cue
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_NORTH, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO
from .PlaceGeometry import nearby_place_cell, transform_estimation_cue_to_cue, compare_place_cells


class PlaceMemory:
    """The memory of place cells"""
    def __init__(self):
        """Initialize the list of place cells"""
        self.place_cells = {}
        self.place_cell_id = 0  # Incremental cell id (first cell is 1)
        self.place_cell_graph = nx.Graph()
        self.place_cell_distances = dict(dict())
        self.current_robot_cell_id = 0  # The place cell where the robot currently is
        self.observe_better = False

    def add_or_update_place_cell(self, memory):
        """Create e new place cell or update the existing one"""
        position_correction = np.array([0, 0, 0])

        # The new experiences for place cell
        experiences = [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock) and
                       e.type not in [EXPERIENCE_COMPASS, EXPERIENCE_NORTH, EXPERIENCE_CENTRAL_ECHO]]

        # If no place cell then create Place Cell 1
        if self.current_robot_cell_id == 0:
            self.create_place_cell(memory.allocentric_memory.robot_point, experiences)
            return np.array([0, 0, 0])

        # local_echo_points = [e.polar_point() for e in experiences if e.type == EXPERIENCE_LOCAL_ECHO]
        # if len(local_echo_points) > 10:
        #     self.probable_place_cell(memory.allocentric_memory.robot_point, local_echo_points)

        # Find the closest cell if any
        existing_id = nearby_place_cell(memory.allocentric_memory.robot_point, self.place_cells)

        # If the robot is near a known cell (the same or another)
        if existing_id > 0:
            # Update the cell and adjust the robot position
            print(f"Robot at existing place {existing_id}")
            position_correction = self.add_cues_relative_to_center(existing_id, memory.allocentric_memory.robot_point,
                                                                   experiences)
        # If the robot is not near a known cell
        else:
            # Create a new place cell
            self.create_place_cell(memory.allocentric_memory.robot_point, experiences)
            print(f"Robot at new place {self.current_robot_cell_id}")

        # If the place cell is not fully observed
        if not self.place_cells[self.current_robot_cell_id].is_fully_observed():
            # Ask to fully observe the current place cell
            self.observe_better = True
        # If the place cell is fully observed,
        else:
            # Print similarities with other fully observed place cells
            self.observe_better = False

        # Print a comparison between place cells based on local echoes if available
        # compare_place_cells(self.place_cells)

        return position_correction

    def create_place_cell(self, point, experiences):
        """Create a new place cell and add it to the list and to the graph"""
        # Create the cues from the experiences
        cues = []
        for e in experiences:
            cue = Cue(e.id, e.polar_pose_matrix(), e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues.append(cue)
        # Create the place cell from the cues
        self.place_cell_id += 1
        self.place_cells[self.place_cell_id] = PlaceCell(point, cues)
        self.place_cells[self.place_cell_id].compute_echo_curve()
        if self.place_cell_id > 1:  # Don't create Node 0
            self.place_cell_graph.add_edge(self.current_robot_cell_id, self.place_cell_id)
            self.place_cell_distances[self.current_robot_cell_id] = {self.place_cell_id: np.linalg.norm(
                self.place_cells[self.current_robot_cell_id].point - self.place_cells[self.place_cell_id].point)}
        self.current_robot_cell_id = self.place_cell_id

    def probable_place_cell(self, robot_point, points):
        """Return the probability to be on each place cell computed from robot point and local echoes"""
        residual_distances = {}
        for k, p in self.place_cells.items():
            if p.is_fully_observed():
                # The translation to go from the robot to the place
                translation = p.point - robot_point
                # points += translation
                # Measure the distance to transfer the echo points to the cell points (less points must go first)
                reg_p2p, residual_distance = transform_estimation_cue_to_cue(
                    points, [c.point() for c in p.cues if c.type == EXPERIENCE_LOCAL_ECHO]
                )
                residual_distances[k] = residual_distance
                # Return the polar translation from the place cell to the robot
                # Must take the opposite to obtain the polar coordinates of the place cell
                print("Transformation\n", reg_p2p.transformation)
                print(f"Cell {k} expected at: {tuple(translation[0:2].astype(int))}, "
                      f"observed at: {tuple(-reg_p2p.transformation[0:2,3].astype(int))}, "
                      f"residual distance: {residual_distance:.0f}mm")
        if len(residual_distances) > 0:
            most_similar_place_id = min(residual_distances, key=residual_distances.get)
            print(f"Most similar place cell is {most_similar_place_id}")

    def add_cues_relative_to_center(self, place_cell_id, point, experiences):
        """Create the cues relative to the place cell and add them. Return null position correction"""
        # Adjust the cue position to the place cell (add the relative position of the robot)
        d_matrix = Matrix44.from_translation(point - self.place_cells[place_cell_id].point)
        # Create the cues from the experiences
        cues = []
        for e in experiences:
            pose_matrix = d_matrix * e.polar_pose_matrix()
            cue = Cue(e.id, pose_matrix, e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues.append(cue)
        # Add the cues to the existing place cell
        self.place_cells[place_cell_id].cues.extend(cues)
        # Recompute the echo curve
        self.place_cells[place_cell_id].compute_echo_curve()
        # Add the edge in the place cell graph if different
        if self.current_robot_cell_id != place_cell_id:
            self.place_cell_graph.add_edge(self.current_robot_cell_id, place_cell_id)
            # TODO check if this edge already existed
            self.place_cell_distances[self.current_robot_cell_id] = {place_cell_id: np.linalg.norm(
                self.place_cells[self.current_robot_cell_id].point - self.place_cells[place_cell_id].point)}
        # The robot is at this place cell
        self.current_robot_cell_id = place_cell_id
        # Return robot position correction
        return [0, 0, 0]

    def save(self):
        """Return a clone of place memory for memory snapshot"""
        saved_place_memory = PlaceMemory()
        saved_place_memory.place_cells = {k: p.save() for k, p in self.place_cells.items()}
        saved_place_memory.place_cell_id = self.place_cell_id
        saved_place_memory.place_cell_graph = self.place_cell_graph.copy()
        saved_place_memory.current_robot_cell_id = self.current_robot_cell_id
        saved_place_memory.place_cell_distances = copy.deepcopy(self.place_cell_distances)
        saved_place_memory.observe_better = self.observe_better
        return saved_place_memory
