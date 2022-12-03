from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO
from ...Robot.CtrlRobot import KEY_EXPERIENCES
import math

EXPERIENCE_PERSISTENCE = 10


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
        self.experiences = []
        self.experience_id = 0  # A unique ID for each experience in memory

    def update_and_add_experiences(self, enacted_interaction, body_direction_rad):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """

        # Move the existing experiences
        for experience in self.experiences:
            experience.displace(enacted_interaction['displacement_matrix'])

        # Create new experiences from points in the enacted_interaction
        new_experiences = []
        for p in enacted_interaction[KEY_EXPERIENCES]:
            experience = Experience(p[1], p[2], p[0], body_direction_rad,
                                    durability=EXPERIENCE_PERSISTENCE, experience_id=self.experience_id)
            new_experiences.append(experience)
            self.experience_id += 1

        # Add the central echos from the local echos
        new_central_echos = self.Compute_central_echo([e for e in new_experiences if e.type == EXPERIENCE_LOCAL_ECHO],
                                                      body_direction_rad)
        self.experiences += new_experiences
        self.experiences += new_central_echos

    def tick(self):
        for e in self.experiences:
            e.tick()
        # Remove the experiences when they are too old
        to_remove = []
        for e in self.experiences:
            if e.actual_durability <= 0:
                to_remove.append(e)
        self.experiences = [x for x in self.experiences if x not in to_remove]

    def revert_echoes_to_angle_distance(self, echo_list):
        """Convert echo interaction to triples (angle,distance,interaction)"""
        output = []
        for elem in echo_list:
            # compute the angle using elem x and y
            angle = math.atan2(elem.y, elem.x)
            # compute the distance using elem x and y
            distance = math.sqrt(elem.x ** 2 + elem.y ** 2)
            output.append((angle, distance, elem))
        return output

    def Compute_central_echo(self, echo_list, body_direction_rad):
        """In case of a sweep we obtain an array of echo, this function discretize
        it to try to find the real position of the objects that sent back the echo

        To do so use 'strikes' which are series of consecutive echoes that are
        close enough to be considered as the same object, and consider that the
        real position of the object is at the middle of the strike"""
        if len(echo_list) == 1:
            print(echo_list[0])
        echo_list = self.revert_echoes_to_angle_distance(echo_list)
        max_delta_dist = 160
        max_delta_angle = math.radians(20)
        streaks = [[], [], [], [], [], [], [], [], [], [], [], []]
        angle_dist = [[], [], [], [], [], [], [], [], [], [], [], []]
        current_id = 0
        echo_list = sorted(echo_list, key=lambda elem: elem[0])  # on trie par angle, pour avoir les streak "préfaites"
        for angle, distance, interaction in echo_list:
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
        experiences_central_echo = []
        for streak in streaks:
            if len(streak) == 0:
                continue
            else:
                x_mean, y_mean = 0, 0
                if len(streak) % 2 == 0:
                    # Compute the means of x and y values for the two elements at the center of the array
                    x_mean = (streak[int(len(streak) / 2)][2].x + streak[int(len(streak) / 2) - 1][2].x) / 2
                    y_mean = (streak[int(len(streak) / 2)][2].y + streak[int(len(streak) / 2) - 1][2].y) / 2
                else:
                    # The x and y are at the center of the array
                    x_mean = streak[int(len(streak) / 2)][2].x
                    y_mean = streak[int(len(streak) / 2)][2].y
                experience_central_echo = Experience(int(x_mean), int(y_mean), EXPERIENCE_CENTRAL_ECHO,
                                                     body_direction_rad, durability=5, experience_id=self.experience_id)
                self.experience_id += 1
                experiences_central_echo.append(experience_central_echo)

        return experiences_central_echo
