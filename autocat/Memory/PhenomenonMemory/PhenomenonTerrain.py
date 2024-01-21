import math
import numpy as np
from pyrr import Vector3, Quaternion
from . import PHENOMENON_RECOGNIZE_CONFIDENCE, PHENOMENON_RECOGNIZED_CONFIDENCE
from .Phenomenon import Phenomenon
from .Affordance import Affordance, MIDDLE_COLOR_INDEX, COLOR_DISTANCE
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from ...Utils import short_angle
from ...Robot.RobotDefine import LINE_X, ROBOT_COLOR_SENSOR_X


TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_PLACE, EXPERIENCE_FLOOR]
TERRAIN_INITIAL_CONFIDENCE = 10  # Must not be null to allow position correction
TERRAIN_ORIGIN_CONFIDENCE = 20  # The terrain has an absolute origin


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        self.phenomenon_type = EXPERIENCE_FLOOR
        self.confidence = TERRAIN_INITIAL_CONFIDENCE
        self.interpolation_types = [EXPERIENCE_FLOOR]

        # If the affordance is color floor then use it as absolute origin
        if affordance.type == EXPERIENCE_FLOOR and affordance.color_index > 0:
            self.absolute_affordance_key = 0
            self.last_origin_clock = affordance.experience.clock
            self.origin_direction_quaternion = affordance.quaternion.copy()
            self.confidence = TERRAIN_ORIGIN_CONFIDENCE

    def update(self, affordance: Affordance):
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
            if affordance.type == EXPERIENCE_FLOOR:
                if affordance.color_index > 0:
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
                        # The terrain origin remains at the terrain position
                        terrain_offset = self.vector_toward_origin(affordance)
                        self.point += terrain_offset
                        for a in self.affordances.values():
                            a.point -= terrain_offset
                    elif abs(short_angle(affordance.quaternion, self.origin_direction_quaternion)) < math.pi / 2 \
                            or self.confidence >= PHENOMENON_RECOGNIZE_CONFIDENCE:
                        # If this affordance is in the direction of the origin or terrain is recognized
                        # else:
                        position_correction = self.vector_toward_origin(affordance)
                        # Prediction error is the opposite of the position_correction projected along the color direction
                        self.origin_prediction_error[affordance.clock] = np.dot(-position_correction, affordance.quaternion
                                                                                * Vector3([0., 1., 0.]))
                        # Correct the position of the affordances since last time the robot visited the absolute origin
                        for a in [a for a in self.affordances.values() if a.clock > self.last_origin_clock]:
                            coef = (a.clock - self.last_origin_clock)/(affordance.clock - self.last_origin_clock)
                            ac = np.array(position_correction * coef, dtype=int)
                            a.point -= ac
                            # print("Affordance clock:", a.experience.clock, "corrected by:", ac, "coef:", coef)
                        # Increase confidence if not consecutive origin affordances
                        if affordance.clock - self.last_origin_clock > 5:
                            self.confidence = PHENOMENON_RECOGNIZE_CONFIDENCE
                        self.last_origin_clock = affordance.clock
                # Black line: Compute the position correction based on the nearest point in the terrain shape
                # DOES NOT WORK: Must use the point on the trajectory rather than the closest point
                # elif self.confidence >= PHENOMENON_RECOGNIZED_CONFIDENCE:
                #     distances = np.linalg.norm(self.shape - affordance.point, axis=1)
                #     closest_point = self.shape[np.argmin(distances)]
                #     position_correction = np.array(affordance.point - closest_point, dtype=int)
                #     print("Nearest shape point", closest_point, "Position correction", position_correction)
                #     affordance.point -= position_correction

            # Interpolate the outline
            self.interpolate()
            return - position_correction  # TODO remove the minus sign
        # Affordances that do not belong to this phenomenon must return None
        return None

    def recognize(self, category):
        """Recognize the terrain"""
        super().recognize(category)

        # The TERRAIN origin depends on the orientation of the absolute affordance
        if np.dot(self.absolute_affordance().polar_sensor_point, category.quaternion * Vector3([1., 0., 0.])) < 0:
            # Origin is North-East
            self.origin_direction_quaternion = category.quaternion.copy()
        else:
            # Origin is South-West
            self.origin_direction_quaternion = category.quaternion * Quaternion.from_z_rotation(math.pi)

        # The new relative origin is the position of green patch from the phenomenon center
        new_relative_origin = np.array(self.origin_direction_quaternion *
                                       Vector3([category.long_radius - LINE_X + ROBOT_COLOR_SENSOR_X, 0, 0]), dtype=int)

        # The position of the phenomenon is adjusted by the difference in relative origin
        terrain_offset = new_relative_origin - self.relative_origin_point
        self.point -= terrain_offset
        for a in self.affordances.values():
            a.point += terrain_offset
        self.relative_origin_point = new_relative_origin

    def confirmation_prompt(self):
        """Return the point in polar egocentric coordinates to aim for confirmation of this phenomenon"""
        # Aim parallel to the origin direction from the relative origin point
        return self.relative_origin_point + self.origin_direction_quaternion * Vector3([500, 0, 0])

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin: " + str(self.point[0]) + "," + str(self.point[1])
        return label

    def vector_toward_origin(self, affordance):
        """Return the distance between the affordance's green point and the origin point"""
        # Positive prediction error means reducing the position computed through path integration
        # The prediction error must be subtracted from the computed position

        # The color point along the y axis: red positive, purple negative.
        color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])

        if abs(short_angle(affordance.quaternion, self.origin_direction_quaternion)) < math.pi / 2:
            # Vector to origin
            # Trust the terrain direction
            v = affordance.point + affordance.polar_sensor_point - self.origin_direction_quaternion * color_y - self.relative_origin_point
            # Trust the affordance direction
            # v = affordance.point + affordance.polar_green_point() - self.relative_origin_point
        else:
            # Vector to opposite of the origin
            # Trust the terrain direction
            v = affordance.point + affordance.polar_sensor_point - self.origin_direction_quaternion * color_y + self.relative_origin_point
            # Trust the affordance direction
            # v = affordance.point + affordance.polar_green_point() + self.relative_origin_point
        # print("Place prediction error", v)
        return np.array(v, dtype=int)

    def save(self, saved_phenomenon=None):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonTerrain(self.affordances[0].save())
        super().save(saved_phenomenon)
        return saved_phenomenon
