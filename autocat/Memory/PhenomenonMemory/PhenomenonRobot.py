import numpy as np
from pyrr import Vector3
from . import PHENOMENON_RECOGNIZABLE_CONFIDENCE
from .Phenomenon import Phenomenon
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ROBOT


class PhenomenonRobot(Phenomenon):
    """A phenomenon representing another robot"""
    # def __init__(self, affordance):
    #     """Construct the phenomenon from an affordance of type EXPERIENCE_ROBOT"""
    #     super().__init__(affordance)
    # self.point = affordance.point.copy().astype(int)
    # affordance.point = np.array([0, 0, 0], dtype=int)
    # self.affordances = {0: affordance}
    # self.affordance_id = 0

    def update(self, affordance):
        """If EXPERIENCE_ROBOT then update the phenomenon"""
        if affordance.type == EXPERIENCE_ROBOT:
            self.last_origin_clock = affordance.clock
            vector_toward_origin = self.vector_toward_origin(affordance)
            for a in self.affordances.values():
                a.point -= vector_toward_origin
            self.point += vector_toward_origin
            affordance.point = np.array([0, 0, 0], dtype=int)
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance
            # Rotate the shape to the orientation of the robot
            self.shape = np.array([(affordance.quaternion * Vector3(p)) for p in self.shape])
            self.set_path()
            return np.array([0, 0, 0], dtype=int)
        else:
            return None

    def recognize(self, category):
        """Recognize the robot category and adjust the shape to the orientation"""
        super().recognize(category)
        # Rotate the shape to the orientation of the robot
        self.shape = np.array([(self.latest_added_affordance().quaternion * Vector3(p)) for p in self.shape])
        self.set_path()

    # def latest_added_affordance(self):
    #     """Return the latest affordance added to this phenomenon"""
    #     return self.affordances[self.affordance_id]
    #
    def save(self):
        """Return a clone of the phenomenon for memory snapshot"""
        saved_phenomenon = PhenomenonRobot(self.affordances[0].save())
        super().save(saved_phenomenon)
        return saved_phenomenon
