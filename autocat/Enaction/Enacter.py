from ..Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, \
    ENACTION_STEP_INTEGRATING, ENACTION_STEP_REFRESHING
from ..Memory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE
from ..Integrator.OutcomeCode import outcome_code


class Enacter:
    def __init__(self, workspace):
        self.workspace = workspace
        self.interaction_step = ENACTION_STEP_IDLE
        self.memory_snapshot = None

    def main(self, dt):
        """Controls the enaction."""
        if self.interaction_step == ENACTION_STEP_IDLE:
            # When the next enaction is in the stack, prepare the enaction
            if self.workspace.composite_enaction is not None:
                # Take the current enaction from the composite interaction
                self.workspace.enaction = self.workspace.composite_enaction.current_enaction()
                # Take a memory snapshot to restore at the end of the enaction
                self.workspace.memory.emotion_code = self.workspace.enaction.predicted_memory.emotion_code
                self.memory_snapshot = self.workspace.memory.save()
                # Show the prompt in memory
                if self.workspace.enaction.trajectory.prompt_point is not None:
                    self.workspace.memory.egocentric_memory.prompt_point = self.workspace.enaction.trajectory.prompt_point.copy()
                    self.workspace.memory.allocentric_memory.update_prompt(self.workspace.memory.egocentric_to_allocentric(self.workspace.memory.egocentric_memory.prompt_point), self.workspace.memory.clock)
                # Begin the enaction
                self.workspace.enaction.begin(self.workspace.memory.body_memory.body_quaternion)
                # Begin the simulation
                self.workspace.simulator.begin()
                if self.workspace.is_imagining:
                    # If imagining then proceed to simulating the enaction
                    self.interaction_step = ENACTION_STEP_ENACTING
                else:
                    # If not imagining then proceed to COMMANDING to send the command to the robot
                    self.interaction_step = ENACTION_STEP_COMMANDING

        # COMMANDING: CtrlRobot sends the command to the robot and moves on to ENACTING

        # ENACTING: Simulate the enaction in memory
        if self.interaction_step == ENACTION_STEP_ENACTING:
            self.workspace.simulator.simulate(dt)
            # If imagining then check for the end of the simulation
            if self.workspace.is_imagining and not self.workspace.simulator.is_simulating:
                # simulated_outcome = self.workspace.simulator.end()
                # self.workspace.enaction.terminate(simulated_outcome)
                self.interaction_step = ENACTION_STEP_INTEGRATING
            # If not imagining then CtrlRobot will terminate the enaction and proceed to INTEGRATING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == ENACTION_STEP_INTEGRATING:
            # Terminate the simulation
            simulated_outcome = self.workspace.simulator.end()
            print("Simulated outcome", simulated_outcome)
            if self.workspace.is_imagining:
                self.workspace.enaction.outcome = simulated_outcome
            self.workspace.enaction.terminate()
            # Restore the memory from the snapshot
            serotonin = self.workspace.memory.body_memory.serotonin  # Handel user change  TODO improve
            dopamine = self.workspace.memory.body_memory.dopamine  # Handel user change
            noradrenaline = self.workspace.memory.body_memory.noradrenaline  # Handel user change
            self.workspace.memory = self.memory_snapshot
            self.workspace.memory.body_memory.serotonin = serotonin
            self.workspace.memory.body_memory.dopamine = dopamine
            self.workspace.memory.body_memory.noradrenaline = noradrenaline
            # Retrieve possible message from other robot
            if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                    self.workspace.message is not None:
                self.workspace.enaction.message = self.workspace.message
                print("Message", self.workspace.message.message_string)
            # Force terminate the simulation
            # simulated_outcome = self.workspace.simulator.end()
            # print("Simulated outcome", simulated_outcome)
            # Update memory
            self.workspace.memory.update(self.workspace.enaction)
            # Compute the outcome code
            self.workspace.enaction.outcome_code = outcome_code(self.workspace.memory,
                                                   self.workspace.enaction.trajectory, self.workspace.enaction.outcome)
            # Track the prediction errors
            self.workspace.prediction_error.log(self.workspace.enaction)
            # Calibrate what can be improved
            self.workspace.calibrator.calibrate()
            # Increment the clock if the enacted interaction was properly received
            if self.workspace.enaction.clock >= self.workspace.memory.clock:  # don't increment if the robot is behind
                self.workspace.memory.clock += 1
            self.interaction_step = ENACTION_STEP_REFRESHING
            # If the composite enaction is over or aborted due to floor or impact
            if not self.workspace.composite_enaction.increment():  # or outcome.floor > 0 or outcome.impact > 0:
                self.workspace.composite_enaction = None

        # REFRESHING: Will be reset to IDLE in the next cycle

    def decide(self):
        """Return the selected composite enaction"""
        proposed_enactions = []
        for name, proposer in self.workspace.proposers.items():
            activation = proposer.activation_level()  # Must compute before proposing
            # print("Computing proposition", name, "with focus", self.memory.egocentric_memory.focus_point)
            enaction = proposer.propose_enaction()
            if enaction is not None:
                proposed_enactions.append([name, enaction, activation])
        # The enaction that has the highest activation is selected
        print("Proposed enactions:")
        for p in proposed_enactions:
            print(" ", p[0], ":", p[1], p[2])
        most_activated = proposed_enactions.index(max(proposed_enactions, key=lambda p: p[2]))
        self.workspace.decider_id = proposed_enactions[most_activated][0]
        print("Decider:", self.workspace.decider_id)
        return proposed_enactions[most_activated][1]
