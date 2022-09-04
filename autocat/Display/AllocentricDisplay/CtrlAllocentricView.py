import pyglet
from .AllocentricView import AllocentricView
from ...Memory import Memory
from ...Memory.HexaMemory.HexaMemory import HexaMemory


class CtrlAllocentricView:
    def __init__(self, workspace):
        """blabla"""
        self.workspace = workspace
        self.hexaview = AllocentricView(hexa_memory=self.workspace.memory.hexa_memory)
        self.refresh_count = 0
        self.mouse_x, self.mouse_y = None, None
        self.hexa_memory = workspace.memory.hexa_memory
        self.to_reset = []
        self.focus_x = None
        self.focus_y = None

        # Handlers
        def on_text_hemw(text):
            """Handles user input"""
            #CAS PARTICULIERS
            if text.upper() == "R":
                #TODO
                ""
            elif text.upper() == "A":
                #TODO
                ""
                self.workspace.put_decider_to_auto()
            elif text.upper() == "M":
                #TODO
                ""
                self.workspace.put_decider_to_manual()
            #CAS GENERAl
            elif text.upper() == "T":
                self.workspace.egocentric_memory.hexa_memory.apply_status_to_rectangle(-500, 600, 1000, 1000, "Frontier")
            else:
                action = {"action": text}
                
                self.workspace.set_action(action)
        self.hexaview.on_text = on_text_hemw

        def on_mouse_press(x, y, button, modifiers):
            """Handles mouse press"""
            self.mouse_x, self.mouse_y = x, y
            self.focus_x, self.focus_y = self.hexa_memory.convert_allocentric_position_to_egocentric_translation(x, y)

        self.hexaview.on_mouse_press = on_mouse_press

    def main(self, dt):
        """blaqbla"""
        if self.refresh_count > 500:
            self.refresh_count = 0
        if self.refresh_count == 0:
            #print("RESET BASE HEXAVIEW")
            self.hexaview.shapesList = []
            self.hexaview.extract_and_convert_interactions(self.hexa_memory)
            self.hexa_memory.cells_changed_recently = []
        if len(self.hexa_memory.cells_changed_recently) > 0:
            self.hexaview.extract_and_convert_recently_changed_cells(self.hexa_memory, self.to_reset, [])
            self.hexa_memory.cells_changed_recently = []
        self.refresh_count += 1
