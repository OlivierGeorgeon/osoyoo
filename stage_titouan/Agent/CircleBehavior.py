########################################################################################
# DEPRECATED. Hared coded circle behavior with focus
########################################################################################

from . PredefinedInteractions import *


class CircleBehavior:
    def __init__(self):
        self.counterclockwise = True  # Turn in trigonometric direction
        self._action = '8'
        self.focus = False
        self.echo_xy = None

    def action(self, outcome, focus_lost=False):
        """ Choose the action on the basis of the previous outcome """
        if focus_lost:
            self.focus = False

        # If previous action was scanning then check if found focus
        if self._action == ACTION_SCAN:
            if outcome in [OUTCOME_LEFT, OUTCOME_FAR_LEFT]:
                # Found focus to the left
                print("Turn clockwise")
                self.focus = True
                self.counterclockwise = False
            if outcome in [OUTCOME_RIGHT, OUTCOME_FAR_RIGHT]:
                # Found focus to the right
                print("Turn counterclockwise")
                self.focus = True
                self.counterclockwise = True

        # if no focus then scan or turn
        if not self.focus:
            if self._action == ACTION_SCAN:
                if self.counterclockwise:
                    self._action = ACTION_TURN_RIGHT
                else:
                    self._action = ACTION_TURN_LEFT
            else:
                self._action = ACTION_SCAN
        else:
            # If focus then choose an action depending on the position result
            if outcome in [OUTCOME_LEFT, OUTCOME_RIGHT]:
                # Keep turning in the same direction
                if self.counterclockwise:
                    self._action = ACTION_RIGHTWARD
                else:
                    self._action = ACTION_LEFTWARD
            if outcome == OUTCOME_FAR_FRONT:
                self._action = ACTION_FORWARD
            if outcome == OUTCOME_CLOSE_FRONT:
                self._action = ACTION_BACKWARD
            if outcome == OUTCOME_FAR_LEFT:
                self._action = ACTION_TURN_LEFT
            if outcome == OUTCOME_FAR_RIGHT:
                self._action = ACTION_TURN_RIGHT

        return self._action

    def result(self, enacted_interaction):
        """ Convert the enacted interaction into outcome adapted to the circle behavior """
        outcome = 'U'  # Outcome unknown

        # If there is an echo
        if 'echo_xy' in enacted_interaction:
            self.echo_xy = enacted_interaction['echo_xy']
            if self.echo_xy[0] < 10:
                outcome = OUTCOME_CLOSE_FRONT
            elif self.echo_xy[0] > 300:
                outcome = OUTCOME_FAR_FRONT
            elif self.echo_xy[1] > 150:
                outcome = OUTCOME_FAR_LEFT
            elif self.echo_xy[1] > 0:
                outcome = OUTCOME_LEFT
            elif self.echo_xy[1] > -150:
                outcome = OUTCOME_RIGHT
            else:
                outcome = OUTCOME_FAR_RIGHT

        # Check if the agent lost the focus
        if self.focus:
            if 'focus' not in enacted_interaction:
                # The focus was lost
                self.focus = False
                outcome = OUTCOME_LOST_FOCUS

        print("Result:", outcome)
        return outcome

    def intended_interaction(self, _action):
        """ Construct the intended interaction from the circle behavior action """
        intended_interaction = {'action': _action, 'speed': 180}
        if self.focus:
            intended_interaction['focus_x'] = self.echo_xy[0]
            intended_interaction['focus_y'] = self.echo_xy[1]

        return intended_interaction


# Testing AgentCircle
if __name__ == "__main__":
    a = CircleBehavior()
    _outcome = OUTCOME_LOST_FOCUS

    for i in range(20):
        _action = a.action(_outcome)
        print("Action: ", _action)
        _outcome = input("Enter outcome: ").upper()
        print(" Outcome: ", _outcome)
