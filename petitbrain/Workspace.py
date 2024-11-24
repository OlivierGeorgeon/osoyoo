import json
import numpy as np
import structlog
from .Proposer.Action import create_actions, ACTION_FORWARD, ACTIONS, ACTION_TURN, ACTION_BACKWARD
from .Memory.Memory import Memory
from .Memory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE
from .Robot.Enaction import Enaction
from .Robot.Command import DIRECTION_BACK
from .Robot.Message import Message
from .Enaction.Enacter import Enacter
from .Enaction.Simulator import Simulator
from .Enaction import ENACTION_STEP_RENDERING
from .Enaction.CompositeEnaction import CompositeEnaction
from .Integrator.PredictionError import PredictionError
from .Integrator.Calibrator import Calibrator
from .Enaction import KEY_ENGAGEMENT_ROBOT, KEY_CONTROL_DECIDER, KEY_ENGAGEMENT_IMAGINARY
from .SoundPlayer import SoundPlayer, SOUND_CLEAR
from .Proposer.Interaction import OUTCOME_PROMPT, create_interactions
from .Proposer.PredefinedInteractions import create_sequence_interactions
from .Robot.RobotDefine import ROBOT_SETTINGS

KEY_CONTROL_USER = "M"  # Manual mode : controlled by the user
KEY_CLEAR = "C"  # Clear the stack of interactions to enact next
KEY_PREDICTION_ERROR = "E"  # Compute the prediction errors
KEY_ENCLOSE = "N"
KEY_POSITION = "P"
KEY_COMPARE = ""


class Workspace:
    """The Workspace supervises the interaction cycle. It produces the intended_interaction
    and processes the enacted interaction """

    def __init__(self, arena_id, robot_id=""):

        # If the robot ID is not in RobotDefine.py then assume the arena_id is the robot's IP address
        if robot_id not in ROBOT_SETTINGS:
            ROBOT_SETTINGS["0"]["IP"] = {"0": arena_id}
            arena_id = "0"
            robot_id = "0"

        self.arena_id = arena_id
        self.robot_id = robot_id

        self.actions = create_actions(robot_id)
        self.primitive_interactions = create_interactions(self.actions)
        self.sequence_interactions = create_sequence_interactions(self.primitive_interactions)

        self.memory = Memory(arena_id, robot_id)
        self.enacter = Enacter(self)
        self.simulator = Simulator(self)
        self.prediction_error = PredictionError(self)
        self.calibrator = Calibrator(self)

        self.composite_enaction = None  # The composite enaction to enact
        self.enaction = None  # The primitive enaction to enact

        self.decider_id = "Manual"
        self.control_mode = KEY_CONTROL_USER
        self.engagement_mode = KEY_ENGAGEMENT_ROBOT

        # Controls which phenomenon view to display
        self.ctrl_phenomenon_view = None
        self.ctrl_place_cell_view = None

        # The tracer
        self.tracer = structlog.get_logger()

        # Message from other robot
        self.message = None

        # The last composite interaction proposed manually
        self.manual_composite_interaction = None

    def main(self, dt):
        """The main handler of the interaction cycle:
        organize the generation of the intended_interaction and the processing of the enacted_interaction."""
        self.enacter.main(dt)

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() in [KEY_CONTROL_DECIDER, KEY_CONTROL_USER]:
            self.control_mode = user_key.upper()
        elif user_key.upper() in [KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY]:
            self.engagement_mode = user_key.upper()
        elif user_key.upper() in ACTIONS:
            # Only process actions when the robot is IDLE
            if self.composite_enaction is None:
            # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                i0 = self.primitive_interactions[(user_key.upper(), OUTCOME_PROMPT)]
                self.composite_enaction = CompositeEnaction(None, 'Manual', np.array([1, 1, 1]), [i0], self.memory.save())
        elif user_key.upper() == "/":
            # If key ALIGN then turn and move forward to the prompt
            if self.composite_enaction is None:
            # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                self.composite_enaction = CompositeEnaction(None, 'Manual', np.array([1, 1, 1]),
                                                            self.sequence_interactions["TF-P"], self.memory.save())
        elif user_key.upper() == ":" and self.memory.egocentric_memory.focus_point is not None:
            # If key ALIGN BACK then turn back and move backward to the prompt
            if self.composite_enaction is None:
            # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                # The first enaction: turn the back to the prompt
                i0 = self.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, self.memory.save(), direction=DIRECTION_BACK)
                # Second enaction: move forward to the prompt
                i1 = self.primitive_interactions[(ACTION_BACKWARD, OUTCOME_PROMPT)]
                e1 = Enaction(i1, e0.predicted_memory.save())
                self.composite_enaction = CompositeEnaction([e0, e1], 'Manual', np.array([1, 1, 1]))
        # elif user_key.upper() == "P" and self.memory.egocentric_memory.focus_point is not None:
        #     # If key PUSH and has focus then create the push sequence
        #     if self.composite_enaction is None:
        #     # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
        #         # First enaction: turn to the prompt
        #         i0 = self.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
        #         e0 = Enaction(i0, self.memory.save())
        #         # Second enaction: move forward to the prompt
        #         i1 = self.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
        #         e1 = Enaction(i1, e0.predicted_memory.save())
        #         # Third enaction: turn to the prompt which is copied from the focus because it may be cleared
        #         i2 = self.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
        #         e2_memory = e1.predicted_memory.save()
        #         e2_memory.egocentric_memory.prompt_point = e1.predicted_memory.egocentric_memory.focus_point.copy()
        #         e2 = Enaction(i2, e2_memory)
        #         # Fourth enaction: move forward to the new prompt
        #         i3 = self.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
        #         e3 = Enaction(i3, e2.predicted_memory.save())
        #         self.composite_enaction = CompositeEnaction([e0, e1, e2, e3], 'Manual', np.array([1, 1, 1]))
        elif user_key.upper() == KEY_CLEAR:
            # Clear the current composite enaction and reset the enaction cycle
            SoundPlayer.play(SOUND_CLEAR)
            self.composite_enaction = None
            # Restore memory
            neurotransmitter_point = self.memory.body_memory.neurotransmitters.copy()
            confidence = self.memory.phenomenon_memory.terrain_confidence()
            self.memory = self.enacter.memory_snapshot
            self.memory.body_memory.neurotransmitters[:] = neurotransmitter_point
            if self.memory.phenomenon_memory.terrain() is not None:
                self.memory.phenomenon_memory.terrain().confidence = confidence
            self.enacter.interaction_step = ENACTION_STEP_RENDERING
            # TODO: prevent a crash when the enaction has been cleared and then an outcome is received after
        elif user_key.upper() == KEY_PREDICTION_ERROR:
            self.prediction_error.plot()
        elif user_key.upper() == KEY_POSITION:
            # Move the robot by the position correction from place cell memory
            self.memory.adjust_robot_position()
            self.show_place_cell(self.memory.place_memory.current_cell_id)
            self.enacter.interaction_step = ENACTION_STEP_RENDERING

    def emit_message(self):
        """Return the message to answer to another robot"""

        message = {"robot": self.robot_id, "clock": self.memory.clock,
                   "azimuth": self.memory.body_memory.body_azimuth(), "emotion": self.memory.body_memory.emotion_code()}

        # If the terrain has been found then send the position relative to the terrain origin
        if self.memory.phenomenon_memory.terrain_confidence() > TERRAIN_ORIGIN_CONFIDENCE:  # TERRAIN_INITIAL_CONFIDENCE:
            robot_point = self.memory.terrain_centric_robot_point()
            message['position'] = robot_point.astype(int).tolist()

        # Add information about the current enaction only once
        if self.enaction is not None and not self.enaction.is_message_sent:
            # The destination position in polar-egocentric
            # TODO handle destination
            # destination_point = quaternion.apply_to_vector(self.enaction.body_quaternion,
            #                                                self.enaction.command.anticipated_translation)
            # message['destination'] = destination_point.astype(int).tolist()

            # The focus point
            if self.enaction.trajectory.focus_point is not None:
                focus_point = self.memory.egocentric_to_polar_egocentric(self.enaction.trajectory.focus_point)
                message['focus'] = focus_point.astype(int).tolist()

            # Mark the message for this enaction sent
            self.enaction.is_message_sent = True

        return json.dumps(message)

    def receive_message(self, message_string):
        """Store the latest message received from other robots in the Workspace. It will be used during INTEGRATING"""
        # If no message then keep the previous one
        if message_string is not None:
            self.message = Message(message_string)

    def show_place_cell(self, place_cell_id):
        """Display this place cell if not zero"""
        if place_cell_id > 0 and self.ctrl_place_cell_view is not None:
            place_cell = self.memory.place_memory.place_cells[place_cell_id]
            self.ctrl_place_cell_view.view.set_caption(f"Place Cell {place_cell_id} at {place_cell}")
            self.ctrl_place_cell_view.place_cell_id = place_cell_id
            # self.ctrl_place_cell_view.update_cue_displays()
