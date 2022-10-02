import math
from ..Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_CENTRAL_ECHO


# def revert_echoes_to_angle_distance(echo_list):
#     """Convert echo interaction to triples (angle,distance,interaction)"""
#     output = []
#     for elem in echo_list:
#         # compute the angle using elem x and y
#         angle = math.atan2(elem.y, elem.x)
#         # compute the distance using elem x and y
#         distance = math.sqrt(elem.x ** 2 + elem.y ** 2)
#         output.append((angle, distance, elem))
#     return output
#
#
# def treat_echos(echo_list):
#     """In case of a sweep we obtain an array of echo, this function discretize
#     it to try to find the real position of the objects that sent back the echo
#
#     To do so use 'strikes' which are series of consecutive echoes that are
#     close enough to be considered as the same object, and consider that the
#     real position of the object is at the middle of the strike"""
#     if len(echo_list) == 1:
#         print(echo_list[0])
#     echo_list = revert_echoes_to_angle_distance(echo_list)
#     max_delta_dist = 160
#     max_delta_angle = math.radians(20)
#     streaks = [[], [], [], [], [], [], [], [], [], [], [], []]
#     angle_dist = [[], [], [], [], [], [], [], [], [], [], [], []]
#     current_id = 0
#     echo_list = sorted(echo_list, key=lambda elem: elem[0])  # on trie par angle, pour avoir les streak "préfaites"
#     for angle, distance, interaction in echo_list:
#         check = False
#         for i, streak in enumerate(streaks):
#             if len(streak) > 0 and not check:
#                 if any((abs(ele[1] - distance) < max_delta_dist and abs(angle - ele[0]) < max_delta_angle) for ele in
#                        streak):
#                     streak.append((angle, distance, interaction))
#                     angle_dist[i].append((math.degrees(angle), distance))
#                     check = True
#         if check:
#             continue
#         if len(streaks[current_id]) == 0:
#             streaks[current_id].append((angle, distance, interaction))
#             angle_dist[current_id].append((math.degrees(angle), distance))
#         else:
#             current_id = (current_id + 1)
#             streaks[current_id].append((angle, distance, interaction))
#             angle_dist[current_id].append((math.degrees(angle), distance))
#     experiences_central_echo = []
#     for streak in streaks:
#         if len(streak) == 0:
#             continue
#         else:
#             x_mean, y_mean = 0, 0
#             if len(streak) % 2 == 0:
#                 # Compute the means of x and y values for the two elements at the center of the array
#                 x_mean = (streak[int(len(streak) / 2)][2].x + streak[int(len(streak) / 2) - 1][2].x) / 2
#                 y_mean = (streak[int(len(streak) / 2)][2].y + streak[int(len(streak) / 2) - 1][2].y) / 2
#             else:
#                 # The x and y are at the center of the array
#                 x_mean = streak[int(len(streak) / 2)][2].x
#                 y_mean = streak[int(len(streak) / 2)][2].y
#             experience_central_echo = Experience(int(x_mean), int(y_mean), width=15,
#                                                  experience_type=EXPERIENCE_CENTRAL_ECHO, durability=5,
#                                                  decay_intensity=1, experience_id=0)
#             experiences_central_echo.append(experience_central_echo)
#             # self.egocentric_memory.experiences.append(experience_central_echo)  # OG add to memory for displacement update
#
#     return experiences_central_echo
#
