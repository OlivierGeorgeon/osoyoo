# A cue is an experience related to a place cell
# It can be used to recognize the place cell

from pyrr import matrix44


class Cue:
    """A cue is an experience related to a place"""
    def __init__(self, experience_id, pose_matrix, experience_type, clock, color_index, polar_sensor_point):
        """Position should be integer to facilitate search"""
        self.id = experience_id
        self.pose_matrix = pose_matrix  # The pose of this cue relative to the place center
        self.type = experience_type
        self.clock = clock
        self.color_index = color_index
        self.polar_sensor_point = polar_sensor_point  # The position of the sensor relative to the cue

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"Cue clock: {self.clock}, type: {self.type}"

    def point(self):
        """Return the point of this cue. """
        # Translate the origin point by the pose
        return matrix44.apply_to_vector(self.pose_matrix, [0., 0., 0.])

    def save(self):
        """Return a cloned cue for memory snapshot"""
        return Cue(self.id, self.pose_matrix.copy(), self.type, self.clock, self.color_index,
                   self.polar_sensor_point.copy())
