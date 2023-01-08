from pyrr import matrix44
from .AllocentricView import AllocentricView
from ...Workspace import INTERACTION_STEP_REFRESHING
from ..PhenomenonDisplay.CtrlPhenomenonView import CtrlPhenomenonView


class CtrlAllocentricView:
    def __init__(self, workspace):
        """Control the allocentric view"""
        self.workspace = workspace
        self.allocentric_memory = workspace.memory.allocentric_memory
        self.allocentric_view = AllocentricView(self.workspace.memory)
        self.refresh_count = 0

        # Handlers
        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.allocentric_view.on_text = on_text

        def on_mouse_press(x, y, button, modifiers):
            """Open a phenomenon view based on the phenomenon on this cell"""
            cell_x, cell_y = self.allocentric_view.cell_from_screen_coordinate(x, y)
            phenomenon = self.allocentric_memory.grid[cell_x][cell_y].phenomenon
            if phenomenon is not None:
                print("Displaying Phenomenon", phenomenon)
                self.workspace.ctrl_phenomenon_view.phenomenon = phenomenon
                # self.workspace.flag_for_view_refresh = True
                # ctrl_phenomenon_view = CtrlPhenomenonView(workspace)
                # ctrl_phenomenon_view.update_body_robot()
                # ctrl_phenomenon_view.update_points_of_interest(phenomenon)

        self.allocentric_view.on_mouse_press = on_mouse_press

    def extract_and_convert_interactions(self):
        """Create the cells in the view from the status in the hexagonal grid"""
        for i in range(0, len(self.allocentric_view.memory.allocentric_memory.grid)):
            for j in range(0, len(self.allocentric_view.memory.allocentric_memory.grid[0])):
                self.allocentric_view.update_hexagon(i, j)
        self.add_focus_cell()

    def add_focus_cell(self):
        """Create a cell corresponding to the focus"""
        # Remove the previous focus cell
        self.allocentric_view.remove_focus_cell()
        # Recreate the focus cell if agent has focus
        if self.workspace.focus_xy is not None:
            displacement_matrix = matrix44.multiply(self.workspace.memory.body_memory.body_direction_matrix(),
                                                    self.allocentric_memory.body_position_matrix())
            v = matrix44.apply_to_vector(displacement_matrix,
                                         [self.workspace.focus_xy[0], self.workspace.focus_xy[1], 0])
            i, j = self.allocentric_memory.convert_pos_in_cell(v[0], v[1])
            self.allocentric_view.add_focus_cell(i, j)

    def main(self, dt):
        """Refresh allocentric view"""
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            self.extract_and_convert_interactions()
