from pyrr import matrix44, Quaternion
import math


EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_SHOCK = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, x, y, width=50, height=50, experience_type='None', durability=10, decay_intensity=1, experience_id=0):
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
        # Stores both the position and the rotation of the interaction
        self.position_matrix = matrix44.create_from_translation([x, y, 0]).astype('float64')

        self.width = width
        self.height = height
        self.durability = durability
        self.actual_durability = durability
        self.decay_intensity = decay_intensity
        self.type = experience_type
        self.tick_number = 0
        self.id = experience_id
        # self.corners = None
        # self.compute_corners()

    # def compute_corners(self):
    #     """Compute the corners of the Interaction.
    #     """
    #     self.corners = [
    #         (self.x, self.y),
    #         (self.x + self.width, self.y),
    #         (self.x + self.width, self.y + self.height),
    #         (self.x, self.y + self.height),
    #     ]

    def decay(self):
        """Remove one decayIntensity from the durability of the object.
        Return: The new durability after decay
        """
        self.actual_durability -= self.decay_intensity
        return self.actual_durability

    def tick(self):
        """Handle everything that happens to the phenomenon when a tick is done"""
        self.tick_number += 1
        self.decay()

    def displace(self, displacement_matrix):
        """ Displace and rotate the interaction by the displacement_matrix """

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
