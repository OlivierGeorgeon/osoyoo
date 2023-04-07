from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE
from ...Robot.CtrlRobot import KEY_EXPERIENCES
from ...Robot.RobotDefine import ROBOT_COLOR_X
import math
import colorsys
from webcolors import name_to_rgb

EXPERIENCE_PERSISTENCE = 10


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
        self.experiences = {}
        self.experience_id = 0  # A unique ID for each experience in memory

    def update_and_add_experiences(self, enacted_interaction, body_direction_rad):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """

        # Move the existing experiences
        for experience in self.experiences.values():
            experience.displace(enacted_interaction['displacement_matrix'])

        # Create new experiences from points in the enacted_interaction
        new_experiences = []
        for p in enacted_interaction[KEY_EXPERIENCES]:
            experience = Experience(p[1], p[2], p[0], body_direction_rad, enacted_interaction["clock"],
                                    experience_id=self.experience_id, durability=EXPERIENCE_PERSISTENCE)
            new_experiences.append(experience)
            self.experiences[experience.id] = experience
            self.experience_id += 1

        # Add the central echos from the local echos
        new_central_echos = self.Compute_central_echo([e for e in new_experiences if e.type == EXPERIENCE_LOCAL_ECHO],
                                                      body_direction_rad, enacted_interaction["clock"])
        for e in new_central_echos:
            self.experiences[e.id] = e

        # Add an experience for the color
        if 'color' in enacted_interaction:
            color_exp = Experience(ROBOT_COLOR_X, 0, EXPERIENCE_PLACE, body_direction_rad, enacted_interaction["clock"],
                                   self.experience_id, durability=EXPERIENCE_PERSISTENCE,
                                   color=category_color(enacted_interaction['color']))
            new_experiences.append(color_exp)
            self.experiences[color_exp.id] = color_exp
            self.experience_id += 1

        # Remove the experiences from egocentric memory when they are two old
        # self.experiences = [e for e in self.experiences if e.clock >= enacted_interaction["clock"] - e.durability]

    def revert_echoes_to_angle_distance(self, echo_list):
        """Convert echo interaction to triples (angle,distance,interaction)"""
        # TODO use the angle and the distance from the head
        output = []
        for elem in echo_list:
            # compute the angle using elem x and y
            angle = math.atan2(elem.point[1], elem.point[0])
            # compute the distance using elem x and y
            distance = math.sqrt(elem.point[0] ** 2 + elem.point[1] ** 2)
            output.append((angle, distance, elem))
        return output

    def Compute_central_echo(self, echo_list, body_direction_rad, clock):
        """In case of a sweep we obtain an array of echo, this function discretizes
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
                    x_mean = (streak[int(len(streak) / 2)][2].point[0] + streak[int(len(streak) / 2) - 1][2].point[0]) / 2
                    y_mean = (streak[int(len(streak) / 2)][2].point[1] + streak[int(len(streak) / 2) - 1][2].point[1]) / 2
                else:
                    # The x and y are at the center of the array
                    x_mean = streak[int(len(streak) / 2)][2].point[0]
                    y_mean = streak[int(len(streak) / 2)][2].point[1]
                experience_central_echo = Experience(int(x_mean), int(y_mean), EXPERIENCE_CENTRAL_ECHO,
                                                     body_direction_rad, clock, experience_id=self.experience_id,
                                                     durability=5)
                self.experience_id += 1
                experiences_central_echo.append(experience_central_echo)

        return experiences_central_echo

    def save(self):
        """Return a deep clone of egocentric memory for simulation"""
        saved_egocentric_memory = EgocentricMemory()
        saved_egocentric_memory.experiences = {key: e.save() for key, e in self.experiences.items()}
        saved_egocentric_memory.experience_id = self.experience_id
        return saved_egocentric_memory


def category_color(color_sensor):
    """Categorize the color from the sensor measure"""
    # https://www.w3.org/wiki/CSS/Properties/color/keywords
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)

    if hsv[1] < 0.45:
        if hsv[0] < 0.6:
            # Not saturate, not violet
            color = "LightSlateGrey"  # Saturation: Table bureau 0.16. Sol bureau 0.17, table olivier 0.21, sol olivier: 0.4, 0.33
        else:
            # Not saturate but violet
            color = 'orchid'  # Hue = 0.66 -- 0.66, Saturation = 0.34, 0.2 -- 0.2
    else:
        color = 'red'  # Hue = 0 -- 0.0, 0.0, sat 0.59
        if hsv[0] < 0.98:
            if hsv[0] > 0.9:
                color = 'deepPink'  # Hue = 0.94, 0.94, 0.94, 0.96, 0.95, sat 0.54
            elif hsv[0] > 0.6:
                color = 'orchid'  # Hue = 0.66
            elif hsv[0] > 0.5:
                color = 'deepSkyBlue'  # Hue = 0.59 -- 0.57, 0.58 -- 0.58, sat 0.86
            elif hsv[0] > 0.28:
                color = 'limeGreen'  # Hue = 0.38, 0.35, 0.37 -- 0.29, 0.33, 0.29, 0.33 -- 0.36, sat 0.68
            elif hsv[0] > 0.175:
                color = 'gold'  # Hue = 0.25, 0.26 -- 0.20 -- 0.20, 0.20, 0.184, 0.2 -- 0.24, sat 0.68
            elif hsv[0] > 0.05:
                color = 'darkOrange'  # Hue = 0.13, 0.16, 0.15 -- 0.06, 0.08, 0.09, 0.08 -- 0.11, sat 0.56

    print("Color: ", hsv, color)

    return name_to_rgb(color)
