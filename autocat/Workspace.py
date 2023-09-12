import json
from pyrr import quaternion
from playsound import playsound
from .Decider.DeciderCircle import DeciderCircle
from .Decider.DeciderExplore import DeciderExplore
from .Decider.DeciderWatch import DeciderWatch
from .Decider.Action import create_actions, ACTION_FORWARD, ACTIONS, ACTION_TURN
from .Memory.Memory import Memory
from .Memory.PhenomenonMemory.PhenomenonMemory import TER
from .Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_INITIAL_CONFIDENCE
from .Integrator.Integrator import Integrator
from .Robot.Enaction import Enaction
from .Robot.Message import Message
from .Enaction.Enacter import Enacter
from .Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_INTENDING, ENACTION_STEP_ENACTING, \
    ENACTION_STEP_INTEGRATING, ENACTION_STEP_REFRESHING
from .Enaction.CompositeEnaction import CompositeEnaction

KEY_CONTROL_DECIDER = "A"  # Automatic mode: controlled by the deciders
KEY_CONTROL_USER = "M"  # Manual mode : controlled by the user
KEY_ENGAGEMENT_ROBOT = "R"  # The robot actually enacts the interaction
KEY_ENGAGEMENT_IMAGINARY = "I"  # The application imagines the interaction but the robot does not enact them
KEY_DECREASE = "D"
KEY_INCREASE = "P"
KEY_CLEAR = "C"  # Clear the stack of interactions to enact next


class Workspace:
    """The Workspace supervises the interaction cycle. It produces the intended_interaction
    and processes the enacted interaction """
    def __init__(self, arena_id, robot_id):
        self.arena_id = arena_id
        self.robot_id = robot_id
        self.actions = create_actions(robot_id)
        self.memory = Memory(arena_id, robot_id)
        # if self.robot_id == '1':
        self.deciders = {'Explore': DeciderExplore(self), 'Circle': DeciderCircle(self), 'Watch': DeciderWatch(self)}
        # else:
        #     self.deciders = {'Explore': DeciderExplore(self), 'Circle': DeciderCircle(self)}
        #     # self.deciders = {'Circle': DeciderCircle(self)}
        self.integrator = Integrator(self)
        self.enacter = Enacter(self)

        self.enactions = {}  # The stack of enactions to enact next
        self.composite_enaction = None  # The composite enaction to enact
        self.enaction = None  # The primitive enaction to enact

        self.control_mode = KEY_CONTROL_USER
        self.engagement_mode = KEY_ENGAGEMENT_ROBOT
        # self.interaction_step = INTERACTION_STEP_IDLE

        # Controls which phenomenon to display
        self.ctrl_phenomenon_view = None

        # Control the enaction
        self.clock = 0
        # self.memory_snapshot = None
        self.is_imagining = False
        self.memory_before_imaginary = None

        # Message from other robot
        self.message = None

    def main(self, dt):
        """The main handler of the interaction cycle:
        organize the generation of the intended_interaction and the processing of the enacted_interaction."""
        # REFRESHING: last only one cycle
        if self.enacter.interaction_step == ENACTION_STEP_REFRESHING:
            self.enacter.interaction_step = ENACTION_STEP_IDLE

        # IDLE: Ready to choose the next intended interaction
        if self.enacter.interaction_step == ENACTION_STEP_IDLE:
            # Manage the memory snapshot
            if self.is_imagining:
                # If stop imagining then restore memory from the snapshot
                if self.engagement_mode == KEY_ENGAGEMENT_ROBOT:
                    self.memory = self.memory_before_imaginary
                    self.is_imagining = False
                    self.enacter.interaction_step = ENACTION_STEP_REFRESHING
            else:
                # If start imagining then take a new memory snapshot
                if self.engagement_mode == KEY_ENGAGEMENT_IMAGINARY:
                    self.memory_before_imaginary = self.memory.save()
                    self.is_imagining = True
            # Next automatic decision
            # if self.clock not in self.enactions:
            if self.composite_enaction is None:
                if self.control_mode == KEY_CONTROL_DECIDER:
                    # The most activated decider processes the previous enaction and chooses the next enaction
                    decider = max(self.deciders, key=lambda k: self.deciders[k].activation_level())
                    print("Decider:", decider)
                    self.deciders[decider].stack_enaction()
                # Case DECIDER_KEY_USER is handled by self.process_user_key()

        self.enacter.main(dt)

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() in [KEY_CONTROL_DECIDER, KEY_CONTROL_USER]:
            self.control_mode = user_key.upper()
        elif user_key.upper() in [KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY]:
            self.engagement_mode = user_key.upper()
        elif user_key.upper() in ACTIONS:
            # Only process actions when the robot is IDLE
            if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                # self.enactions[self.clock] = Enaction(self.actions[user_key.upper()], self.clock, self.memory)
                self.composite_enaction = Enaction(self.actions[user_key.upper()], self.clock, self.memory)
        elif user_key.upper() == "/":
            # If key ALIGN then turn and move forward to the prompt
            if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                # The first enaction: turn to the prompt
                e0 = Enaction(self.actions[ACTION_TURN], self.clock, self.memory)
                self.enactions[self.clock] = e0
                # Second enaction: move forward to the prompt
                # self.enactions[self.clock + 1] = Enaction(self.actions[ACTION_FORWARD], self.clock + 1, e1.post_memory)
                e1 = Enaction(self.actions[ACTION_FORWARD], self.clock + 1, e0.post_memory)
                self.composite_enaction = CompositeEnaction([e0, e1])
        elif user_key.upper() == "P" and self.memory.egocentric_memory.focus_point is not None:
            # If key PUSH and has focus then create the push sequence
            if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                # First enaction: turn to the prompt
                e0 = Enaction(self.actions[ACTION_TURN], self.clock, self.memory)
                self.enactions[self.clock] = e0
                # Second enaction: move forward to the prompt
                e1 = Enaction(self.actions[ACTION_FORWARD], self.clock + 1, e0.post_memory)
                self.enactions[self.clock + 1] = e1
                # Third enaction: turn to the prompt which is copied from the focus because it may be cleared
                e1.post_memory.egocentric_memory.prompt_point = e1.post_memory.egocentric_memory.focus_point.copy()
                e2 = Enaction(self.actions[ACTION_TURN], self.clock + 2, e1.post_memory)
                self.enactions[self.clock + 2] = e2
                # Fourth enaction: move forward to the new prompt
                e3 = Enaction(self.actions[ACTION_FORWARD], self.clock + 3, e2.post_memory)
                self.enactions[self.clock + 3] = e3
                self.composite_enaction = CompositeEnaction([e0, e1, e2, e3])
        elif user_key.upper() == KEY_CLEAR:
            # Clear the stack of enactions
            playsound('autocat/Assets/R3.wav', False)
            # self.enactions = {}
            self.composite_enaction = None

    def emit_message(self):
        """Return the message to answer to another robot"""

        # Only compute the message once for the current enaction
        if self.enaction is None or self.enaction.message_sent:
            return None

        message = {"robot": self.robot_id, "clock": self.clock, "azimuth": self.memory.body_memory.body_azimuth()}

        # If the terrain has been found then send the position relative to the terrain origin
        if TER in self.memory.phenomenon_memory.phenomena and self.memory.phenomenon_memory.phenomena[TER].confidence > TERRAIN_INITIAL_CONFIDENCE:
            point = self.memory.allocentric_memory.robot_point - self.memory.phenomenon_memory.phenomena[TER].point
            message['pos_x'] = round(point[0])
            message['pos_y'] = round(point[1])

        # If ongoing enaction wit focus and message not yet sent then add the enation information
        if self.enaction is not None and self.enaction.focus_point is not None:
            focus_point = self.memory.egocentric_to_polar_egocentric(self.enaction.focus_point)
            # The position of the focus
            message['focus_x'] = round(focus_point[0])
            message['focus_y'] = round(focus_point[1])
            # The destination position in polar-egocentric
            destination_point = quaternion.apply_to_vector(self.enaction.body_quaternion,
                                                           self.enaction.command.anticipated_translation)
            message['destination_x'] = round(destination_point[0])
            message['destination_y'] = round(destination_point[1])

        # Mark the message for this enaction sent
        self.enaction.message_sent = True
        # Send the message of there is position or focus
        if 'pos_x' in message or 'focus_x' in message:
            return json.dumps(message)
        else:
            return None

    def receive_message(self, message_string):
        """Store the latest message received from other robots in the Workspace. It will be used during INTEGRATING"""
        # If no message then keep the previous one
        if message_string is not None:
            self.message = Message(message_string)
            self.message.ego_quaternion = self.message.body_quaternion.cross(self.memory.body_memory.body_quaternion.inverse)
            # print("other angle", math.degrees(self.message.body_quaternion.angle * self.message.body_quaternion.axis[2]))
            # print("this angle", math.degrees(self.memory.body_memory.body_quaternion.angle * self.memory.body_memory.body_quaternion.axis[2]))
            # print("ego angle", math.degrees(self.message.ego_quaternion.angle * self.message.ego_quaternion.axis[2]))
            if self.message.ter_position is not None:
                # If position in terrain and the position of this robot knows the position of the terrain
                if TER in self.memory.phenomenon_memory.phenomena \
                        and self.memory.phenomenon_memory.phenomena[TER].confidence > TERRAIN_INITIAL_CONFIDENCE:
                    allo_point = self.message.ter_position + self.memory.phenomenon_memory.phenomena[TER].point
                    print("Robot", self.message.robot, "position:", allo_point)
                    self.message.ego_position = self.memory.allocentric_to_egocentric(allo_point)
                else:
                    # If cannot place the robot then flush the message
                    self.message = None
            else:
                # If only focus position was received then we assume this robot is in the other's focus
                # if self.message.polar_ego_position is not None:
                self.message.ego_position = self.memory.polar_egocentric_to_egocentric(self.message.polar_ego_position)
