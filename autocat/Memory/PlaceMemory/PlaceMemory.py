import math
import numpy as np
import networkx as nx
from pyrr import Matrix44
import copy
from . import MIN_PLACE_CELL_DISTANCE
from ...Memory.PlaceMemory.PlaceCell import PlaceCell
from ...Memory.PlaceMemory.Cue import Cue
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_LOCAL_ECHO
from .PlaceGeometry import nearby_place_cell, transform_estimation_cue_to_cue


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
        # Create the cues
        cues = []
        # The new experiences generated during this step constitute cues
        for e in [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock) and
                  e.type not in [EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH, EXPERIENCE_CENTRAL_ECHO]]:
            cue = Cue(e.id, e.polar_pose_matrix(), e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues.append(cue)

        # If no place cell then create Place Cell 1
        if self.current_robot_cell_id == 0:
            self.create_place_cell(memory.allocentric_memory.robot_point, cues)
            return np.array([0, 0, 0])

        # Find the closest cell if any
        existing_id = nearby_place_cell(memory.allocentric_memory.robot_point, self.place_cells)

        # If the robot is near a known cell (the same or another)
        if existing_id > 0:
            # Update the cell and adjust the robot position
            print(f"Robot at existing place {existing_id}")
            position_correction = self.add_cues_relative_to_center(existing_id, memory.allocentric_memory.robot_point, cues)
        # If the robot is not near a known cell
        else:
            # Create a new place cell
            self.create_place_cell(memory.allocentric_memory.robot_point, cues)
            print(f"Robot at new place {self.current_robot_cell_id}")

        # Print similarity with other place cells based on central echos if available
        central_echos = [c for c in cues if c.type == EXPERIENCE_LOCAL_ECHO]
        if len(central_echos) > 10:
            self.probable_place_cell(memory.allocentric_memory.robot_point, central_echos)

        # If the place cell is not fully observed
        if not self.place_cells[self.current_robot_cell_id].is_fully_observed():
            # Ask to fully observe the current place cell
            self.observe_better = True
        # If the place cell is fully observed,
        else:
            # Print similarities with other fully observed place cells
            self.observe_better = False

        return position_correction

    def create_place_cell(self, point, cues):
        """Create a new place cell and add it to the list and to the graph"""
        self.place_cell_id += 1
        self.place_cells[self.place_cell_id] = PlaceCell(point, cues)
        self.place_cells[self.place_cell_id].compute_echo_curve()
        if self.place_cell_id > 1:  # Don't create Node 0
            self.place_cell_graph.add_edge(self.current_robot_cell_id, self.place_cell_id)
            self.place_cell_distances[self.current_robot_cell_id] = {self.place_cell_id: np.linalg.norm(
                self.place_cells[self.current_robot_cell_id].point - self.place_cells[self.place_cell_id].point)}
        self.current_robot_cell_id = self.place_cell_id

    def probable_place_cell(self, point, cues):
        """Return the probability to be on each place cell"""
        points = [c.point() for c in cues]
        standard_distances = {}
        for k, p in self.place_cells.items():
            if p.is_fully_observed():
                # Move the points to the place
                translation = p.point - point
                points += translation
                # Measure the distance from the points
                reg_p2p, standard_distance = transform_estimation_cue_to_cue(points, [c.point() for c in p.cues if c.type == EXPERIENCE_LOCAL_ECHO], threshold=1000)
                standard_distances[k] = standard_distance
                print("Transformation\n", reg_p2p.transformation.astype(int))
                print(f"Probability of Cell {k}: standard distance {standard_distance:.0f}: translation ({translation[0]},{translation[1]})")

    def add_cues_relative_to_center(self, place_cell_id, point, cues):
        """Translate the cues to the place cell point and add them to the place cell"""
        # Adjust the cue position to the place cell (add the relative position of the robot)
        d_matrix = Matrix44.from_translation(point - self.place_cells[place_cell_id].point)
        for cue in cues:
            # https://pyglet.readthedocs.io/en/latest/programming_guide/math.html#matrix-multiplication
            cue.pose_matrix @= d_matrix  # = d_matrix * cue.pose_matrix  # *= does not work: wrong order

        # Adjust the position from the estimation by the cues
        # position_correction = self.place_cells[place_cell_id].translation_estimation(cues)
        # position_correction_matrix = Matrix44.from_translation(position_correction)
        # for cue in cues:
        #     cue.pose_matrix @= position_correction_matrix

        # Add the cues to the existing place cell
        self.place_cells[place_cell_id].cues.extend(cues)
        self.place_cells[place_cell_id].compute_echo_curve()

        # Add the edge in the place cell graph if different
        if self.current_robot_cell_id != place_cell_id:
            self.place_cell_graph.add_edge(self.current_robot_cell_id, place_cell_id)
            # TODO check if this edge already existed
            self.place_cell_distances[self.current_robot_cell_id] = {place_cell_id: np.linalg.norm(
                self.place_cells[self.current_robot_cell_id].point - self.place_cells[place_cell_id].point)}
        self.current_robot_cell_id = place_cell_id

        # Return robot position correction
        return [0, 0, 0]  # position_correction

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
