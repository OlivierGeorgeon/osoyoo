import math
import numpy as np
from pyrr import vector, Vector3, Quaternion
from .Phenomenon import Phenomenon
from .Affordance import MIDDLE_COLOR_INDEX, COLOR_DISTANCE
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from ...Robot.RobotDefine import TERRAIN_RADIUS, terrain_quaternion, terrain_north_east_point, ROBOT_FLOOR_SENSOR_X
from ...Utils import azimuth_to_quaternion, quaternion_to_direction_rad


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]
TERRAIN_INITIAL_CONFIDENCE = 10  # Must not be null to allow position correction
TERRAIN_ORIGIN_CONFIDENCE = 20  # The terrain has an absolute origin
TERRAIN_RECOGNIZE_CONFIDENCE = 30  # The terrain has been toured back to origin


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        # self.arena_id = arena_id
        self.phenomenon_type = EXPERIENCE_FLOOR
        # print("New phenomenon terrain with experience clock:", affordance.experience.clock)
        self.confidence = TERRAIN_INITIAL_CONFIDENCE
        # If the affordance is color floor then use it as absolute origin
        self.interpolation_types = [EXPERIENCE_FLOOR]
        if affordance.type == EXPERIENCE_FLOOR and affordance.color_index > 0:
            self.absolute_affordance_key = 0
            self.last_origin_clock = affordance.experience.clock
            self.origin_direction_quaternion = affordance.quaternion * Quaternion.from_z_rotation(math.pi)
            self.confidence = TERRAIN_ORIGIN_CONFIDENCE
            # The terrain position is moved to the green sensor position relative to this FLOOR affordance
            terrain_offset = -self.place_prediction_error(affordance)
            self.point += terrain_offset
            for a in self.affordances.values():
                a.point -= terrain_offset

        # Default shape TODO: learn the shape
        # self.set_shape(terrain_north_east_point(self.arena_id), terrain_quaternion(self.arena_id), None)
        # self.north_east_point = terrain_north_east_point(self.arena_id)
        # self.quaternion = terrain_quaternion(self.arena_id)

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
            if affordance.type == EXPERIENCE_FLOOR and affordance.color_index > 0:
                # If the phenomenon does not have an absolute origin yet then this affordance becomes the absolute
                if self.confidence < TERRAIN_ORIGIN_CONFIDENCE:
                    # This experience becomes the phenomenon's absolute origin
                    self.absolute_affordance_key = self.affordance_id
                    # The phenomenon's direction is the absolute direction of this affordance
                    self.origin_direction_quaternion = affordance.quaternion.copy()
                    self.last_origin_clock = affordance.clock
                    self.confidence = TERRAIN_ORIGIN_CONFIDENCE
                    # The terrain position is moved to the green sensor position relative to this FLOOR affordance
                    # (Assume the pattern of the color patch)
                    # The terrain origin remains equal to the terrain position
                    color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])
                    color_point = self.origin_direction_quaternion * color_y
                    terrain_offset = np.array(affordance.point + affordance.polar_sensor_point - color_point, dtype=int)
                    # terrain_offset = self.place_prediction_error(affordance)
                    self.point += terrain_offset
                    for a in self.affordances.values():
                        a.point -= terrain_offset
                elif np.dot(affordance.polar_sensor_point, self.origin_direction_quaternion * Vector3([10., 0, 0])) < 0:
                    # If this affordance is in the direction of the origin
                    color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])
                    affordance_green_sensor_point = affordance.point + affordance.polar_sensor_point - affordance.quaternion * color_y - self.relative_origin_point
                    print("Affordance sensor point ", affordance.point + affordance.polar_sensor_point, "affordance green sensor point", affordance_green_sensor_point)
                    position_correction = affordance_green_sensor_point
                    # Correct the position of the affordances since last time the robot visited the absolute origin
                    for a in [a for a in self.affordances.values() if a.clock > self.last_origin_clock]:
                        coef = (a.clock - self.last_origin_clock)/(affordance.clock - self.last_origin_clock)
                        ac = np.array(position_correction * coef, dtype=int)
                        a.point -= ac
                        # print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)
                    # Increase confidence if not consecutive origin affordances
                    # if affordance.clock - self.last_origin_clock > 5:
                    self.confidence = TERRAIN_RECOGNIZE_CONFIDENCE
                    self.last_origin_clock = affordance.clock

            # Interpolate the outline
            self.interpolate()
            return - position_correction  # TODO remove the minus sign
        # Affordances that do not belong to this phenomenon must return None
        return None

    def confirmation_prompt(self):
        """Return the point in polar egocentric coordinates to aim for confirmation of this phenomenon"""
        # Aim parallel to the origin direction from the relative origin point
        return self.relative_origin_point + self.origin_direction_quaternion * Vector3([500, 0, 0])
        # if self.absolute_affordance() is None:
        #     return None
        # elif np.dot(self.absolute_affordance().polar_sensor_point, self.north_east_point) < 0:
        #     # North-East
        #     return vector.set_length(self.north_east_point, 500)
        # else:
        #     return vector.set_length(self.north_east_point, -500)

        # Does not presuppose the orientation of the terrain
        # rotation_matrix = self.absolute_affordance().experience.rotation_matrix
        # point = np.array([500, 0, 0])  # Need the opposite
        # confirmation_point = matrix44.apply_to_vector(rotation_matrix, point).astype(int)  # + self.point
        # return confirmation_point

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin: " + str(self.point[0]) + "," + str(self.point[1])
        return label

    def place_prediction_error(self, affordance):
        """Return the distance computed from the affordance place minus the color_point place.
        prediction_error = computed_place(affordance) - desired_place(terrain)"""
        # Positive prediction error means reducing the position computed through path integration
        # The prediction error must be subtracted from the computed position

        # north_east_point, quaternion, _ = self.get_shape()
        # north_east_place = vector.set_length(self.north_east_point, vector.length(self.north_east_point) - ROBOT_FLOOR_SENSOR_X)
        # The color point along the y axis: red positive, purple negative.
        color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])
        color_point = self.relative_origin_point + self.origin_direction_quaternion * color_y

        # if np.dot(affordance.polar_sensor_point, self.north_east_point) < 0:
        #     # North-East
        #     color_point = self.north_east_point + self.quaternion * color_y
        #     # print("Color point NE:", color_point)
        # else:
        #     # South-West
        #     color_point = -self.north_east_point - self.quaternion * color_y
        #     # print("Color point SW:", color_point)

        p_error = affordance.point + affordance.polar_sensor_point - color_point
        # print("Place prediction error", p_error)
        return np.array(p_error, dtype=int)

    def save(self):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonTerrain(self.affordances[0].save())
        super().save(saved_phenomenon)
        return saved_phenomenon
