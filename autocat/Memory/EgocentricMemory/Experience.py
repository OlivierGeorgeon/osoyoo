from pyrr import matrix44, Quaternion
from ...Robot.RobotDefine import ROBOT_HEAD_X

EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_IMPACT = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'
EXPERIENCE_PLACE = 'Place'


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, experience_type='None', durability=10, decay_intensity=1, experience_id=0, direction_rad=0):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        decayIntensity : represent how much is removed from durability on each iteraction.
        """
        self.x = x
        self.y = y

        # The position matrix is applied to the vertices of the point_of_interest to display
        # the point of interest at the position of the experience in egocentric view
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')

        # The sensor matrix is applied to the vertices to display the sensor in phenomenon view relative the experience
        # For echo experiences only yet
        opposite_translation_matrix = matrix44.create_from_translation([-x + ROBOT_HEAD_X, -y, 0])  # opposite position
        orientation_matrix = matrix44.create_from_z_rotation(-direction_rad)  # opposite azimuth
        # Apply the opposite azimuth to the opposite position to find the position of the sensor relative to the exp.
        self.sensor_matrix = matrix44.multiply(opposite_translation_matrix, orientation_matrix)
        # self.sensor_x, self.sensor_y, _ = matrix44.apply_to_vector(self.sensor_matrix, [0, 0, 0])

        self.durability = durability
        self.actual_durability = durability
        self.decay_intensity = decay_intensity
        self.type = experience_type
        self.tick_number = 0
        self.id = experience_id

    def tick(self):
        """Updates the clock and decay of this interaction"""
        self.tick_number += 1
        self.actual_durability -= self.decay_intensity

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""

        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the x, y coordinates in robot-centric coordinates
        self.x, self.y, _ = matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])
        # self.x, self.y = v[0], v[1]

    # def position_vector(self):
    #     return matrix44.apply_to_vector(self.position_matrix, [0, 0, 0])
    #
    # def rotation_degree(self):
    #     """Return the rotation of the interaction relative to the robot in degree"""
    #     q = Quaternion(self.position_matrix)
    #     if q.axis[2] > 0:  # Rotate around z axis upwards
    #         rotation = math.degrees(q.angle)
    #     else:  # Rotate around z axis downward
    #         rotation = math.degrees(-q.angle)
    #     return rotation
    #
    # def east_coordinates_from_body_direction_matrix(self, body_direction_matrix):
    #     """The robot-centric/Est/North coordinates of the experience given the body direction matrix"""
    #     v = matrix44.apply_to_vector(body_direction_matrix, [self.x, self.y, 0])
    #     return v[0], v[1]

    def allocentric_from_matrices(self, body_direction_matrix, body_position_matrix):
        """ The allocentric coordinates of the experience given the body direction and position matrices"""
        displacement_matrix = matrix44.multiply(body_direction_matrix, body_position_matrix)
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        return v[0], v[1]

    def allocentric_position_matrix(self, body_direction_matrix, body_position_matrix):
        """ The position matrix to place this experience in allocentric memory"""
        displacement_matrix = matrix44.multiply(body_direction_matrix, body_position_matrix)
        return matrix44.multiply(self.position_matrix, displacement_matrix)
