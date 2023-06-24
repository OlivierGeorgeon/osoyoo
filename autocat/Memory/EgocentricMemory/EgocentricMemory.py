import numpy as np
from playsound import playsound
from pyrr import matrix44
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_IMPACT
from ...Robot.RobotDefine import ROBOT_COLOR_X, ROBOT_FRONT_X, LINE_X, ROBOT_FRONT_Y, ROBOT_HEAD_X, ROBOT_SIDE
from ...Decider.Action import ACTION_SCAN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD
import math

EXPERIENCE_PERSISTENCE = 10


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
        self.focus_point = None  # The point where the agent is focusing
        self.prompt_point = None  # The point where the agent is prompted do go
        self.experiences = {}
        self.experience_id = 0  # A unique ID for each experience in memory

    def update_and_add_experiences(self, enacted_enaction):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """

        # Move the existing experiences
        for experience in self.experiences.values():
            experience.displace(enacted_enaction.displacement_matrix)

        # Add the PLACE experience with the sensed color
        place_exp = Experience([ROBOT_COLOR_X, 0, 0], EXPERIENCE_PLACE, enacted_enaction.body_direction_rad, enacted_enaction.clock,
                               self.experience_id, durability=EXPERIENCE_PERSISTENCE,
                               color_index=enacted_enaction.color_index)
        self.experiences[place_exp.id] = place_exp
        self.experience_id += 1

        # The FLOOR experience
        if enacted_enaction.floor > 0:
            if enacted_enaction.floor == 0b01:
                # Black line on the right
                point = np.array([LINE_X, 0, 0])  # 100, 0  # 20
            elif enacted_enaction.floor == 0b10:
                # Black line on the left
                point = np.array([LINE_X, 0, 0])  # 100, 0  # -20
            else:
                # Black line on the front
                point = np.array([LINE_X, 0, 0])
            # Place the experience point
            floor_exp = Experience(point, EXPERIENCE_FLOOR, enacted_enaction.body_direction_rad,
                                   enacted_enaction.clock, experience_id=self.experience_id,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enacted_enaction.color_index)
            self.experiences[floor_exp.id] = floor_exp
            self.experience_id += 1

        # The ECHO experience
        if enacted_enaction.echo_point is not None:
            echo_exp = Experience(enacted_enaction.echo_point,
                                  EXPERIENCE_ALIGNED_ECHO, enacted_enaction.body_direction_rad,
                                  enacted_enaction.clock, experience_id=self.experience_id,
                                  durability=EXPERIENCE_PERSISTENCE, color_index=enacted_enaction.color_index)
            self.experiences[echo_exp.id] = echo_exp
            self.experience_id += 1

        # The BLOCKED experience
        # if enacted_enaction.blocked:
        #     blocked_exp = Experience(ROBOT_FRONT_X, 0, EXPERIENCE_IMPACT, body_direction_rad,
        #                              enacted_enaction.clock, experience_id=self.experience_id,
        #                              durability=EXPERIENCE_PERSISTENCE, color_index=enacted_enaction.color_index)
        #     self.experiences[blocked_exp.id] = blocked_exp
        #     self.experience_id += 1
        # else:
        # The IMPACT experience
        if enacted_enaction.impact > 0:
            if enacted_enaction.action.action_code == ACTION_FORWARD:
                if enacted_enaction.impact == 0b01:  # Impact on the right
                    point = np.array([ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enacted_enaction.impact == 0b11:  # Impact on the front
                    point = np.array([ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    point = np.array([ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            elif enacted_enaction.action.action_code == ACTION_LEFTWARD:
                point = np.array([0, ROBOT_SIDE, 0])
            elif enacted_enaction.action.action_code == ACTION_RIGHTWARD:
                point = np.array([0, -ROBOT_SIDE, 0])
            elif enacted_enaction.action.action_code == ACTION_BACKWARD:
                if enacted_enaction.impact == 0b01:  # Impact on the right
                    point = np.array([-ROBOT_FRONT_X, -ROBOT_FRONT_Y, 0])
                elif enacted_enaction.impact == 0b11:  # Impact on the front
                    point = np.array([-ROBOT_FRONT_X, 0, 0])
                else:  # Impact on the left
                    point = np.array([-ROBOT_FRONT_X, ROBOT_FRONT_Y, 0])
            impact_exp = Experience(point, EXPERIENCE_IMPACT, enacted_enaction.body_direction_rad,
                                    enacted_enaction.clock, experience_id=self.experience_id,
                                    durability=EXPERIENCE_PERSISTENCE, color_index=enacted_enaction.color_index)
            self.experiences[impact_exp.id] = impact_exp
            self.experience_id += 1

        # The LOCAL ECHO experiences
        local_echos = []
        for e in enacted_enaction.echos.items():
            angle = math.radians(int(e[0]))
            point = np.array([ROBOT_HEAD_X + math.cos(angle) * e[1], math.sin(angle) * e[1], 0])
            local_exp = Experience(point, EXPERIENCE_LOCAL_ECHO, enacted_enaction.body_direction_rad,
                                   enacted_enaction.clock, experience_id=self.experience_id,
                                   durability=EXPERIENCE_PERSISTENCE, color_index=enacted_enaction.color_index)
            self.experiences[local_exp.id] = local_exp
            self.experience_id += 1
            local_echos.append((angle, e[1], local_exp))

        # Add the CENTRAL ECHOs from the LOCAL ECHOs
        self.add_central_echos(local_echos)

        # Remove the experiences from egocentric memory when they are two old
        # self.experiences = [e for e in self.experiences if e.clock >= enacted_interaction["clock"] - e.durability]

    def add_central_echos(self, echos):
        """In case of a sweep we obtain an array of echo, this function discretizes
        it to try to find the real position of the objects that sent back the echo

        To do so use 'strikes' which are series of consecutive echoes that are
        close enough to be considered as the same object, and consider that the
        real position of the object is at the middle of the strike"""

        if len(echos) == 0:
            return
        body_direction_rad = echos[0][2].absolute_direction_rad
        clock = echos[0][2].clock
        max_delta_dist = 160
        max_delta_angle = math.radians(20)
        streaks = [[], [], [], [], [], [], [], [], [], [], [], []]
        angle_dist = [[], [], [], [], [], [], [], [], [], [], [], []]
        current_id = 0
        echos = sorted(echos, key=lambda elem: elem[0])  # on trie par angle, pour avoir les streak "préfaites"
        for angle, distance, interaction in echos:
            check = False
            for i, streak in enumerate(streaks):
                if len(streak) > 0 and not check:
                    if any((abs(ele[1] - distance) < max_delta_dist and abs(angle - ele[0]) < max_delta_angle) for ele in
                           streak):
                        streak.append((angle, distance, interaction))
                        angle_dist[i].append((math.degrees(angle), distance))
                        check = True
            if check:
                continue
            if len(streaks[current_id]) == 0:
                streaks[current_id].append((angle, distance, interaction))
                angle_dist[current_id].append((math.degrees(angle), distance))
            else:
                current_id = (current_id + 1)
                streaks[current_id].append((angle, distance, interaction))
                angle_dist[current_id].append((math.degrees(angle), distance))
        for streak in streaks:
            if len(streak) == 0:
                continue
            else:
                x_mean, y_mean = 0, 0
                if len(streak) % 2 == 0:
                    # Compute the means of x and y values for the two elements at the center of the array
                    x_mean = (streak[int(len(streak) / 2)][2].point[0] + streak[int(len(streak) / 2) - 1][2].point[0]) / 2
                    y_mean = (streak[int(len(streak) / 2)][2].point[1] + streak[int(len(streak) / 2) - 1][2].point[1]) / 2
                else:
                    # The x and y are at the center of the array
                    x_mean = streak[int(len(streak) / 2)][2].point[0]
                    y_mean = streak[int(len(streak) / 2)][2].point[1]
                experience_central_echo = Experience([int(x_mean), int(y_mean), 0], EXPERIENCE_CENTRAL_ECHO,
                                                     body_direction_rad, clock, experience_id=self.experience_id,
                                                     durability=5)
                self.experiences[experience_central_echo.id] = experience_central_echo
                self.experience_id += 1

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
