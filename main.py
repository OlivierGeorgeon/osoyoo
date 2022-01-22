import pyglet
from Controller import Controller
from EgoMemoryWindow import EgoMemoryWindow
import json
import math


def main():
    view = EgoMemoryWindow()
    controller = Controller(view)

    @view.event
    def on_text(text):
        if controller.enact_step == 0:
            if text == "/":  # Turn of the angle marked by the mouse click
                angle = int(math.degrees(math.atan2(view.mouse_press_y, view.mouse_press_x)))
                text = json.dumps({'action': '/', 'angle': angle})
            controller.async_action_trigger(text)
        else:
            print("Waiting for previous outcome before sending new action")

    def watch_async_outcome(dt):
        if controller.enact_step == 2:
            print("Redraw window")
            controller.process_outcome(controller.action, controller.async_outcome_string)
            controller.enact_step = 0

    pyglet.clock.schedule_interval(watch_async_outcome, 0.1)
    pyglet.app.run()


main()
