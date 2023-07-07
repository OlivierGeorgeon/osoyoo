import numpy as np
from pyrr import matrix44
from .Phenomenon import Phenomenon, PHENOMENON_DELTA, PHENOMENON_CONFIDENCE_PRUNE
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, \
    EXPERIENCE_IMPACT

OBJECT_EXPERIENCE_TYPES = [EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_BLOCK, EXPERIENCE_IMPACT]


class PhenomenonObject(Phenomenon):
    """A hypothetical phenomenon related to echo localization"""
    def __init__(self, affordance):
        super().__init__(affordance)
        self.absolute_affordance_key = 0  # The initial affordance is the origin
        # print("New phenomenon Object")

    def update(self, affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""

        # Only echo experiences
        if affordance.experience.type not in OBJECT_EXPERIENCE_TYPES:
            return None  # Must return None to check if this affordance can be associated with another phenomenon

        position_correction = np.array([0, 0, 0], dtype=int)
        # The affordance is repositioned in reference to the phenomenon
        # (Do not modify the affordance if it does not belong to this phenomenon)
        relative_affordance_point = np.array(affordance.point - self.point, dtype=int)

        # Find the reference affordance
        nearest_affordance = self.reference_affordance(affordance)
        reference_affordance_point = nearest_affordance.point
        # Reference point based on similarity of affordances TODO choose between nearest or similar
        similar_affordance_points = np.array([a.point for a in self.affordances.values() if a.is_similar_to(affordance)])
        if similar_affordance_points.size > 0:
            # print("Correct reference affordance from similar affordances")
            reference_affordance_point = similar_affordance_points.mean(axis=0)

        # The delta of position from the reference affordance point
        delta = reference_affordance_point - relative_affordance_point

        # If the new affordance is attributed to this phenomenon
        if np.linalg.norm(delta) < PHENOMENON_DELTA:
            # If the affordance is similar to the origin affordance (near position and direction)
            if affordance.is_similar_to(self.affordances[0]):
                # The affordance in (0,0) and correct the robot's position
                # Only if a tour has been completed
                if self.nb_tour > 0:
                    position_correction = -relative_affordance_point
                    print("Phenomenon position correction:", position_correction)
            else:
                position_correction = np.array(self.confidence * delta, dtype=int)

            # Check if a new tour has started when reaching opposite direction
            if affordance.is_opposite_to(self.affordances[0]):
                self.tour_started = True
            # If a new tour has been completed then increase confidence
            if self.tour_started and affordance.is_clockwise_from(self.affordances[0]):
                self.tour_started = False
                self.nb_tour += 1
                self.confidence = min(self.confidence + 0.2, 1.)

            # Move the new affordance's position to relative reference
            affordance.point = relative_affordance_point + position_correction

            # Prune: remove the affordances that are nearer or equal to the sensor
            self.prune(affordance)
            # Append the new affordance
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance

            # Return the correction to apply to the robot's position
            return position_correction
        else:
            # This affordance does not belong to this phenomenon
            return None  # Must return None to check if this affordance can be associated with another phenomenon

    def reference_affordance(self, affordance):
        """Find the previous affordance that serves as the reference to correct the position"""
        # TODO the reference algorithm must be improved
        # In this implementation the reference affordance is the affordance closest to the head
        phenomenon_points = np.array([a.point for a in self.affordances.values()])
        # head_point = np.array(matrix44.apply_to_vector(affordance.experience.sensor_matrix, [0, 0, 0]))
        # head_point = affordance.experience.sensor_point.copy()
        dist2 = np.sum((phenomenon_points - affordance.experience.sensor_point())**2, axis=1)
        return list(self.affordances.values())[dist2.argmin()]

    def prune(self, affordance):
        """Remove previous affordances to keep their number under control"""
        # TODO The Prune algorithm must be improved
        if self.confidence > PHENOMENON_CONFIDENCE_PRUNE:
            nb_affordance = len(self.affordances.values())
            # self.affordances = [a for a in self.affordances if
            #                     numpy.linalg.norm(a.point - head_point) >
            #                     numpy.linalg.norm(affordance.point - head_point)]
            # self.affordances.remove(nearest_affordance)
            for a in self.affordances.values():  # TODO make sure that it does not prune the origin affordance
                # if numpy.linalg.norm(a.point - head_point) < numpy.linalg.norm(affordance.point - head_point):
                #     self.affordances.remove(a)
                #     break  # Remove only the first similar affordance found
                if a.is_similar_to(affordance):
                    # Remove affordance similar to this affordance that are not the affordance 0
                    self.affordances = {key: val for key, val in self.affordances.items() if val != a or key == 0}
                    break  # Remove only the first similar affordance found
            print("Prune:", nb_affordance - len(self.affordances), "affordances removed.")

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        # The affordance 0 is not removed
        saved_phenomenon = PhenomenonObject(self.affordances[0].save(experiences))
        super().save(saved_phenomenon, experiences)
        return saved_phenomenon
