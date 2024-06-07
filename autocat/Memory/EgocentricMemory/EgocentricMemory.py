import math
import numpy as np
from pyrr import Matrix44, Quaternion, Vector3
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT, EXPERIENCE_ROBOT, \
    EXPERIENCE_TOUCH, EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH
from ...Robot.RobotDefine import ROBOT_COLOR_SENSOR_X, ROBOT_FLOOR_SENSOR_X, ROBOT_CHASSIS_Y, ROBOT_OUTSIDE_Y, \
    ROBOT_SETTINGS
from ...Proposer.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_CIRCUMVENT, \
    ACTION_TURN
from ...Utils import quaternion_translation_to_matrix, head_angle_distance_to_matrix, matrix_to_rotation_matrix, translation_quaternion_to_matrix

EXPERIENCE_PERSISTENCE = 10


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.prompt_point = None  # The point where the agent is prompted do go
        self.focus_point = None  # The point where the agent is focusing
        self.experiences = {}
        self.experience_id = 0  # A unique ID for each experience in memory

    def update_and_add_experiences(self, enaction):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """
        # Move the existing experiences
        for experience in self.experiences.values():
            if experience.type == EXPERIENCE_COMPASS:
                # Get the rotation part of the displacement matrix
                # m33 = matrix33.create_from_matrix44(enaction.trajectory.displacement_matrix)
                # experience.displace(matrix44.create_from_matrix33(m33))
                experience.displace(matrix_to_rotation_matrix(enaction.trajectory.displacement_matrix))
            elif experience.type != EXPERIENCE_AZIMUTH:  # Do not move the azimuth experiences for calibration
                experience.displace(enaction.trajectory.displacement_matrix)

        # Add the PLACE experience with the sensed color
        pose_matrix = Matrix44.from_translation([ROBOT_COLOR_SENSOR_X, 0, 0], dtype=float)
        place_exp = Experience(self.experience_id, pose_matrix, EXPERIENCE_PLACE, enaction.clock,
                               enaction.trajectory.body_quaternion, durability=EXPERIENCE_PERSISTENCE,
                               color_index=enaction.outcome.color_index)
        self.experiences[place_exp.id] = place_exp
        self.experience_id += 1

        # The FLOOR experience
        if enaction.outcome.floor > 0:
            if enaction.action.action_code in [ACTION_FORWARD, ACTION_TURN, ACTION_SWIPE, ACTION_RIGHTWARD]:
                pose_matrix = translation_quaternion_to_matrix([ROBOT_FLOOR_SENSOR_X, 0, 0],
                                                               enaction.trajectory.yaw_quaternion.inverse)
                pose_matrix = Matrix44.from_translation([np.linalg.norm(ROBOT_SETTINGS[self.robot_id]
                                                                        ["retreat_distance"]), 0, 0]) * pose_matrix
            elif enaction.action.action_code == ACTION_BACKWARD:
                pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X - ROBOT_SETTINGS[self.robot_id]
                                                        ["retreat_distance"][0], 0, 0]) * pose_matrix
            # else:  # SWIPE
            #     if enaction.command.speed[1] > 0:
            #         # pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS[self.robot_id]["retreat_distance"][0], 0]).astype('float64')
            #         pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(math.pi/2), [ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS[self.robot_id]["retreat_distance"][0], 0])
            #     else:
            #         # pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, -ROBOT_SETTINGS[self.robot_id]["retreat_distance"][0], 0]).astype('float64')
            #         pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(math.pi / 2),
            #                                                [ROBOT_FLOOR_SENSOR_X,
            #                                                 -ROBOT_SETTINGS[self.robot_id]["retreat_distance"][0], 0])
            floor_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_matrix,
                                   experience_type=EXPERIENCE_FLOOR, clock=enaction.clock,
                                   body_quaternion=enaction.trajectory.body_quaternion,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[floor_exp.id] = floor_exp
            self.experience_id += 1

        # The ECHO experience

        if enaction.outcome.echo_point is not None:
            echo_exp = Experience(experience_id=self.experience_id, pose_matrix=enaction.outcome.echo_matrix,
                                  experience_type=EXPERIENCE_ALIGNED_ECHO, clock=enaction.clock,
                                  body_quaternion=enaction.trajectory.body_quaternion,
                                  durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[echo_exp.id] = echo_exp
            # print(echo_exp)
            self.experience_id += 1

        # The IMPACT experience
        if enaction.outcome.impact > 0:
            if enaction.action.action_code == ACTION_FORWARD:
                if enaction.outcome.impact == 0b01:  # Impact on the right
                    pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, -ROBOT_CHASSIS_Y, 0], dtype=float)
                    # point = np.array([ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enaction.outcome.impact == 0b11:  # Impact on the front
                    pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, 0, 0], dtype=float)
                    # point = np.array([ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    pose_matrix = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, ROBOT_CHASSIS_Y, 0], dtype=float)
                    # point = np.array([ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            elif enaction.action.action_code in [ACTION_SWIPE]:
                pose_matrix = Matrix44.from_translation([0, ROBOT_OUTSIDE_Y, 0], dtype=float)
                # point = np.array([0, ROBOT_SIDE, 0])
            elif enaction.action.action_code in [ACTION_RIGHTWARD, ACTION_CIRCUMVENT]:
                pose_matrix = Matrix44.from_translation([0, -ROBOT_OUTSIDE_Y, 0], dtype=float)
                # point = np.array([0, -ROBOT_SIDE, 0])
            elif enaction.action.action_code == ACTION_BACKWARD:
                if enaction.outcome.impact == 0b01:  # Impact on the right
                    pose_matrix = Matrix44.from_translation([-ROBOT_FLOOR_SENSOR_X, -ROBOT_CHASSIS_Y, 0], dtype=float)
                    # point = np.array([-ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enaction.outcome.impact == 0b11:  # Impact on the front
                    pose_matrix = Matrix44.from_translation([-ROBOT_FLOOR_SENSOR_X, 0, 0], dtype=float)
                    # point = np.array([-ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    pose_matrix = Matrix44.from_translation([-ROBOT_FLOOR_SENSOR_X, ROBOT_CHASSIS_Y, 0], dtype=float)
                    # point = np.array([-ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            impact_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_matrix,
                                    experience_type=EXPERIENCE_IMPACT, clock=enaction.clock,
                                    body_quaternion=enaction.trajectory.body_quaternion,
                                    durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[impact_exp.id] = impact_exp
            self.experience_id += 1

        # The LOCAL ECHO experiences
        local_echos = []
        for e in enaction.outcome.echos.items():
            # angle = math.radians(int(e[0]))
            # point = np.array([ROBOT_HEAD_X + math.cos(angle) * e[1], math.sin(angle) * e[1], 0])
            pose_matrix = head_angle_distance_to_matrix(int(e[0]), e[1])
            local_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_matrix,
                                   experience_type=EXPERIENCE_LOCAL_ECHO, clock=enaction.clock,
                                   body_quaternion=enaction.trajectory.body_quaternion,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[local_exp.id] = local_exp
            self.experience_id += 1
            # local_echos.append((angle, e[1], local_exp))

        # The CENTRAL ECHO experiences
        for e in enaction.outcome.central_echos:
            # angle = math.radians(int(e[0]))
            # point = np.array([ROBOT_HEAD_X + math.cos(angle) * e[1], math.sin(angle) * e[1], 0])
            pose_matrix = head_angle_distance_to_matrix(int(e[0]), e[1])
            central_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_matrix,
                                     experience_type=EXPERIENCE_CENTRAL_ECHO, clock=enaction.clock,
                                     body_quaternion=enaction.trajectory.body_quaternion,
                                     durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[central_exp.id] = central_exp
            self.experience_id += 1
            local_echos.append((math.radians(int(e[0])), e[1], central_exp))

        # # Add the CENTRAL ECHOs from the LOCAL ECHOs
        # self.add_central_echos(local_echos)

        # Add the other robot experience
        if enaction.message is not None and enaction.message.position_matrix is not None:
            # pose_m = quaternion_translation_to_matrix(enaction.message.ego_quaternion, enaction.message.ego_position)
            robot_exp = Experience(experience_id=self.experience_id, pose_matrix=enaction.message.position_matrix,
                                   experience_type=EXPERIENCE_ROBOT, clock=enaction.clock,
                                   body_quaternion=enaction.trajectory.body_quaternion,
                                   durability=EXPERIENCE_PERSISTENCE // 3, color_index=enaction.message.emotion_code)
            self.experiences[robot_exp.id] = robot_exp
            self.experience_id += 1

        # Add the touch experience
        if enaction.outcome.touch:
            pose_m = Matrix44.from_translation([ROBOT_FLOOR_SENSOR_X, 0, 0], dtype=float)
            touch_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_m,
                                   experience_type=EXPERIENCE_TOUCH, clock=enaction.clock,
                                   body_quaternion=enaction.trajectory.body_quaternion,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=0)
            self.experiences[touch_exp.id] = touch_exp
            self.experience_id += 1

        # Add the compass experience with durability 0
        pose_m = quaternion_translation_to_matrix(enaction.trajectory.body_quaternion.inverse,
                                                  enaction.outcome.compass_point)
        compass_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_m,
                                 experience_type=EXPERIENCE_COMPASS, clock=enaction.clock,
                                 body_quaternion=enaction.trajectory.body_quaternion, durability=0, color_index=0)
        self.experiences[compass_exp.id] = compass_exp
        self.experience_id += 1
        # Add the azimuth experience with durability 0
        azimuth_exp = Experience(experience_id=self.experience_id, pose_matrix=pose_m,
                                 experience_type=EXPERIENCE_AZIMUTH, clock=enaction.clock,
                                 body_quaternion=enaction.trajectory.body_quaternion, durability=0, color_index=0)
        self.experiences[azimuth_exp.id] = azimuth_exp
        self.experience_id += 1

        # Remove the experiences from egocentric memory when they are two old
        # self.experiences = [e for e in self.experiences if e.clock >= enacted_interaction["clock"] - e.durability]

    def save(self):
        """Return a deep clone of egocentric memory for simulation"""
        saved_egocentric_memory = EgocentricMemory(self.robot_id)
        if self.focus_point is not None:
            saved_egocentric_memory.focus_point = self.focus_point.copy()
        if self.prompt_point is not None:
            saved_egocentric_memory.prompt_point = self.prompt_point.copy()
        saved_egocentric_memory.experiences = {key: e.save() for key, e in self.experiences.items()}
        saved_egocentric_memory.experience_id = self.experience_id
        return saved_egocentric_memory
