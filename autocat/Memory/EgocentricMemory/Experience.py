from pyrr import matrix44, Quaternion
import math

EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_SHOCK = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'
EXPERIENCE_PLACE = 'Place'


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, experience_type='None', durability=10, decay_intensity=1, experience_id=0):
        """Create an experience to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        decayIntensity : represent how much is removed from durability on each iteraction.
        """
        self.x = x
        self.y = y
        # self.rotation = 0
        # Stores both the position and the rotation of the experience
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')

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
        """Displace and rotate the experience by the displacement_matrix"""

        # Update the position matrix in robot-centric coordinates
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # Recompute the x, y coordinates in robot-centric coordinates
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        self.x, self.y = v[0], v[1]

        # # Compute the rotation of the experience
        # q = Quaternion(displacement_matrix)
        # if q.axis[2] > 0:  # Rotate around z axis upwards
        #     self.rotation += math.degrees(q.angle)
        # else:  # Rotate around z axis downward
        #     self.rotation += math.degrees(-q.angle)

    def get_rotation_degree(self):
        """Return the rotation of the interaction relative to the robot in degree"""
        q = Quaternion(self.position_matrix)
        if q.axis[2] > 0:  # Rotate around z axis upwards
            rotation = math.degrees(q.angle)
        else:  # Rotate around z axis downward
            rotation = math.degrees(-q.angle)
        return rotation

    # def get_allocentric_coordinates(self, body_direction_rad):
    #     """ Compute the robot-centric/North coordinates of the experience given the body direction"""
    #     x = int(self.x * math.cos(body_direction_rad) - self.y * math.sin(body_direction_rad))
    #     y = int(self.y * math.cos(body_direction_rad) + self.x * math.sin(body_direction_rad))
    #     return x, y

    def east_coordinates_from_body_direction_matrix(self, body_direction_matrix):
        """ Compute the robot-centric/Est/North coordinates of the experience given the body direction matrix"""
        v = matrix44.apply_to_vector(body_direction_matrix, [self.x, self.y, 0])
        return v[0], v[1]

    def allocentric_from_matrices(self, body_direction_matrix, body_position_matrix):
        displacement_matrix = matrix44.multiply(body_direction_matrix, body_position_matrix)
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        return v[0], v[1]
