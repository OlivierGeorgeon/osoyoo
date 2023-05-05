import time
from pyglet.window import key
from .AllocentricView import AllocentricView
from ...Robot.CtrlRobot import INTERACTION_STEP_REFRESHING, INTERACTION_STEP_ENACTING


class CtrlAllocentricView:
    def __init__(self, workspace):
        """Control the allocentric view"""
        self.workspace = workspace
        self.allocentric_view = AllocentricView(self.workspace)
        self.next_time_refresh = 0
        self.prompt_point = None

        # Handlers
        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.allocentric_view.on_text = on_text

        def on_mouse_press(x, y, button, modifiers):
            """Open a phenomenon view based on the phenomenon on this cell"""
            self.prompt_point = self.allocentric_view.mouse_coordinates_to_point(x, y)
            cell_x, cell_y = self.workspace.memory.allocentric_memory.convert_pos_in_cell(self.prompt_point[0], self.prompt_point[1])
            phenomenon = self.workspace.memory.allocentric_memory.grid[cell_x][cell_y].phenomenon
            if phenomenon is not None:
                print("Displaying Phenomenon", phenomenon)
                self.workspace.ctrl_phenomenon_view.phenomenon = phenomenon
                # ctrl_phenomenon_view = CtrlPhenomenonView(workspace)
                # ctrl_phenomenon_view.update_body_robot()
                # ctrl_phenomenon_view.update_points_of_interest(phenomenon)

        self.allocentric_view.on_mouse_press = on_mouse_press

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                self.workspace.memory.egocentric_memory.prompt_point = None
                self.workspace.memory.allocentric_memory.update_prompt(None)
                self.update_view()
            if symbol == key.INSERT:
                # Mark the prompt in allocentric view
                self.workspace.memory.allocentric_memory.update_prompt(self.prompt_point)
                self.update_view()
                # Store the prompt in egocentric memory
                ego_point = self.workspace.memory.allocentric_to_egocentric(self.prompt_point)
                self.workspace.memory.egocentric_memory.prompt_point = ego_point

        self.allocentric_view.on_key_press = on_key_press

    def update_view(self):
        """Update the allocentric view from the status in the allocentric grid cells"""
        for c in [c for line in self.workspace.memory.allocentric_memory.grid for c in line]:
            self.allocentric_view.update_hexagon(c)

    def main(self, dt):
        """Refresh allocentric view"""
        # Refresh during the simulation very 250 millisecond
        if self.workspace.interaction_step == INTERACTION_STEP_ENACTING and time.time() > self.next_time_refresh:
            self.next_time_refresh = time.time() + 0.250
            self.update_view()
        # Refresh at the end of the interaction cycle
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            self.update_view()
