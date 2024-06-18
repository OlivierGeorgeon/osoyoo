import numpy as np
import networkx as nx
from pyrr import Matrix44
from ...Memory.PlaceMemory.PlaceCell import PlaceCell
from ...Memory.PlaceMemory.Cue import Cue
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH

MIN_PLACE_CELL_DISTANCE = 300


class PlaceMemory:
    """The memory of place cells"""
    def __init__(self):
        """Initialize the list of place cells"""
        self.place_cells = {}
        self.place_cell_id = 0  # Incremental cell id (first cell is 1)
        self.place_cell_graph = nx.Graph()
        self.current_robot_cell_id = 0  # The place cell where the robot currently is

    def add_or_update_place_cell(self, memory):
        """Create e new place cell or update the existing one"""
        # Create the cues
        cues = {}
        # The new experiences generated during this step constitute cues
        for e in [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock) and
                  e.type not in [EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH]]:
            cue = Cue(e.id, e.polar_pose_matrix(), e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues[cue.id] = cue

        existing_id = None

        # Try to recognize an existing place cell (currently only based on distance)
        pc_distance_id = {np.linalg.norm(pc.point - memory.allocentric_memory.robot_point): key for key, pc
                          in self.place_cells.items()}
        if len(pc_distance_id) > 0:
            min_distance = min(pc_distance_id.keys())
            if min_distance < MIN_PLACE_CELL_DISTANCE:
                existing_id = pc_distance_id[min_distance]

        if existing_id is None:
            # If place cell not recognized, add it
            self.place_cell_id += 1
            self.place_cells[self.place_cell_id] = PlaceCell(memory.allocentric_memory.robot_point, cues)
            if self.place_cell_id > 1:  # Don't create Node 0
                self.place_cell_graph.add_edge(self.current_robot_cell_id, self.place_cell_id)
            self.current_robot_cell_id = self.place_cell_id
            return np.array([0, 0, 0])
        else:
            # If place cell recognized, add new cues
            # Adjust the cue position to the place cell (add the relative position of the robot)
            d_matrix = Matrix44.from_translation(memory.allocentric_memory.robot_point -
                                                 self.place_cells[existing_id].point)
            for cue in cues.values():
                # https://pyglet.readthedocs.io/en/latest/programming_guide/math.html#matrix-multiplication
                cue.pose_matrix @= d_matrix  # = d_matrix * cue.pose_matrix  # *= does not work: wrong order

            # Adjust the position from the estimation by the cues
            position_correction = self.place_cells[existing_id].recognize_vector(cues)
            position_correction_matrix = Matrix44.from_translation(position_correction)
            for cue in cues.values():
                cue.pose_matrix @= position_correction_matrix

            # Add the cues to the existing place cell
            self.place_cells[existing_id].cues.update(cues)

            # Add the edge in the graph if different
            if self.current_robot_cell_id != existing_id:
                self.place_cell_graph.add_edge(self.current_robot_cell_id, existing_id)
            self.current_robot_cell_id = existing_id
            # Return robot position correction
            return position_correction

    def save(self):
        """Return a clone of place memory for memory snapshot"""
        saved_place_memory = PlaceMemory()
        saved_place_memory.place_cells = {k: p.save() for k, p in self.place_cells.items()}
        saved_place_memory.place_cell_id = self.place_cell_id
        saved_place_memory.place_cell_graph = self.place_cell_graph.copy()
        saved_place_memory.current_robot_cell_id = self.current_robot_cell_id
        return saved_place_memory
