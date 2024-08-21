import math
from .InteractiveWindow import InteractiveWindow
from pyglet.window import key
from ..Memory.PlaceMemory.PlaceGeometry import compare_all_place_cells


class CtrlWindow:
    """The parent class of the controller of all the pyglet windows"""

    def __init__(self, workspace):
        self.view = InteractiveWindow()
        self.workspace = workspace

        def on_text(text):
            """Handle user keypress"""
            self.workspace.process_user_key(text)

        def on_mouse_motion(x, y, dx, dy):
            """Display the position in allocentric memory and the cell in the grid"""
            ego_point = self.view.window_to_ego_centric(x, y)
            self.display_mouse(ego_point)

        def on_key_press(symbol, modifiers):
            """handle single key press"""
            # F1: save the comparison of the current place cells with all others
            if symbol == key.F1:
                cell_id = self.workspace.memory.place_memory.current_cell_id
                print(f"Comparing cell {cell_id} to other fully observed cells")
                if cell_id > 0:
                    compare_all_place_cells(cell_id, self.workspace.memory.place_memory.place_cells)
            # F2: start a new subgraph
            if symbol == key.F2:
                self.workspace.memory.place_memory.graph_start_id = self.workspace.memory.place_memory.place_cell_id + 1
            # F3:

        # Add the event functions to the window
        self.view.push_handlers(on_text, on_mouse_motion, on_key_press)

    def display_mouse(self, ego_point):
        """Display the mouse information"""
        ego_angle = math.degrees(math.atan2(ego_point[1], ego_point[0]))
        self.view.label3.text = f"Ego: {tuple(ego_point[:2])}, {ego_angle:.0f}°"
