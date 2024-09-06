import numpy as np
import networkx as nx
from pyrr import Matrix44, vector3, Vector3
import copy
from ...Memory.PlaceMemory.PlaceCell import PlaceCell
from ...Memory.PlaceMemory.Cue import Cue
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_NORTH, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_LOCAL_ECHO, EXPERIENCE_ALIGNED_ECHO
from .PlaceGeometry import nearby_place_cell, transform_estimation_cue_to_cue, compare_place_cells
from ...SoundPlayer import SoundPlayer, SOUND_SURPRISE, SOUND_PLACE_CELL
from ...constants import LOG_CELL, LOG_POSITION_PE, LOG_FORWARD_PE


class PlaceMemory:
    """The memory of place cells"""
    def __init__(self):
        """Initialize the list of place cells"""
        self.place_cells = {}
        self.place_cell_id = 0  # Incremental cell id (first cell is 1)
        self.place_cell_graph = nx.Graph()
        self.place_cell_distances = dict(dict())
        self.previous_cell_id = 0
        self.current_cell_id = 0  # The place cell where the robot currently is
        self.position_pe = np.array([0, 0, 0])  # Position prediction error used to correct the positon
        self.observe_better = True  # Trigger scan on initialisation. Reset by decider
        self.graph_start_id = 1  # The first place cell of the current graph to display
        self.estimated_distance = None
        self.forward_pe = 0

    def add_or_update_place_cell(self, memory):
        """Create e new place cell or update the existing one. Set the proposed correction"""

        # Reset the position_correction
        self.position_pe[:] = 0
        self.estimated_distance = None
        self.forward_pe = 0

        # The new experiences for place cell
        experiences = [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock) and
                       e.type not in [EXPERIENCE_COMPASS, EXPERIENCE_NORTH, EXPERIENCE_CENTRAL_ECHO]]

        # If no place cell then create Place Cell 1 with confidence 100
        if self.current_cell_id == 0:
            self.create_place_cell(memory.allocentric_memory.robot_point, experiences)

        # Find the closest cell if any
        existing_id = nearby_place_cell(memory.allocentric_memory.robot_point, self.place_cells)

        # If the robot is near a known cell (the same or another)
        if existing_id > 0:
            # If the cell is fully observed
            if self.place_cells[existing_id].is_fully_observed():
                # Add the new cues except the local echos
                non_echoes = [e for e in experiences if (e.clock >= memory.clock) and e.type != EXPERIENCE_LOCAL_ECHO]
                self.add_cues_relative_to_center(existing_id, memory.allocentric_memory.robot_point, non_echoes)
                # Compute the position adjustment
                local_echoes = [e for e in experiences if (e.clock >= memory.clock) and e.type == EXPERIENCE_LOCAL_ECHO]
                # If a scan has been performed then find the position correction based on local echoes
                if len(local_echoes) > 0:
                    points = np.array([e.polar_point() for e in local_echoes])
                    estimated_robot_point = self.place_cells[existing_id].translation_estimation_echo(
                        points, memory.allocentric_memory.robot_point, memory.clock)
                    estimated_allo_robot_point = estimated_robot_point + self.place_cells[existing_id].point
                    # The robot position correction
                    proposed_correction = estimated_allo_robot_point - memory.allocentric_memory.robot_point
                    print(f"Position relative to place cell {self.current_cell_id}: "
                          f"{tuple(estimated_robot_point[:2].astype(int))}, "
                          f"propose correction: {tuple(proposed_correction[:2].astype(int))}")
                    if np.linalg.norm(proposed_correction) < 200:
                        # Adjust the position and confidence
                        self.position_pe[:] = proposed_correction
                        memory.adjust_robot_position(self.place_cells[existing_id])
                        SoundPlayer.play(SOUND_SURPRISE)
            # If the cell is not fully observed
            else:
                # Add the cues including the local echoes
                self.add_cues_relative_to_center(existing_id, memory.allocentric_memory.robot_point, experiences)
                # Recompute the echo curve
                self.place_cells[existing_id].compute_echo_curve()
                # If the cell is now fully observed then plot the comparison with the previous cell
                if self.place_cells[existing_id].is_fully_observed() and self.previous_cell_id > 0 and \
                        self.place_cells[self.previous_cell_id].is_fully_observed():
                    # Estimate the translation from the previous place cell based on echoes. Plot the comparison
                    estimated_translation = compare_place_cells(
                        self.place_cells[existing_id], self.place_cells[self.previous_cell_id], memory.clock)
                    # If at least three points match and no rotation
                    if estimated_translation is not None:
                        self.estimated_distance = np.linalg.norm(estimated_translation)
                        place_distance = self.place_cells[existing_id].point - self.place_cells[self.previous_cell_id].point
                        self.position_pe[:] = -estimated_translation - place_distance
                        # self.position_pe[:] = self.place_cells[self.previous_cell_id].point \
                        #                       - estimated_translation - self.place_cells[existing_id].point
                                              #  + self.place_cells[self.previous_cell_id].last_robot_point_in_cell\
                        print(f"Position pe : {tuple(self.position_pe[:2].astype(int))} = "
                              f"echo estimation {tuple(-estimated_translation[:2].astype(int))} - "
                              f"speed estimation {tuple(place_distance[:2].astype(int))} - ")
                        self.calculate_forward_pe()
                        # Adjust the position and increase confidence to 50
                        memory.adjust_cell_position(self.place_cells[existing_id])

            # If the robot just moved to an existing place cell
            if existing_id != self.current_cell_id:
                # If this cell was fully observed
                if self.place_cells[existing_id].is_fully_observed():
                    # Try to adjust position based on aligned echo
                    align_experiences = [e for e in memory.egocentric_memory.experiences.values()
                                         if (e.clock >= memory.clock) and e.type == EXPERIENCE_ALIGNED_ECHO]
                    if len(align_experiences) == 1:  # One aligned echo experience
                        allo_point = align_experiences[0].polar_point() + memory.allocentric_memory.robot_point
                        proposed_correction = self.place_cells[existing_id].translation_estimate_aligned_echo(
                            allo_point)
                        print(f"Proposed correction to nearest central echo: "
                              f"{tuple(proposed_correction[:2].astype(int))}")
                        # If the proposed correction is not too great then make the correction
                        if np.linalg.norm(proposed_correction) < 100 and abs(
                                memory.body_memory.head_direction_degree()) < 40:
                            # Adjust the position and increase confidence
                            self.position_pe[:] = proposed_correction
                            memory.adjust_robot_position(self.place_cells[existing_id])
                            SoundPlayer.play(SOUND_SURPRISE)
                        else:
                            self.observe_better = True
                    else:
                        print("No echo: scan")
                        self.observe_better = True
                # Add the edge and the distance from the previous place cell to the newly recognized one
                self.place_cell_graph.add_edge(self.current_cell_id, existing_id)
                self.place_cell_distances[existing_id] = {self.current_cell_id: np.linalg.norm(
                    self.place_cells[existing_id].point - self.place_cells[self.current_cell_id].point)}
                self.previous_cell_id = self.current_cell_id
                self.current_cell_id = existing_id
                print(f"Moving from Place {self.previous_cell_id} to existing Place {self.current_cell_id}")
            else:
                print(f"Coming from Place {self.previous_cell_id} and staying at Place {self.current_cell_id}")

            # update the position of the robot in the current place cell
            self.place_cells[existing_id].update_robot_point_in_cell(memory.allocentric_memory.robot_point)

        # If the robot is not near a known cell
        else:
            # Create a new place cell
            self.create_place_cell(memory.allocentric_memory.robot_point, experiences)
            print(f"Moving from Place {self.previous_cell_id} to new Place {self.current_cell_id}")
            SoundPlayer.play(SOUND_PLACE_CELL)

        self.place_cells[self.current_cell_id].last_visited_clock = memory.clock

    def create_place_cell(self, point, experiences):
        """Create a new place cell and add it to the list and to the graph"""
        # Create the cues from the experiences
        cues = []
        for e in experiences:
            cue = Cue(e.id, e.polar_pose_matrix(), e.type, e.clock, e.color_index, e.polar_sensor_point())
            cues.append(cue)
        # Memorize the previous cell id
        self.previous_cell_id = self.current_cell_id
        # The new place cell gets half the confidence of the previous one
        if self.previous_cell_id > 0:
            confidence = self.place_cells[self.previous_cell_id].position_confidence // 2
        else:
            confidence = 100
        # Create the place cell from the cues
        self.place_cell_id += 1
        self.place_cells[self.place_cell_id] = PlaceCell(self.place_cell_id, point, cues, confidence)
        self.place_cells[self.place_cell_id].compute_echo_curve()
        # Add the edge and the distance from the previous place cell to the new one
        if self.place_cell_id > 1:  # Don't create Node 0
            self.place_cell_graph.add_edge(self.current_cell_id, self.place_cell_id)
            self.place_cell_distances[self.current_cell_id] = {self.place_cell_id: np.linalg.norm(
                self.place_cells[self.current_cell_id].point - self.place_cells[self.place_cell_id].point)}
        self.current_cell_id = self.place_cell_id

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
        # Adjust the cue position to the place cell by adding the relative position of the robot
        d_matrix = Matrix44.from_translation(point - self.place_cells[place_cell_id].point)
        # Create the cues from the experiences and append them to the place cell
        for e in experiences:
            pose_matrix = d_matrix * e.polar_pose_matrix()
            cue = Cue(e.id, pose_matrix, e.type, e.clock, e.color_index, e.polar_sensor_point())
            self.place_cells[place_cell_id].cues.append(cue)

    def current_place_cell(self):
        """Return the current place cell"""
        if self.current_cell_id > 0:
            return self.place_cells[self.current_cell_id]

    def trace_dict(self):
        """Return a dictionary of fields that should be traced"""
        return {LOG_CELL: self.current_cell_id, LOG_POSITION_PE: round(np.linalg.norm(self.position_pe)),
                LOG_FORWARD_PE: round(self.forward_pe)}

    def calculate_forward_pe(self):
        predicted_translation = vector3.normalise(Vector3(self.place_cells[self.current_cell_id].point -
                                                   self.place_cells[self.previous_cell_id].point -
                                                   self.place_cells[self.previous_cell_id].last_robot_point_in_cell,
                                                  dtype=float))
        # place_change_v = Vector3(self.place_cells[self.current_cell_id].point - self.new_cell_point, dtype=float)
        # place_change_v.normalize()
        self.forward_pe = np.dot(predicted_translation, self.position_pe)
        print(f"Current cell {self.current_cell_id}, previous cell {self.previous_cell_id}. "
              f"Last robot point in cell {tuple(self.place_cells[self.previous_cell_id].last_robot_point_in_cell[:2].astype(int))}. "
              f"Predicted translation vector {tuple(predicted_translation[:2])}. "
              f"Position pe {tuple(self.position_pe[:2].astype(int))}. "
              f"Forward pe {round(self.forward_pe)}")

    def save(self):
        """Return a clone of place memory for memory snapshot"""
        saved_place_memory = PlaceMemory()
        saved_place_memory.place_cells = {k: p.save() for k, p in self.place_cells.items()}
        saved_place_memory.place_cell_id = self.place_cell_id
        saved_place_memory.place_cell_graph = self.place_cell_graph.copy()
        saved_place_memory.previous_cell_id = self.previous_cell_id
        saved_place_memory.current_cell_id = self.current_cell_id
        saved_place_memory.place_cell_distances = copy.deepcopy(self.place_cell_distances)
        saved_place_memory.observe_better = self.observe_better
        saved_place_memory.position_pe[:] = self.position_pe
        saved_place_memory.estimated_distance = self.estimated_distance
        saved_place_memory.forward_pe = self.forward_pe
        return saved_place_memory
