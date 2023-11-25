import numpy as np
from .Phenomenon import PHENOMENON_INITIAL_CONFIDENCE
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ROBOT


class PhenomenonRobot:
    def __init__(self, affordance):
        """Construct the phenomenon from an affordance of type EXPERIENCE_ROBOT"""
        self.point = affordance.point.copy().astype(int)
        affordance.point = np.array([0, 0, 0], dtype=int)
        self.affordances = {0: affordance}
        self.affordance_id = 0
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE

    def update(self, affordance):
        """If EXPERIENCE_ROBOT then update the phenomenon"""
        if affordance.experience.type == EXPERIENCE_ROBOT:
            prediction_error = self.point_prediction_error(affordance)
            for a in self.affordances.values():
                a.point -= prediction_error
            self.point += prediction_error
            affordance.point = np.array([0, 0, 0], dtype=int)
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance
            return np.array([0, 0, 0], dtype=int)
        else:
            return None

    def point_prediction_error(self, affordance):
        """Return the distance computed from the affordance point minus the phenomenon point.
        prediction_error = affordance.point - phenomenon.point"""
        prediction_error = affordance.point - self.point
        return prediction_error.astype(int)

    def current(self):
        """Return the current affordance that characterize the phenomenon"""
        return self.affordances[self.affordance_id]

    def save(self, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon = PhenomenonRobot(self.affordances[0].save(experiences))
        saved_phenomenon.point = self.point.copy()
        saved_phenomenon.confidence = self.confidence
        saved_phenomenon.affordances = {key: a.save(experiences) for key, a in self.affordances.items()}
        saved_phenomenon.affordance_id = self.affordance_id
        return saved_phenomenon
