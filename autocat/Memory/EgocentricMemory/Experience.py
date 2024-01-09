import numpy as np
from pyrr import matrix44, Quaternion, Vector3
from ...Robot.RobotDefine import ROBOT_HEAD_X, ROBOT_COLOR_SENSOR_X, ROBOT_FLOOR_SENSOR_X

EXPERIENCE_ALIGNED_ECHO = 'Echo'
EXPERIENCE_LOCAL_ECHO = 'Local_Echo'
EXPERIENCE_CENTRAL_ECHO = 'Central_Echo'
EXPERIENCE_BLOCK = 'Block'
EXPERIENCE_IMPACT = 'Shock'
EXPERIENCE_FLOOR = 'Floor'
EXPERIENCE_FOCUS = 'Focus'
EXPERIENCE_PLACE = 'Place'
EXPERIENCE_PROMPT = 'Prompt'
EXPERIENCE_ROBOT = 'Robot'
FLOOR_COLORS = {0: 'LightSlateGrey', 1: 'red', 2: 'darkOrange', 3: 'gold', 4: 'limeGreen', 5: 'deepSkyBlue',
                6: 'orchid', 7: 'deepPink'}


class Experience:
    """Experiences are instances of interactions
    along with the spatial and temporal information of where and when they were enacted"""

    def __init__(self, pose_matrix, experience_type, clock, experience_id, durability=10, color_index=0):
        """Create an experience to be placed in the memory.
        Args:
        point : position of the affordance relative to the robot.
        type : type of experience (i.e. Chock, Block, Echolocalisation, Line etc)
        durability : durability of the experience, when it reach zero the experience should be removed from the memory.
        """
        # self.point = np.array(point)
        self.pose_matrix = pose_matrix
        self.type = experience_type
        # self.absolute_direction_rad = body_direction_rad
        # self.absolute_direction_quaternion = Quaternion.from_z_rotation(body_direction_rad)
        self.clock = clock
        self.id = experience_id
        self.durability = durability
        self.color_index = color_index

        # # The position of the sensor relative to the position of the experience
        # if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
        #     # The position of the head relative to the position of the echo
        #     head_direction_rad = math.atan2(self.point()[1], self.point()[0] - ROBOT_HEAD_X)
        #     self.absolute_direction_rad += head_direction_rad  # The absolute direction of the sensor...
        #     # self.absolute_direction_quaternion *= Quaternion.from_z_rotation(head_direction_rad)
        #     self.absolute_direction_rad = np.mod(self.absolute_direction_rad, 2*math.pi)  # ...within [0,2pi]
        #     relative_sensor_point = np.array([-self.point()[0] + ROBOT_HEAD_X, -self.point()[1], 0])
        # # The position of a color for a FLOOR experience is used to correct position relative to terrain
        # elif self.type == EXPERIENCE_FLOOR:
        #     # The position of the color sensor relative to the line
        #     relative_sensor_point = -np.array([LINE_X - ROBOT_COLOR_X, 0, 0])
        # else:
        #     relative_sensor_point = -self.point()  # By default the center of the robot.
        #
        # # The polar-egocentric position of the sensor relative to the polar_egocentric position of the experience
        # body_direction_matrix = matrix44.create_from_z_rotation(-body_direction_rad)
        # self._sensor_point = matrix44.apply_to_vector(body_direction_matrix, relative_sensor_point).astype(int)
        # angle_sensor = math.atan2(self._sensor_point[1], self._sensor_point[0])
        # # self.rotation_matrix = matrix44.create_from_z_rotation(math.pi - angle_sensor)
        # self.quaternion = Quaternion.from_z_rotation(angle_sensor - math.pi)

    def __str__(self):
        return "(id:" + str(self.id) + ",clock:" + str(self.clock) + ", type:" + self.type + ")"

    def displace(self, displacement_matrix):
        """Displace the experience by the displacement_matrix"""
        # Update the position matrix in robot-centric coordinates
        # by miraculously multiplying the position_matrix by the displacement_matrix
        self.pose_matrix = matrix44.multiply(self.pose_matrix, displacement_matrix)

    def point(self):
        """Return the point of reference of this point of interest. Used for compass calibration"""
        # Translate the origin point by the pose
        return matrix44.apply_to_vector(self.pose_matrix, [0., 0., 0.])

    def absolute_quaternion(self, body_quaternion):
        """Return a quaternion representing the absolute direction of this experience"""
        # The body quaternion minus the relative direction of the experience
        return Quaternion.from_matrix(self.pose_matrix).inverse * body_quaternion

    def polar_sensor_point(self, body_quaternion):
        """Return the polar-egocentric position of the sensor relative to this experience"""
        # The position of the center of the robot
        ego_robot_center = -Vector3(self.point())
        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the head relative to the echo
            return body_quaternion * (ego_robot_center + [ROBOT_HEAD_X, 0, 0])
        elif self.type == EXPERIENCE_FLOOR:
            # The position of the color sensor at the end of the interaction relative to the experience
            # return body_quaternion * (ego_robot_center + [LINE_X - ROBOT_COLOR_SENSOR_X, 0, 0])
            return body_quaternion * (ego_robot_center + [ROBOT_COLOR_SENSOR_X, 0, 0])
            # return body_quaternion * (ego_robot_center + [ROBOT_FLOOR_SENSOR_X, 0, 0])
            # return body_quaternion * Vector3([ROBOT_COLOR_SENSOR_X - ROBOT_FLOOR_SENSOR_X, 0, 0])
        else:
            # The other sensors are at the position of the experience
            return Vector3([0, 0, 0])
            # return body_quaternion * ego_robot_center

    def save(self):
        """Create a copy of the experience for memory snapshot"""
        # Clone the position matrix so it can be updated separately
        saved_experience = Experience(self.pose_matrix.copy(), self.type, self.clock, self.id, self.durability,
                                      self.color_index)
        # saved_experience.position_matrix = self.position_matrix.copy()
        # Reset the absolute directions  TODO Modify so they don't have to be reset
        # saved_experience.absolute_direction_rad = self.absolute_direction_rad
        # saved_experience._sensor_point = self.sensor_point()  # The cloned experience would compute from the new x y
        # # saved_experience.rotation_matrix = self.rotation_matrix
        # saved_experience.quaternion = self.quaternion.copy()
        return saved_experience
