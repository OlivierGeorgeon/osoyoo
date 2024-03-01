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
from ..Integrator.OutcomeCode import FOCUS_TOO_FAR_DISTANCE
from ..Integrator.Integrator import integrate
from ..Enaction.Predict import push_objects
from .EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO

GRID_WIDTH = 30  # 15   # 100 Number of cells wide
GRID_HEIGHT = 100  # 70  # 45  # 200 Number of cells high
NEAR_HOME = 300    # (mm) Max distance to consider near home
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
        self.egocentric_memory = EgocentricMemory(robot_id)
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
                        print("Focus near terrain center:", is_to_arrange, ". Before terrain center:", is_closer,
                              ". Other robot angry:", self.phenomenon_memory.other_robot_is_angry())
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

    def update(self, enaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.focus_point = enaction.trajectory.focus_point
        self.egocentric_memory.prompt_point = enaction.trajectory.prompt_point
        # print("Trajectory prompt", enaction.trajectory.prompt_point)

        # Push objects before moving the robot
        push_objects(enaction.trajectory, self)

        # Translate the robot before applying the yaw
        # print("Robot relative translation", enaction.translation)
        self.allocentric_memory.move(self.body_memory.body_quaternion, enaction.trajectory, enaction.clock)
        self.body_memory.update(enaction)

        # Compute the other robot's position relative to the current state of memory
        if enaction.message is not None:
            enaction.message.set_position_matrix(self)

        # Update egocentric memory
        self.egocentric_memory.update_and_add_experiences(enaction)

        # Push objects
        # push_objects(enaction.trajectory, self)

        # The integrator may again update the robot's position
        # Call the integrator to create and update the phenomena
        integrate(self)

        """Update allocentric memory on the basis of body, phenomenon, and egocentric memory"""
        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory, self.clock)

        # Mark the affordances
        self.allocentric_memory.update_affordances(self.phenomenon_memory, self.clock)

        # Update the focus in allocentric memory
        allo_focus = self.egocentric_to_allocentric(self.egocentric_memory.focus_point)
        self.allocentric_memory.update_focus(allo_focus, self.clock)

        # Update the prompt in allocentric memory
        allo_prompt = self.egocentric_to_allocentric(self.egocentric_memory.prompt_point)
        self.allocentric_memory.update_prompt(allo_prompt, self.clock)

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

    def save(self):
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
            print("Focus in terrain-centric coordinates", np.round(terrain_point))
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
