from .Command import Command, DIRECTION_FRONT
from ..Enaction.Predict import generate_prediction
from ..Enaction.Trajectory import Trajectory


class Enaction:
    """An enaction is defined by its action and its predicted outcome code.
    It contains a command, predicted memory, predicted outcome, actual trajectory, and actual outcome."""

    def __init__(self, interaction, memory, direction=DIRECTION_FRONT, span=40, caution=0):
        """Generate the command, predicted memory, and predicted outcome."""
        # The initial arguments
        self.action = interaction.action
        self.predicted_memory = memory  # must be a clone of the current memory
        self.clock = memory.clock

        # Generate the command to the robot
        self.command = Command(self.action, memory, direction, span, caution)

        # Initialize the actual trajectory (clone again the necessary elements of memory)
        self.trajectory = Trajectory(memory, self.command)

        # Generate the predicted memory and the predicted outcome
        self.predicted_memory.clock += 1
        self.predicted_outcome, self.predicted_outcome_code = generate_prediction(self.command, self.predicted_memory)

        # The key used for hash
        self.key = (self.action.action_code, self.predicted_outcome_code)

        # The actual outcome
        self.outcome = None
        self.outcome_code = ""

        # The message received from other robot
        self.message = None
        # Message sent to other robots
        self.is_message_sent = False

    def __hash__(self):
        """Return the hash computed from the key"""
        return hash(self.key)

    def __eq__(self, other):
        """Enactions are equal if they have the same action and predicted outcome"""
        if isinstance(other, Enaction):
            return self.key == other.key
        return NotImplemented

    def __str__(self):
        """Return a representation of the key tuple (action, predicted outcome)"""
        return self.key.__str__()

    def begin(self, body_quaternion):
        """Update the body_quaternion to avoid errors in the estimated yaw"""
        print("Command", self.command.serialize())
        print("Predicted outcome", self.predicted_outcome)
        self.trajectory.body_quaternion = body_quaternion.copy()

    def terminate(self):
        """Computes the actual trajectory: body_quaternion, translation, displacement_matrix, focus, and prompt."""
        # self.outcome = outcome
        # Mitigated the outcome.duration1 from prediction and actual
        # if self.predicted_outcome.floor and self.outcome.floor and \
        #         self.predicted_outcome.duration1 != self.outcome.duration1:
        #     self.outcome.duration1 = round((self.predicted_outcome.duration1 * self.predicted_outcome.confidence +
        #                                     self.outcome.duration1 * (100 - self.predicted_outcome.confidence)) / 100)
        #     print("Outcome adjusted Duration1:", self.outcome.duration1)
        self.trajectory.track_displacement(self.outcome)
        self.trajectory.track_focus(self.outcome)

    def succeed(self):
        """Return True if floor and impact were correctly predicted"""
        if (self.outcome.floor > 0) != (self.predicted_outcome.floor > 0):
            return False
        if (self.outcome.impact > 0) != (self.predicted_outcome.impact > 0):
            return False
        return True
        # return self.outcome.floor == self.predicted_outcome.floor and self.outcome.impact == 0

    # def current_enaction(self):
    #     """Used if the enaction is taken as a composite enaction"""
    #     return self

    # def increment(self):
    #     """Used if the enaction is taken as a composite enaction"""
    #     return False
