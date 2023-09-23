import numpy as np
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT, EXPERIENCE_ROBOT
from ...Robot.RobotDefine import ROBOT_COLOR_X, ROBOT_FRONT_X, LINE_X, ROBOT_FRONT_Y, ROBOT_HEAD_X, ROBOT_SIDE
from ...Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_CIRCUMVENT
import math

EXPERIENCE_PERSISTENCE = 10


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
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
            experience.displace(enaction.displacement_matrix)

        # Add the PLACE experience with the sensed color
        body_direction_rad = enaction.body_quaternion.axis[2] * enaction.body_quaternion.angle
        place_exp = Experience([ROBOT_COLOR_X, 0, 0], EXPERIENCE_PLACE, body_direction_rad, enaction.clock,
                               self.experience_id, durability=EXPERIENCE_PERSISTENCE,
                               color_index=enaction.outcome.color_index)
        self.experiences[place_exp.id] = place_exp
        self.experience_id += 1

        # The FLOOR experience
        if enaction.outcome.floor > 0:
            if enaction.outcome.floor == 0b01:
                # Black line on the right
                point = np.array([LINE_X, 0, 0])  # 100, 0  # 20
            elif enaction.outcome.floor == 0b10:
                # Black line on the left
                point = np.array([LINE_X, 0, 0])  # 100, 0  # -20
            else:
                # Black line on the front
                point = np.array([LINE_X, 0, 0])
            floor_exp = Experience(point, EXPERIENCE_FLOOR, body_direction_rad,
                                   enaction.clock, experience_id=self.experience_id,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[floor_exp.id] = floor_exp
            self.experience_id += 1

        # The ECHO experience
        if enaction.outcome.echo_point is not None:
            echo_exp = Experience(enaction.outcome.echo_point,
                                  EXPERIENCE_ALIGNED_ECHO, body_direction_rad,
                                  enaction.clock, experience_id=self.experience_id,
                                  durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[echo_exp.id] = echo_exp
            self.experience_id += 1

        # The IMPACT experience
        if enaction.outcome.impact > 0:
            if enaction.action.action_code == ACTION_FORWARD:
                if enaction.outcome.impact == 0b01:  # Impact on the right
                    point = np.array([ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enaction.outcome.impact == 0b11:  # Impact on the front
                    point = np.array([ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    point = np.array([ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            elif enaction.action.action_code in [ACTION_SWIPE]:
                point = np.array([0, ROBOT_SIDE, 0])
            elif enaction.action.action_code in [ACTION_RIGHTWARD, ACTION_CIRCUMVENT]:
                point = np.array([0, -ROBOT_SIDE, 0])
            elif enaction.action.action_code == ACTION_BACKWARD:
                if enaction.outcome.impact == 0b01:  # Impact on the right
                    point = np.array([-ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enaction.outcome.impact == 0b11:  # Impact on the front
                    point = np.array([-ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    point = np.array([-ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            impact_exp = Experience(point, EXPERIENCE_IMPACT, body_direction_rad,
                                    enaction.clock, experience_id=self.experience_id,
                                    durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[impact_exp.id] = impact_exp
            self.experience_id += 1

        # The LOCAL ECHO experiences
        local_echos = []
        for e in enaction.outcome.echos.items():
            angle = math.radians(int(e[0]))
            point = np.array([ROBOT_HEAD_X + math.cos(angle) * e[1], math.sin(angle) * e[1], 0])
            local_exp = Experience(point, EXPERIENCE_LOCAL_ECHO, body_direction_rad,
                                   enaction.clock, experience_id=self.experience_id,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[local_exp.id] = local_exp
            self.experience_id += 1
            # local_echos.append((angle, e[1], local_exp))

        # The CENTRAL ECHO experiences
        for e in enaction.outcome.central_echos:
            angle = math.radians(int(e[0]))
            point = np.array([ROBOT_HEAD_X + math.cos(angle) * e[1], math.sin(angle) * e[1], 0])
            central_exp = Experience(point, EXPERIENCE_CENTRAL_ECHO, body_direction_rad,
                                     enaction.clock, experience_id=self.experience_id,
                                     durability=EXPERIENCE_PERSISTENCE, color_index=enaction.outcome.color_index)
            self.experiences[central_exp.id] = central_exp
            self.experience_id += 1
            local_echos.append((angle, e[1], central_exp))

        # # Add the CENTRAL ECHOs from the LOCAL ECHOs
        # self.add_central_echos(local_echos)

        # Add the other robot experience
        if enaction.message is not None:
            robot_exp = Experience(enaction.message.ego_position, EXPERIENCE_ROBOT, body_direction_rad,
                                   enaction.clock, experience_id=self.experience_id, durability=EXPERIENCE_PERSISTENCE//3,
                                   color_index=enaction.outcome.color_index, direction_quaternion=enaction.message.ego_quaternion)
            self.experiences[robot_exp.id] = robot_exp
            self.experience_id += 1

        # Remove the experiences from egocentric memory when they are two old
        # self.experiences = [e for e in self.experiences if e.clock >= enacted_interaction["clock"] - e.durability]

    def save(self):
        """Return a deep clone of egocentric memory for simulation"""
        saved_egocentric_memory = EgocentricMemory()
        if self.focus_point is not None:
            saved_egocentric_memory.focus_point = self.focus_point.copy()
        if self.prompt_point is not None:
            saved_egocentric_memory.prompt_point = self.prompt_point.copy()
        saved_egocentric_memory.experiences = {key: e.save() for key, e in self.experiences.items()}
        saved_egocentric_memory.experience_id = self.experience_id
        return saved_egocentric_memory
