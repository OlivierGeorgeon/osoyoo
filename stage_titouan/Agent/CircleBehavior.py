OUTCOME_LOST_FOCUS = 'L'
OUTCOME_FAR_FRONT = 'F'
OUTCOME_CLOSE_FRONT = 'C'
OUTCOME_LEFT = '4'
OUTCOME_RIGHT = '6'
OUTCOME_FAR_LEFT = '1'
OUTCOME_FAR_RIGHT = '3'

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'


class CircleBehavior:
    def __init__(self):
        self.clockwise = True
        self._action = '8'
        self.focus = False
        self.echo_xy = None

    def action(self, outcome):

        # If previous action was scanning then check if found focus
        if self._action == ACTION_SCAN:
            if outcome in [OUTCOME_LEFT, OUTCOME_FAR_LEFT]:
                # Found focus to the left
                print("Turn counterclockwise")
                self.focus = True
                self.clockwise = False
            if outcome in [OUTCOME_RIGHT, OUTCOME_FAR_RIGHT]:
                # Found focus to the right
                print("Turn clockwise")
                self.focus = True
                self.clockwise = True

        # if no focus then scan or turn
        if not self.focus:
            if self._action == ACTION_SCAN:
                if self.clockwise:
                    self._action = ACTION_TURN_RIGHT
                else:
                    self._action = ACTION_TURN_LEFT
            else:
                self._action = ACTION_SCAN

        else:
            if outcome in [OUTCOME_LEFT, OUTCOME_RIGHT]:
                if self.clockwise:
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

        # if the agent was focussed
        if self.focus:
            if 'focus' in enacted_interaction:
                # The focus has been kept
                self.focus = True
            else:
                # The focus has been lost
                self.focus = False
                outcome = OUTCOME_LOST_FOCUS

        print("Result:", outcome)
        return outcome

    def intended_interaction(self, _action):
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
