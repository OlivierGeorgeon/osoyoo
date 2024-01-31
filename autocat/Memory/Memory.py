import numpy as np
from pyrr import quaternion
from . import EMOTION_HAPPY, EMOTION_RELAXED, EMOTION_SAD, EMOTION_ANGRY, EMOTION_UPSET
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory, EXCITATION_LOW, ENERGY_TIRED
from .PhenomenonMemory import ARRANGE_OBJECT_RADIUS
from .PhenomenonMemory.PhenomenonMemory import PhenomenonMemory
from .PhenomenonMemory.PhenomenonTerrain import TERRAIN_INITIAL_CONFIDENCE, TERRAIN_ORIGIN_CONFIDENCE
from .AllocentricMemory.Hexagonal_geometry import CELL_RADIUS
from .. import Memory
from ..Decider.Decider import FOCUS_TOO_FAR_DISTANCE
# from ..Decider.Action import ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD
# from .PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
# from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS


GRID_WIDTH = 30  # 15   # 100 Number of cells wide
GRID_HEIGHT = 100  # 70  # 45  # 200 Number of cells high
NEAR_HOME = 300    # (mm) Max distance to consider near home
SIMULATION_TIME_RATIO = 1  # 0.5   # The simulation speed is slower than the real speed because ...
ARRANGE_MIN_RADIUS = 100
ARRANGE_MAX_RADIUS = 400


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self, arena_id, robot_id):
        self.arena_id = arena_id
        self.robot_id = robot_id
        self.clock = 0
        self.body_memory = BodyMemory(robot_id)
        self.egocentric_memory = EgocentricMemory()
        self.allocentric_memory = AllocentricMemory(GRID_WIDTH, GRID_HEIGHT, cell_radius=CELL_RADIUS)
        self.phenomenon_memory = PhenomenonMemory(arena_id)
        self.emotion_code = EMOTION_RELAXED

    def __str__(self):
        return "Memory Robot position (" + str(round(self.allocentric_memory.robot_point[0])) + "," +\
                                           str(round(self.allocentric_memory.robot_point[1])) + ")"

    def appraise_emotion(self):
        """Update the emotional state code"""
        # Search terrain origin: Robot HAPPY DeciderCircle
        if self.phenomenon_memory.terrain_confidence() < TERRAIN_ORIGIN_CONFIDENCE:
            self.emotion_code = EMOTION_HAPPY
        # Terrain origin has been found
        else:
            # High energy then must circle, explore, watch or arrange
            if self.body_memory.energy >= ENERGY_TIRED:
                # High excitation then must circle or explore
                if self.body_memory.excitation > EXCITATION_LOW:
                    # Focus inside terrain or not too far: HAPPY DeciderCircle
                    if self.egocentric_memory.focus_point is not None and \
                            np.linalg.norm(self.egocentric_memory.focus_point) < FOCUS_TOO_FAR_DISTANCE and \
                            not self.is_outside_terrain(self.egocentric_memory.focus_point):
                        self.emotion_code = EMOTION_HAPPY
                    # No interesting focus: RELAXED, DeciderExplore
                    else:
                        self.emotion_code = EMOTION_RELAXED
                else:
                    # High energy with low excitation, must watch or arrange
                    # if self.is_outside_terrain(self.egocentric_memory.focus_point):
                    if self.egocentric_memory.focus_point is None:
                        # Focus outside terrain or None then SAD, DeciderWatch
                        # No focus then SAD, DeciderWatch
                        self.emotion_code = EMOTION_SAD
                    # Focus is inside terrain
                    else:
                        # If object in the area where it must be arranged
                        ego_target = self.terrain_centric_to_egocentric(self.phenomenon_memory.arrange_point())
                        is_to_arrange = self.is_to_arrange(self.egocentric_memory.focus_point)
                        # print("Ego focus", self.egocentric_memory.focus_point)
                        # if object is closer than target point (minus the radius to prevent keeping pushing)
                        is_closer = self.egocentric_memory.focus_point[0] < ego_target[0] - ARRANGE_OBJECT_RADIUS
                        print("Focus near terrain center:", is_to_arrange, "Before terrain center:", is_closer,
                              "Other robot angry:", self.phenomenon_memory.other_robot_is_angry())
                        if is_to_arrange:
                            if is_closer and not self.phenomenon_memory.other_robot_is_angry():
                                # Object before center: ANGRY DeciderArrange
                                self.emotion_code = EMOTION_ANGRY
                            else:
                                # Object behind center: UPSET DeciderArrange
                                self.emotion_code = EMOTION_UPSET
                        else:
                            # Object too far from center: SAD DeciderWatch
                            self.emotion_code = EMOTION_SAD
            else:
                # Tired: Robot RELAXED, DeciderExplore to go home
                self.emotion_code = EMOTION_RELAXED

    def update_and_add_experiences(self, enaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.focus_point = enaction.focus_point
        self.egocentric_memory.prompt_point = enaction.prompt_point

        # Translate the robot before applying the yaw
        # print("Robot relative translation", enaction.translation)
        self.allocentric_memory.move(self.body_memory.body_quaternion, enaction.translation, enaction.clock)
        self.body_memory.update(enaction)

        self.egocentric_memory.update_and_add_experiences(enaction)

        # The integrator may again update the robot's position

    def update_allocentric(self, clock):
        """Update allocentric memory on the basis of body, phenomenon, and egocentric memory"""
        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory, clock)

        # Mark the affordances
        self.allocentric_memory.update_affordances(self.phenomenon_memory, clock)

        # Update the focus in allocentric memory
        allo_focus = self.egocentric_to_allocentric(self.egocentric_memory.focus_point)
        self.allocentric_memory.update_focus(allo_focus, clock)

        # Update the prompt in allocentric memory
        allo_prompt = self.egocentric_to_allocentric(self.egocentric_memory.prompt_point)
        self.allocentric_memory.update_prompt(allo_prompt, clock)

    def egocentric_to_polar_egocentric(self, point):
        """Convert the position of a point from egocentric to polar-egocentric reference"""
        if point is None:
            return None
        return quaternion.apply_to_vector(self.body_memory.body_quaternion, point)

    def egocentric_to_allocentric(self, point):
        """Return the point in allocentric from the point in egocentric reference"""
        if point is None:
            return None
        # convert to polar-egocentric and then add the position in allocentric memory
        return self.egocentric_to_polar_egocentric(point) + self.allocentric_memory.robot_point

    def polar_egocentric_to_egocentric(self, point):
        """Convert from polar-egocentric to egocentric references"""
        if point is None:
            return None
        # Rotate the point by the opposite body direction using the inverse body quaternion
        return quaternion.apply_to_vector(self.body_memory.body_quaternion.inverse, point)

    def allocentric_to_egocentric(self, point):
        """Return the point in egocentric coordinates from the point in allocentric coordinates"""
        if point is None:
            return None
        return self.polar_egocentric_to_egocentric(point - self.allocentric_memory.robot_point)

    def terrain_centric_to_egocentric(self, point):
        """Return the point in egocentric coordinates from the point in terrain-centric coordinates"""
        if point is None:
            return None
        if self.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            return self.allocentric_to_egocentric(point + self.phenomenon_memory.terrain().point)
        return self.allocentric_to_egocentric(point)

    def egocentric_to_terrain_centric(self, point):
        """Return the point in terrain egocentric coordinates from the point in egocentric coordinates"""
        if point is None:
            return None
        if self.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            return self.egocentric_to_allocentric(point) - self.phenomenon_memory.terrain().point
        return self.egocentric_to_allocentric(point)

    def terrain_centric_to_allocentric(self, point):
        """Return the point in allocentric coordinates from the point in terrain_centric"""
        if point is None:
            return None
        elif self.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            return point + self.phenomenon_memory.terrain().point
        else:
            return point

    def terrain_centric_robot_point(self):
        """Return the position of the robot relative to the terrain point"""
        if self.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            return self.allocentric_memory.robot_point - self.phenomenon_memory.terrain().point
        else:
            return self.allocentric_memory.robot_point

    def save(self) -> Memory:
        """Return a clone of memory for memory snapshot"""
        # start_time = time.time()
        saved_memory = Memory(self.phenomenon_memory.arena_id, self.robot_id)
        saved_memory.clock = self.clock
        saved_memory.emotion_code = self.emotion_code
        # Clone body memory
        saved_memory.body_memory = self.body_memory.save()
        # Clone egocentric memory
        saved_memory.egocentric_memory = self.egocentric_memory.save()
        # Clone allocentric memory
        saved_memory.allocentric_memory = self.allocentric_memory.save()
        # Clone phenomenon memory
        saved_memory.phenomenon_memory = self.phenomenon_memory.save()
        # print("Save memory duration:", time.time() - start_time, "seconds")

        return saved_memory

    def is_to_arrange(self, ego_point):
        """Return True if the focus within 400mm of the terrain center"""
        # If no terrain origin then don't arrange object
        if self.phenomenon_memory.terrain_confidence() <= TERRAIN_INITIAL_CONFIDENCE:
            return False
        # If there is a terrain origin, check if the focus is around the terrain center
        else:
            terrain_point = self.egocentric_to_terrain_centric(ego_point)
            print("Focus in terrain-centric coordinates", terrain_point)
            return np.linalg.norm(terrain_point) < ARRANGE_MAX_RADIUS

    def is_outside_terrain(self, ego_point):
        """Return True if ego_point is not None and there is a terrain and ego_point is outside"""
        allo_point = self.egocentric_to_allocentric(ego_point)
        return self.phenomenon_memory.is_outside_terrain(allo_point)

    def is_near_terrain_origin(self):
        """Return True if the robot is near the origin of the terrain"""
        terrain = self.phenomenon_memory.terrain()
        if terrain is not None:
            delta = terrain.relative_origin_point + terrain.point - self.allocentric_memory.robot_point
            return np.linalg.norm(delta) < NEAR_HOME
        else:
            return False

    # def predict_terrain_outcome(self, enaction):
    #     """Return the outcome fields related to the terrain"""
    #     predicted_outcome_terrain = {"status": "I", "duration1": enaction.command.duration}
    #     # If terrain is recognized, predict the floor outcome
    #     if self.phenomenon_memory.terrain_confidence() >= PHENOMENON_RECOGNIZED_CONFIDENCE:
    #         # The shape of the terrain in egocentric coordinates
    #         ego_shape = np.array([self.terrain_centric_to_egocentric(p) for p in self.phenomenon_memory.terrain().shape])
    #         if enaction.action.action_code == ACTION_FORWARD:
    #             # Loop over the points where the y coordinate changes sign
    #             for i in np.where(np.diff(np.sign(ego_shape[:, 1])))[0]:
    #                 if abs(ego_shape[i+1][0] - ego_shape[i][0]) < 5:
    #                     predicted_outcome_terrain["floor"] = 3
    #                     predicted_outcome_terrain["yaw"] = 0
    #                     x_line = ego_shape[i][0]
    #                 else:
    #                     slope = (ego_shape[i+1][1] - ego_shape[i][1])/(ego_shape[i+1][0] - ego_shape[i][0])
    #                     x_line = ego_shape[i][0] - ego_shape[i][1]/slope
    #                     if ego_shape[i][0] > ego_shape[i + 1][0]:
    #                         predicted_outcome_terrain["floor"] = 1
    #                         predicted_outcome_terrain["yaw"] = -45
    #                     else:
    #                         predicted_outcome_terrain["floor"] = 2
    #                         predicted_outcome_terrain["yaw"] = 45
    #                 if x_line > 0:
    #                     print("intersection point", self.phenomenon_memory.terrain().shape[i], "Distance", x_line)
    #                     duration1 = (x_line - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[self.robot_id]["forward_speed"]
    #                     if duration1 < enaction.command.duration:
    #                         predicted_outcome_terrain["duration1"] = round(duration1)
    #                     else:
    #                         predicted_outcome_terrain["duration1"] = enaction.command.duration
    #                         predicted_outcome_terrain["floor"] = 0
    #                         predicted_outcome_terrain["yaw"] = 0
    #                     break
    #         elif enaction.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
    #             # Translate the shape by the position of the floor sensor so we can check the sign of the x coordinate
    #             ego_shape -= np.array([ROBOT_FLOOR_SENSOR_X, 0, 0])  #
    #             # Loop over the points where the x coordinate pass the floor sensor
    #             for i in np.where(np.diff(np.sign(ego_shape[:, 0])))[0]:
    #                 if abs(ego_shape[i+1][1] - ego_shape[i][1]) == 0:
    #                     y_line = ego_shape[i][1]
    #                 else:
    #                     slope = (ego_shape[i+1][0] - ego_shape[i][0])/(ego_shape[i+1][1] - ego_shape[i][1])
    #                     y_line = ego_shape[i][1] - ego_shape[i][0]/slope
    #                 if enaction.command.speed_y > 0 and y_line > 0:  # Swipe left
    #                     duration1 = y_line * 1000 / ROBOT_SETTINGS[self.robot_id]["lateral_speed"]
    #                     if duration1 < enaction.command.duration:
    #                         predicted_outcome_terrain["duration1"] = round(duration1)
    #                         predicted_outcome_terrain["floor"] = 2
    #                         predicted_outcome_terrain["yaw"] = 45
    #                     else:
    #                         predicted_outcome_terrain["duration1"] = enaction.command.duration
    #                         predicted_outcome_terrain["floor"] = 0
    #                         predicted_outcome_terrain["yaw"] = 0
    #                     break
    #                 elif enaction.command.speed_y < 0 and y_line < 0:  # Swipe right
    #                     duration1 = -y_line * 1000 / ROBOT_SETTINGS[self.robot_id]["lateral_speed"]
    #                     if duration1 < enaction.command.duration:
    #                         predicted_outcome_terrain["duration1"] = round(duration1)
    #                         predicted_outcome_terrain["floor"] = 1
    #                         predicted_outcome_terrain["yaw"] = -45
    #                     else:
    #                         predicted_outcome_terrain["duration1"] = enaction.command.duration
    #                         predicted_outcome_terrain["floor"] = 0
    #                         predicted_outcome_terrain["yaw"] = 0
    #                     break
    #         # print("Predicted floor", self.predicted_floor)
    #     return predicted_outcome_terrain
