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
        """Create an object to be placed in the memory.
        Args:
        x, y : coordinates relative the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the object, when it reach zero the object should be removed from the memory.
        decayIntensity : represent how much is removed from durability at each iteraction.
        """
        self.x = x  # TODO Don't use x y and rotation but only position_matrix
        self.y = y
        self.rotation = 0
        # Stores both the position and the rotation of the experience
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')

        # self.width = width
        # self.height = height
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
        # self.decay()

    def displace(self, displacement_matrix):
        """ Displace and rotate the experience by the displacement_matrix """

        assert displacement_matrix is not None
        self.position_matrix = matrix44.multiply(self.position_matrix, displacement_matrix)

        # TODO Don't use x, y, and rotation but only position_matrix
        # if self.x is not None and self.y is not None:
        v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
        self.x, self.y = v[0], v[1]

        q = Quaternion(displacement_matrix)
        if q.axis[2] > 0:  # Rotate around z axis upwards
            self.rotation += math.degrees(q.angle)
        else:  # Rotate around z axis downward
            self.rotation += math.degrees(-q.angle)

    def get_allocentric_coordinates(self, body_direction_rad):
        """ Compute allocentric coordinates of the experience given the body direction
        Return a list of ((x,y),interaction)"""
        # rota_radian = self.workspace.memory.body_memory.body_direction_rad
        allocentric_coordinates = []
        # for _, interaction in enumerate(interaction_list):
        # corner_x, corner_y = interaction.x, interaction.y
        x_prime = int(self.x * math.cos(body_direction_rad) - self.y * math.sin(body_direction_rad))
                      # + self.allocentric_memory.robot_pos_x)
        y_prime = int(self.y * math.cos(body_direction_rad) + self.x * math.sin(body_direction_rad))
                      # + self.allocentric_memory.robot_pos_y)
        # allocentric_coordinates.append(((x_prime, y_prime), interaction))

        return x_prime, y_prime
