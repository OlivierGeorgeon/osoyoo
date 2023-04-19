import json
import math
import numpy as np
from pyrr import matrix44
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_ALIGN_ROBOT, ACTION_LEFTWARD, ACTION_RIGHTWARD, \
    ACTION_TURN_LEFT, ACTION_TURN_RIGHT
from .RobotDefine import DEFAULT_YAW, TURN_DURATION
from ..Utils import rotate_vector_z

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds
SIMULATION_TIME_RATIO = 1  # 0.5   # The simulation speed is slower than the real speed because ...
SIMULATION_STEP_OFF = 0
SIMULATION_STEP_ON = 1  # More step will be used to take wifi transmission time into account


class Enaction:
    def __init__(self, interaction, clock, focus_point, prompt_point):
        self.interaction = interaction
        self.clock = clock
        self.focus_point = None
        if focus_point is not None:
            self.focus_point = focus_point.copy()
        self.duration = None
        self.angle = None
        if prompt_point is not None:
            if self.interaction.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                self.duration = int(np.linalg.norm(prompt_point) /
                                    math.fabs(self.interaction.action.translation_speed[0]) * 1000)
            if self.interaction.action.action_code == ACTION_ALIGN_ROBOT:
                self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))
            if (self.interaction.action.action_code == ACTION_TURN_RIGHT) and prompt_point[1] < 0:
                self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))
            if (self.interaction.action.action_code == ACTION_TURN_LEFT) and prompt_point[1] > 0:
                self.angle = int(math.degrees(math.atan2(prompt_point[1], prompt_point[0])))

        self.simulation_duration = 0
        self.simulation_rotation_speed = 0
        self.simulation_step = 0
        self.simulation_time = 0.

    def serialize(self):
        """Return the serial representation to send to the robot"""
        serial = {'clock': self.clock, 'action': self.interaction.action.action_code}
        if self.duration is not None:
            serial['duration'] = self.duration
        if self.angle is not None:
            serial['angle'] = self.angle
        if self.focus_point is not None:
            serial['focus_x'] = int(self.focus_point[0])  # Convert to python int
            serial['focus_y'] = int(self.focus_point[1])
        if self.interaction.action.action_code == ACTION_FORWARD:
            serial['speed'] = int(self.interaction.action.translation_speed[0])
        if self.interaction.action.action_code == ACTION_BACKWARD:
            serial['speed'] = -int(self.interaction.action.translation_speed[0])
        if self.interaction.action.action_code == ACTION_LEFTWARD:
            serial['speed'] = int(self.interaction.action.translation_speed[1])
        if self.interaction.action.action_code == ACTION_RIGHTWARD:
            serial['speed'] = -int(self.interaction.action.translation_speed[1])
        return json.dumps(serial)

    def timeout(self):
        """Return the timeout of this enaction"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout

    def start_simulation(self):
        """Initialize the simulation of the intended interaction"""
        self.simulation_step = SIMULATION_STEP_ON
        # Compute the duration and the speed depending and the enaction
        self.simulation_duration = self.interaction.action.target_duration
        self.simulation_rotation_speed = self.interaction.action.rotation_speed_rad
        if self.duration is not None:
            self.simulation_duration = self.duration / 1000
        if self.angle is not None:
            self.simulation_duration = math.fabs(self.angle) * TURN_DURATION / DEFAULT_YAW
            if self.angle < 0 and self.interaction.action.action_code != ACTION_TURN_RIGHT:  # TODO fix turn right with prompt
                self.simulation_rotation_speed = -self.interaction.action.rotation_speed_rad
        self.simulation_duration *= SIMULATION_TIME_RATIO
        self.simulation_rotation_speed *= SIMULATION_TIME_RATIO

    def simulate(self, memory, dt):
        """Simulate the enaction in memory. Return True during the simulation, and False when it ends"""
        # Check the target time
        self.simulation_time += dt
        if self.simulation_time > self.simulation_duration:
            self.simulation_time = 0.
            self.simulation_step = SIMULATION_STEP_OFF
            return False

        # Simulate the displacement in egocentric memory
        translation_matrix = matrix44.create_from_translation(-self.interaction.action.translation_speed * dt *
                                                              SIMULATION_TIME_RATIO)
        rotation_matrix = matrix44.create_from_z_rotation(self.simulation_rotation_speed * dt)
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        for experience in memory.egocentric_memory.experiences.values():
            experience.displace(displacement_matrix)
        # Simulate the displacement of the focus and prompt
        if memory.egocentric_memory.focus_point is not None:
            memory.egocentric_memory.focus_point = matrix44.apply_to_vector(displacement_matrix,
                                                                            memory.egocentric_memory.focus_point)
        if memory.egocentric_memory.prompt_point is not None:
            memory.egocentric_memory.prompt_point = matrix44.apply_to_vector(displacement_matrix,
                                                                             memory.egocentric_memory.prompt_point)
        # Displacement in body memory
        memory.body_memory.body_direction_rad += self.simulation_rotation_speed * dt
        # Update allocentric memory
        memory.allocentric_memory.robot_point += rotate_vector_z(self.interaction.action.translation_speed * dt *
                                                                 SIMULATION_TIME_RATIO,
                                                                 memory.body_memory.body_direction_rad)
        memory.allocentric_memory.place_robot(memory.body_memory, self.clock)

        return True

    def body_label(self):
        """Return the label to display in the body view"""
        rotation_speed = "{:.2f}".format(math.degrees(self.interaction.action.rotation_speed_rad))
        label = "Speed x: " + str(int(self.interaction.action.translation_speed[0])) + "mm/s, y: " \
            + str(int(self.interaction.action.translation_speed[1])) + "mm/s, rotation:" + rotation_speed + "°/s"
        return label
