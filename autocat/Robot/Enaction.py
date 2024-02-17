from .Command import Command, DIRECTION_FRONT
from ..Enaction.Predict import predict_outcome
from ..Enaction.Trajectory import Trajectory
from ..Integrator.OutcomeCode import outcome_code


class Enaction:
    """An Enaction object handles the enaction of an interaction by the robot
    1. Workspace instantiates the enaction
    2. CtrlRobot sends the command to the robot
    3. CtrlRobot computes the outcome received from the robot
    4. CtrlRobot call ternminate(outcome)
    """
    def __init__(self, action, memory, direction=DIRECTION_FRONT, span=40, caution=0):
        """Initialize the enaction upon creation. Will be adjusted before generating the command"""
        # The initial arguments
        self.action = action
        self.clock = memory.clock

        # Generate the command to the robot
        self.command = Command(self.action, self.clock, memory.egocentric_memory.prompt_point,
                               memory.egocentric_memory.focus_point, direction, span, memory.emotion_code, caution)

        # Initialize the predicted memory
        self.predicted_memory = memory.save()
        self.predicted_memory.clock += 1

        # Compute the predicted outcome and update the predicted memory
        self.predicted_outcome = predict_outcome(self.command, self.predicted_memory)

        # Initialize the trajectory
        self.trajectory = Trajectory(memory, self.predicted_outcome.yaw, self.command.speed, self.command.span)

        # The predicted outcome code
        self.predicted_outcome_code = outcome_code(self.predicted_memory, self.trajectory, self.predicted_outcome)

        # The key used for hash
        self.key = (self.action.action_code, self.predicted_outcome_code)

        # The actual outcome
        self.outcome = None
        self.outcome_code = ""

        # The message received from other robot
        self.message = None
        # Message sent to other robots
        self.message_sent = False

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
        """Adjust the spatial modifiers of the enaction.
        Compute the command to send to the robot.
        Initialize the simulation"""

        print("Command", self.command.serialize())
        print("Predicted outcome", self.predicted_outcome)
        # Update the body_quaternion to avoid errors in the estimated yaw
        self.trajectory.body_quaternion = body_quaternion.copy()

    def terminate(self, outcome):
        """Computes the body_quaternion, the translation, the displacement_matrix, the focus and the prompt."""
        self.outcome = outcome
        self.trajectory.track_displacement(self.outcome)
        self.trajectory.track_focus(self.outcome)

    def succeed(self):
        """Return True if the enaction succeeded: no floor or impact outcome"""
        return self.outcome.floor == 0 and self.outcome.impact == 0

    def current_enaction(self):
        """Used if the enaction is taken as a composite enaction"""
        return self

    def increment(self):
        """Used if the enaction is taken as a composite enaction"""
        return False
