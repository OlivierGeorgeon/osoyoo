from .AllocentricView import AllocentricView
import math
from .Cell import Cell


class CtrlAllocentricView:
    def __init__(self, workspace):
        """Control the allocentric view"""
        self.workspace = workspace
        self.allocentric_memory = workspace.memory.allocentric_memory
        self.allocentric_view = AllocentricView(self.workspace.memory)
        self.refresh_count = 0
        # self.mouse_x, self.mouse_y = None, None
        self.to_reset = []
        # self.focus_x = None
        # self.focus_y = None

        # Handlers
        def on_text_hemw(text):
            """Handles user input"""
            # CAS PARTICULIERS
            if text.upper() == "R":
                # TODO
                ""
            elif text.upper() == "A":
                # TODO
                ""
                self.workspace.put_decider_to_auto()
            elif text.upper() == "M":
                # TODO
                ""
                self.workspace.put_decider_to_manual()
            # CAS GENERAl
            elif text.upper() == "T":
                self.workspace.egocentric_memory.allocentric_memory.apply_status_to_rectangle(-500, 600, 1000, 1000,
                                                                                              "Frontier")
            else:
                action = {"action": text}
                
                self.workspace.set_action(action)
        self.allocentric_view.on_text = on_text_hemw

        # def on_mouse_press(x, y, button, modifiers):
        #     """Handles mouse press"""
        #     self.mouse_x, self.mouse_y = x, y
        #     self.focus_x, self.focus_y = self.allocentric_memory.convert_allocentric_position_to_egocentric_translation(x, y)
        #
        # self.allocentric_view.on_mouse_press = on_mouse_press

    def extract_and_convert_interactions(self):
        """Create the cells in the view from the status in the hexagonal grid"""
        for i in range(0, len(self.allocentric_view.memory.allocentric_memory.grid)):
            for j in range(0, len(self.allocentric_view.memory.allocentric_memory.grid[0])):
                self.allocentric_view.add_cell(i, j)

    def extract_and_convert_recently_changed_cells(self, to_reset=[], projections=[]):
        cell_list = self.memory.allocentric_memory.cells_changed_recently + to_reset + projections
        for (i, j) in cell_list:
            self.allocentric_view.add_cell(i, j)

    def main(self, dt):
        """Refresh allocentric view"""
        if self.refresh_count > 500:
            self.refresh_count = 0
        if self.refresh_count == 0:
            # Display all cells on initialization
            self.allocentric_view.shapesList = []
            self.extract_and_convert_interactions()
            self.allocentric_memory.cells_changed_recently = []
        if len(self.allocentric_memory.cells_changed_recently) > 0:
            self.extract_and_convert_recently_changed_cells(self.to_reset, [])
            self.allocentric_memory.cells_changed_recently = []
        self.refresh_count += 1
