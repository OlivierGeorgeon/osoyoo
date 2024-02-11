from ..Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, \
    ENACTION_STEP_INTEGRATING, ENACTION_STEP_REFRESHING
from ..Memory.PhenomenonMemory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE
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
                self.memory_snapshot = self.workspace.memory.save()
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
            # If imagining then use the simulated outcome when the simulation is finished
            if self.workspace.is_imagining and not self.workspace.simulator.is_simulating:
                simulated_outcome = self.workspace.simulator.end()
                self.workspace.enaction.terminate(simulated_outcome)
                self.interaction_step = ENACTION_STEP_INTEGRATING
            # If not imagining then CtrlRobot will terminate the enaction and proceed to INTEGRATING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == ENACTION_STEP_INTEGRATING:
            # Restore the memory from the snapshot
            self.workspace.memory = self.memory_snapshot
            # Retrieve possible message from other robot
            if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                    self.workspace.message is not None:
                self.workspace.enaction.message = self.workspace.message
                print("Message", self.workspace.message.message_string)
            # Force terminate the simulation
            simulated_outcome = self.workspace.simulator.end()
            print("Simulated outcome", simulated_outcome)
            # Update memory
            self.workspace.memory.update_and_add_experiences(self.workspace.enaction)
            # Compute the outcome code
            self.workspace.enaction.outcome_code = outcome_code(self.workspace.memory, self.workspace.enaction)
            # Track the prediction errors
            self.workspace.prediction_error.log(self.workspace.enaction)
            # Increment the clock if the enacted interaction was properly received
            if self.workspace.enaction.clock >= self.workspace.memory.clock:  # don't increment if the robot is behind
                self.workspace.memory.clock += 1
            self.interaction_step = ENACTION_STEP_REFRESHING
            # If the composite enaction is over or aborted due to floor or impact
            if not self.workspace.composite_enaction.increment():  # or outcome.floor > 0 or outcome.impact > 0:
                self.workspace.composite_enaction = None

        # REFRESHING: Will be reset to IDLE in the next cycle
