import numpy as np
from pyrr import Matrix44
from ...Memory.PlaceMemory.PlaceCell import PlaceCell
from ...Memory.PlaceMemory.Cue import Cue

MIN_PLACE_CELL_DISTANCE = 300


class PlaceMemory:
    """The memory of place cells"""
    def __init__(self):
        """Initialize the list of place cells"""
        self.place_cells = {}
        self.place_cell_id = 0

    def add_or_update_place_cell(self, memory):
        """Create e new place cell or update the existing one"""
        # Create the cues
        cues = {}
        # The new experiences generated during this step constitute cues
        for e in [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock)]:
            cue = Cue(e.id, e.polar_pose_matrix(), e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues[cue.id] = cue

        # distances = [np.linalg.norm(pc.point - point)for pc in self.place_cells.values()]
        existing_id = None
        pc_distance_id = {np.linalg.norm(pc.point - memory.allocentric_memory.robot_point): key for key, pc in self.place_cells.items()}
        if len(pc_distance_id) > 0 and min(pc_distance_id) < MIN_PLACE_CELL_DISTANCE:
            existing_id = pc_distance_id[min(pc_distance_id.keys())]
        if existing_id is None:
            # Add a new place cell
            self.place_cell_id += 1
            self.place_cells[self.place_cell_id] = PlaceCell(memory.allocentric_memory.robot_point, cues)
            return None
        else:
            # Offset the cues to the closes place cell
            offset_matrix = Matrix44.from_translation(memory.allocentric_memory.robot_point - self.place_cells[existing_id].point)
            for cue in cues.values():
                cue.pose_matrix *= offset_matrix
            # Add the cues to the existing place cell
            return self.place_cells[existing_id].add_cues(cues)

    def save(self):
        """Return a clone of place memory for memory snapshot"""
        saved_place_memory = PlaceMemory()
        saved_place_memory.place_cells = {k: p.save() for k, p in self.place_cells.items()}
        saved_place_memory.place_cell_id = self.place_cell_id
        return saved_place_memory
