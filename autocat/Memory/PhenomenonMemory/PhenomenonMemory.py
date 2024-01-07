import numpy as np
from pyrr import Vector3
from .PhenomenonCategory import PhenomenonCategory
from .PhenomenonObject import PhenomenonObject
from .PhenomenonTerrain import PhenomenonTerrain, TERRAIN_EXPERIENCE_TYPES, TERRAIN_ORIGIN_CONFIDENCE
from .PhenomenonRobot import PhenomenonRobot
from .. import EMOTION_ANGRY
from ..EgocentricMemory.Experience import EXPERIENCE_ROBOT, EXPERIENCE_FLOOR
from ...Robot.RobotDefine import TERRAIN_RADIUS

TER = 0
ROBOT1 = -1  # The last other robot from which this robot receives a message TODO Handle more robots


class PhenomenonMemory:
    def __init__(self, arena_id):
        self.arena_id = arena_id
        self.phenomena = {}  # Phenomenon 0 is the terrain
        self.phenomenon_id = 0  # Used for object phenomena

        # Initialize the phenomenon categories
        category_terrain = PhenomenonCategory(EXPERIENCE_FLOOR, TERRAIN_RADIUS[self.arena_id]["short_radius"],
                                              TERRAIN_RADIUS[self.arena_id]["radius"],
                                              TERRAIN_RADIUS[self.arena_id]["azimuth"])
        self.phenomenon_categories = {TER: category_terrain}  # Phenomenon_category 0 is the terrain

    def terrain_confidence(self):
        """Return the confidence in the terrain: 0 if no terrain found yet."""
        if TER in self.phenomena:
            return self.phenomena[TER].confidence
        else:
            return 0

    def watch_point(self):
        """The point where the robot returns for watching in allocentric coordinates"""
        # If the terrain has has an origin
        if self.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            # Set the watch point half way between the center and the color patch
            point = self.phenomena[TER].origin_direction_quaternion() * \
                    Vector3([TERRAIN_RADIUS[self.arena_id]["radius"] * 0.5, 0, 0])
            return point + self.phenomena[TER].point
        # If the terrain has not been identified then et the watch point as the birth point
        else:
            return np.array([0, 0, 0])

    def arrange_point(self):
        """Return the point where the robot should arrange the objects in terrain centric coordinates"""
        # If the terrain has been toured
        if self.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE:
            # Set the arrange point half way to the other side of the terrain
            point = self.phenomena[TER].origin_direction_quaternion() * \
                    Vector3([-TERRAIN_RADIUS[self.arena_id]["radius"] * 0.5, 0, 0])
            # return point  # Arrange point is on the opposite side
            return np.array([0, 0, 0])  # Arrange point is the center of the terrain
        # If the terrain has not been identified then the arrange point is the birth point
        else:
            return np.array([0, 0, 0])

    def is_outside_terrain(self, allo_point):
        """Return True if allo_point is not None and there is a confident terrain and allo_point is outside"""
        # If no point then False
        if allo_point is None:
            is_outside_terrain = False
        # If terrain not confident then False
        elif self.terrain_confidence() < TERRAIN_ORIGIN_CONFIDENCE:
            is_outside_terrain = False
        # If the point is outside the confident terrain then True
        else:
            is_outside_terrain = not self.phenomena[TER].is_inside(allo_point)
        return is_outside_terrain

    def create_phenomenon(self, affordance):
        """Create a new phenomenon depending of the type of the affordance"""
        # Must always create a phenomenon
        if affordance.type in TERRAIN_EXPERIENCE_TYPES:
            self.phenomena[TER] = PhenomenonTerrain(affordance, self.arena_id)
            return TER
        if affordance.type == EXPERIENCE_ROBOT:
            self.phenomena[ROBOT1] = PhenomenonRobot(affordance)
            return ROBOT1
        else:
            self.phenomenon_id += 1
            self.phenomena[self.phenomenon_id] = PhenomenonObject(affordance)
            return self.phenomenon_id

    def create_phenomena(self, affordances):
        """Create new phenomena from the list of affordances"""
        new_phenomena_id = []
        for affordance in affordances:
            if len(new_phenomena_id) == 0:
                new_phenomena_id.append(self.create_phenomenon(affordance))
            else:
                clustered = False
                # Look if the new affordance can be attached to an existing new phenomenon
                for new_phenomenon_id in new_phenomena_id:
                    print("Update new phenomenon")
                    if self.phenomena[new_phenomenon_id].update(affordance) is not None:
                        clustered = True
                        break
                if not clustered:
                    new_phenomena_id.append(self.create_phenomenon(affordance))
        # self.object_phenomena.extend(new_phenomena_id)

    def update_phenomena(self, affordances):
        """Try to attach a list of affordances to phenomena in the list.
        Returns the affordances that have not been attached, and the average translation"""
        position_correction = np.array([0, 0, 0], dtype=int)
        sum_translation = np.array([0, 0, 0], dtype=int)
        number_of_add = 0
        remaining_affordances = affordances.copy()

        for affordance in affordances:
            for phenomenon in self.phenomena.values():
                delta = phenomenon.update(affordance)
                if delta is not None:
                    remaining_affordances.remove(affordance)
                    # Null correction do not count (to be improved)
                    if round(np.linalg.norm(delta)) > 0:
                        sum_translation += delta.astype(int)
                        number_of_add += 1
                    # Don't look the other phenomena
                    break
        if number_of_add > 0:
            position_correction = np.divide(sum_translation, number_of_add)

        return remaining_affordances, position_correction

    def other_robot_is_angry(self):
        """Return True if there is another robot and it is angry"""
        if ROBOT1 in self.phenomena and self.phenomena[ROBOT1].current().color_index == EMOTION_ANGRY:
            return True
        else:
            return False

    def save(self):
        """Return a clone of phenomenon memory for memory snapshot"""
        saved_phenomenon_memory = PhenomenonMemory(self.arena_id)
        saved_phenomenon_memory.phenomenon_categories = {k: c.save() for k, c in self.phenomenon_categories.items()}
        saved_phenomenon_memory.phenomena = {k: p.save() for k, p in self.phenomena.items()}
        saved_phenomenon_memory.phenomenon_id = self.phenomenon_id
        return saved_phenomenon_memory
