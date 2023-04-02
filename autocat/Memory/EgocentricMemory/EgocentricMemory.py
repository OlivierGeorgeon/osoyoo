from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE
from ...Robot.CtrlRobot import KEY_EXPERIENCES
from ...Robot.RobotDefine import ROBOT_COLOR_X
import math
# from .Color import category_color
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
        color_exp = Experience(ROBOT_COLOR_X, 0, EXPERIENCE_PLACE, body_direction_rad, enacted_interaction["clock"],
                               self.experience_id, durability=EXPERIENCE_PERSISTENCE,
                               color=category_color(enacted_interaction['color']))
        # color_exp.color = (enacted_interaction['color']['red'], enacted_interaction['color']['green'],
        #                   enacted_interaction['color']['blue'])
        # Tried to display the hue only
        # hsv = colorsys.rgb_to_hsv(float(color_exp.color[0])/256.0, float(color_exp.color[1])/256.0, float(color_exp.color[2])/256.0)
        # rgb = colorsys.hsv_to_rgb(hsv[0], 1.0, 1.0)
        # color_exp.color = (int(rgb[0] * 256.0), int(rgb[1] * 256.0), int(rgb[2] * 256.0))
        # color_exp.color = category_color(enacted_interaction['color'])

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
    # https://www.colorspire.com/rgb-color-wheel/
    # https://www.pinterest.fr/pin/521713938063708448/
    hsv = colorsys.rgb_to_hsv(float(color_sensor['red']) / 256.0, float(color_sensor['green']) / 256.0,
                              float(color_sensor['blue']) / 256.0)
    color = "LightSlateGrey"

    if hsv[1] > 0.48:

        # if color_sensor['temp'] < 2800:
        if hsv[0] < 0.1:
            color = 'red'  # Hue = 0
        # elif color_sensor['temp'] < 3150:
        elif hsv[0] < 0.2:
            color = 'darkorange'  # Hue = 0.13, 0.16
        # elif color_sensor['temp'] < 3800:  #
        elif hsv[0] < 0.3:
            color = 'gold'  # Hue = 0.25, 0.26
        # elif color_sensor['temp'] < 8000:
        elif hsv[0] < 0.5:
            color = 'seagreen'  # Hue = 0.38, 0.35, 0.37
        else:
            if hsv[0] < 0.9:
                if hsv[1] > 0.68:
                    color = 'royalblue'  # Hue = 0.571, 0.592
                else:
                    color = 'blueviolet'  # Hue = 0.582, 0.61
            else:
                color = 'red'  # Hue = 0

        # elif color_sensor['temp'] > 13000:
        #     color = 'blue'  # Hue = 0.571, 0.592
        # else:
        #     color = 'violet'  # Hue = 0.582, 0.61

    print("Color: ", hsv, color)

    return name_to_rgb(color)
