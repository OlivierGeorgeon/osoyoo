import numpy as np
from playsound import playsound
from pyrr import matrix44
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_PLACE, category_color
from ...Robot.CtrlRobot import KEY_EXPERIENCES
from ...Robot.RobotDefine import ROBOT_COLOR_X
from ...Decider.Action import ACTION_SCAN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD
import math
import colorsys

EXPERIENCE_PERSISTENCE = 10
FOCUS_MAX_DELTA = 100  # (mm) Maximum delta to keep focus


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
        self.focus_point = None  # The point where the agent is focusing
        self.prompt_point = None  # The point where the agent is prompted do go
        self.experiences = {}
        self.experience_id = 0  # A unique ID for each experience in memory

    def manage_focus(self, enacted_interaction):
        """Manage focus catch, lost, or update. Also move the prompt"""
        if self.focus_point is not None:
            # If focussed then adjust the displacement
            # The new estimated position of the focus point
            displacement_matrix = enacted_interaction['displacement_matrix']
            translation = enacted_interaction['translation']
            rotation_matrix = enacted_interaction['rotation_matrix']
            if 'echo_xy' in enacted_interaction:
                # echo_point = enacted_interaction['echo_xy']  # May be 10000 if no echo received
                action_code = enacted_interaction['action']
                prediction_focus_point = matrix44.apply_to_vector(displacement_matrix, self.focus_point)
                # The error between the expected and the actual position of the echo
                # prediction_error_focus = prediction_focus_point - echo_point
                prediction_error_focus = prediction_focus_point - enacted_interaction['echo_xy']
                # The focus displacement was simulated in egocentric memory
                # prediction_error_focus = self.workspace.memory.egocentric_memory.focus_point - echo_point

                # if math.dist(echo_point, prediction_focus_point) < FOCUS_MAX_DELTA:
                if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA:
                    # The focus has been kept
                    enacted_interaction['focus'] = True
                    # If the action has been completed
                    if enacted_interaction['duration1'] >= 1000:
                        # If the head is forward then correct longitudinal displacements
                        if -20 < enacted_interaction['head_angle'] < 20:
                            if action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                                translation[0] = translation[0] + prediction_error_focus[0]
                                # TODO pass the action to correct the estimated speed:
                                # self.workspace.actions[action_code].adjust_translation_speed(translation)
                        # If the head is sideways then correct lateral displacements
                        if 60 < enacted_interaction['head_angle'] or enacted_interaction['head_angle'] < -60:
                            if action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                                translation[1] = translation[1] + prediction_error_focus[1]
                                # TODO pass the action to correct the estimated speed:
                                # self.workspace.actions[action_code].adjust_translation_speed(translation)
                        # Update the displacement matrix according to the new translation
                        translation_matrix = matrix44.create_from_translation(-translation)
                        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                        enacted_interaction['translation'] = translation
                        enacted_interaction['displacement_matrix'] = displacement_matrix

                        # If the focus was kept then update it
                        # if 'focus' in enacted_interaction:
                        # if 'echo_xy' in enacted_interaction:  # Not sure why this is necessary
                        # self.focus_point = np.array([enacted_interaction['echo_xy'][0],
                        #                              enacted_interaction['echo_xy'][1], 0])
                    self.focus_point = enacted_interaction['echo_xy']
                    print("UPDATE FOCUS by delta", prediction_error_focus)
                    # If the focus was lost then reset it
                else:
                    # The focus was lost, override the echo outcome
                    print("LOST FOCUS due to delta", prediction_error_focus)
                    enacted_interaction['lost_focus'] = True  # Used by agent_circle
                    self.focus_point = None
                    # playsound('autocat/Assets/R5.wav', False)
            else:
                # The focus was lost, override the echo outcome
                print("LOST FOCUS due to no echo")
                enacted_interaction['lost_focus'] = True  # Used by agent_circle
                self.focus_point = None
                # playsound('autocat/Assets/R5.wav', False)
        else:
            if enacted_interaction['action'] in [ACTION_SCAN, ACTION_FORWARD]:
                # Catch focus
                if 'echo_xy' in enacted_interaction:
                    # playsound('autocat/Assets/R11.wav', False)
                    # Create the focus in the memory snapshot that will be retrieved at the INTEGRETING step
                    # self.focus_point = np.array([enacted_interaction['echo_xy'][0],
                    #                              enacted_interaction['echo_xy'][1], 0])
                    self.focus_point = enacted_interaction['echo_xy']
                    print("CATCH FOCUS", self.focus_point)

        # Move the prompt
        if self.prompt_point is not None:
            self.prompt_point = matrix44.apply_to_vector(enacted_interaction['displacement_matrix'], self.prompt_point).astype(int)
            print("Prompt moved to egocentric: ", self.prompt_point)

    def update_and_add_experiences(self, enacted_interaction, body_direction_rad):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """

        last_experience_id = self.experience_id
        # Move the existing experiences
        for experience in self.experiences.values():
            experience.displace(enacted_interaction['displacement_matrix'])

        # Add the PLACE experience with the sensed color
        # color = None
        if 'color' in enacted_interaction:
            color_index = category_color(enacted_interaction['color'])
        else:
            color_index = 0
        color_exp = Experience(ROBOT_COLOR_X, 0, EXPERIENCE_PLACE, body_direction_rad, enacted_interaction["clock"],
                               self.experience_id, durability=EXPERIENCE_PERSISTENCE, color_index=color_index)
        self.experiences[color_exp.id] = color_exp
        self.experience_id += 1

        # Create new experiences from points in the enacted_interaction
        for p in enacted_interaction[KEY_EXPERIENCES]:
            experience = Experience(p[1], p[2], p[0], body_direction_rad, enacted_interaction["clock"],
                                    experience_id=self.experience_id, durability=EXPERIENCE_PERSISTENCE,
                                    color_index=color_index)
            # new_experiences.append(experience)
            self.experiences[experience.id] = experience
            self.experience_id += 1

        # Add the central echos from the local echos
        echos = [e for e in self.experiences.values() if e.type == EXPERIENCE_LOCAL_ECHO and e.id > last_experience_id]
        new_central_echos = self.Compute_central_echo(echos)
        for e in new_central_echos:
            self.experiences[e.id] = e

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

    def Compute_central_echo(self, echos):
        """In case of a sweep we obtain an array of echo, this function discretizes
        it to try to find the real position of the objects that sent back the echo

        To do so use 'strikes' which are series of consecutive echoes that are
        close enough to be considered as the same object, and consider that the
        real position of the object is at the middle of the strike"""
        experiences_central_echo = []
        if len(echos) == 0:
            return experiences_central_echo
        body_direction_rad = echos[0].absolute_direction_rad
        clock = echos[0].clock
        echos = self.revert_echoes_to_angle_distance(echos)
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
                experience_central_echo = Experience(int(x_mean), int(y_mean), EXPERIENCE_CENTRAL_ECHO,
                                                     body_direction_rad, clock, experience_id=self.experience_id,
                                                     durability=5)
                self.experience_id += 1
                experiences_central_echo.append(experience_central_echo)

        return experiences_central_echo

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
