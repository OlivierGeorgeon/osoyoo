import pyglet
from Controller import Controller
from EgoMemoryWindow import EgoMemoryWindow
import json
from Agent5 import Agent5


def main():
    emw = EgoMemoryWindow()
    controller = Controller(emw)
    agent = Agent5()

    def watch_agent_turn(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if controller.enact_step == 2:
            # Update the egocentric memory window
            controller.update_model()
            controller.enact_step = 0

        if controller.enact_step == 0:
            # Retrieve the previous outcome
            outcome = 0
            json_outcome = json.loads(controller.outcome_string)
            if 'floor' in json_outcome:
                outcome = json_outcome['floor']

            # Choose the next action
            action = agent.action(outcome)
            controller.enact(['8', '1', '3'][action])

    # Schedule the watch of the end of the previous interaction and choosing the next
    pyglet.clock.schedule_interval(watch_agent_turn, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()


main()
