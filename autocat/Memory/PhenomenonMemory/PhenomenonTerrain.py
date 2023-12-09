import math
import numpy as np
from pyrr import vector, Vector3, Quaternion
from .Phenomenon import Phenomenon
from .Affordance import MIDDLE_COLOR_INDEX, COLOR_DISTANCE
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from ...Robot.RobotDefine import TERRAIN_RADIUS, terrain_quaternion, terrain_north_east_point
from ...Utils import azimuth_to_quaternion


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]
TERRAIN_INITIAL_CONFIDENCE = 10  # Must not be null to allow position correction
TERRAIN_ORIGIN_CONFIDENCE = 20  # The terrain has an absolute origin
TERRAIN_CIRCUMFERENCE_CONFIDENCE = 30  # The terrain has been toured back to origin


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance, arena_id):
        super().__init__(affordance)
        self.arena_id = arena_id
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)
        self.confidence = TERRAIN_INITIAL_CONFIDENCE
        # If the affordance is color floor then use it as absolute origin
        self.interpolation_types = [EXPERIENCE_FLOOR]
        if affordance.absolute_point_interest():
            self.absolute_affordance_key = 0
            self.last_origin_clock = affordance.experience.clock

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""

        # Check if the affordance is acceptable for this phenomenon type
        if affordance.type in TERRAIN_EXPERIENCE_TYPES:
            # Add the affordance
            affordance.point = affordance.point.astype(int) - self.point.astype(int)
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance
            position_correction = np.array([0, 0, 0], dtype=int)

            # Check if this affordance is absolute
            if affordance.absolute_point_interest():
                # If the phenomenon does not have an absolute origin yet then this affordance becomes the absolute
                if self.absolute_affordance_key is None:
                    # This experience becomes the phenomenon's absolute origin
                    self.absolute_affordance_key = self.affordance_id
                    self.last_origin_clock = affordance.clock
                    terrain_offset = self.place_prediction_error(affordance)
                    self.point += terrain_offset
                    # All the position of affordance including this one are adjusted
                    for a in self.affordances.values():
                        a.point -= terrain_offset
                    self.confidence = TERRAIN_ORIGIN_CONFIDENCE
                else:
                    position_correction = self.place_prediction_error(affordance)
                    # Correct the position of the affordances since last time the robot visited the absolute origin
                    for a in [a for a in self.affordances.values() if a.clock > self.last_origin_clock]:
                        coef = (a.clock - self.last_origin_clock)/(affordance.clock - self.last_origin_clock)
                        ac = np.array(position_correction * coef, dtype=int)
                        a.point -= ac
                        # print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)
                    # Increase confidence if not consecutive origin affordances
                    if affordance.clock - self.last_origin_clock > 5:
                        self.confidence = TERRAIN_CIRCUMFERENCE_CONFIDENCE
                    self.last_origin_clock = affordance.clock

            # Interpolate the outline
            self.interpolate()
            return - position_correction  # TODO remove the minus sign
        # Affordances that do not belong to this phenomenon must return None
        return None

    def origin_point(self):
        """Return the position where to go to check the origin in allocentric coordinates"""
        if self.absolute_affordance() is None:
            return None
        elif np.dot(self.absolute_affordance().polar_sensor_point, terrain_north_east_point(self.arena_id)) < 0:
            # North-East
            return terrain_north_east_point(self.arena_id) + self.point
        else:
            return -terrain_north_east_point(self.arena_id) + self.point

        # return self.absolute_affordance().green_point() + self.point

    def confirmation_prompt(self):
        """Return the point in polar egocentric coordinates to aim for confirmation of this phenomenon"""
        # Parallel to the absolute affordance direction
        if self.absolute_affordance() is None:
            return None
        elif np.dot(self.absolute_affordance().polar_sensor_point, terrain_north_east_point(self.arena_id)) < 0:
            # North-East
            return vector.set_length(terrain_north_east_point(self.arena_id), 500)
        else:
            return vector.set_length(terrain_north_east_point(self.arena_id), -500)
        # Does not presuppose the orientation of the terrain
        # rotation_matrix = self.absolute_affordance().experience.rotation_matrix
        # point = np.array([500, 0, 0])  # Need the opposite
        # confirmation_point = matrix44.apply_to_vector(rotation_matrix, point).astype(int)  # + self.point
        # return confirmation_point

    def origin_direction_quaternion(self):
        """Return the quaternion representing the direction of the color patch from the center of the terrain"""
        if self.absolute_affordance() is None:
            return None
        if np.dot(self.absolute_affordance().polar_sensor_point, terrain_north_east_point(self.arena_id)) < 0:
            # The North-East patch
            return azimuth_to_quaternion(TERRAIN_RADIUS[self.arena_id]["azimuth"])
        else:
            # South west patch
            return azimuth_to_quaternion(TERRAIN_RADIUS[self.arena_id]["azimuth"] + 180)

    def outline(self):
        """Return the terrain outline points"""
        return self.interpolation_points

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin: " + str(self.point[0]) + "," + str(self.point[1])
        return label

    def place_prediction_error(self, affordance):
        """Return the distance computed from the affordance place minus the color_point place.
        prediction_error = computed_place(affordance) - desired_place(terrain)"""
        # Positive prediction error means reducing the position computed through path integration
        # The prediction error must be subtracted from the computed position

        # The color point along the y axis: red positive, purple negative.
        color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])

        if np.dot(affordance.polar_sensor_point, terrain_north_east_point(self.arena_id)) < 0:
            # North-East
            color_point = terrain_north_east_point(self.arena_id) + terrain_quaternion(self.arena_id) * color_y
            # print("Color point NE:", color_point)
        else:
            # South-West
            color_point = -terrain_north_east_point(self.arena_id) - terrain_quaternion(self.arena_id) * color_y
            # print("Color point SW:", color_point)

        p_error = affordance.point + affordance.polar_sensor_point - color_point
        # print("Place prediction error", p_error)
        return np.array(p_error, dtype=int)

    def save(self):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonTerrain(self.affordances[0].save(), self.arena_id)
        super().save(saved_phenomenon)
        return saved_phenomenon

