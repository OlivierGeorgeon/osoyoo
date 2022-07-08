import pyglet
from . HexaView import HexaView
from ... Workspace import Workspace
from ... Memory.HexaMemory.HexaMemory import HexaMemory

class CtrlHexaviewTest:

    """Made to work with CtrlWorkspaceTest"""

    def __init__(self, ctrl_workspace):
        """blabla"""
        self.ctrl_workspace = ctrl_workspace
        self.hexaview = HexaView(hexa_memory = self.ctrl_workspace.workspace.hexa_memory)
        self.refresh_count = 0
        self.mouse_x, self.mouse_y = None, None
        self.hexa_memory = ctrl_workspace.workspace.hexa_memory
        self.to_reset = []

        #Handlers
        def on_text_hemw(text):
            """Handles user input"""
            #CAS PARTICULIERS
            if text.upper() == "R" :
                #TODO
                ""
            elif text.upper() == "A":
                #TODO
                ""
                self.ctrl_workspace.put_decider_to_auto()
            elif text.upper() == "M":
                #TODO
                ""
                self.ctrl_workspace.put_decider_to_manual()
            #CAS GENERAl
            else :
                action = {"action": text}
                self.ctrl_workspace.set_action(action)
        self.hexaview.on_text = on_text_hemw

    def main(self,dt):
        """blaqbla"""
        if self.refresh_count > 500 :
            self.refresh_count = 0
        if self.refresh_count == 0 :
            #print("RESET BASE HEXAVIEW")
            self.hexaview.shapesList = []
            self.hexaview.extract_and_convert_interactions(self.hexa_memory)
            self.hexa_memory.cells_changed_recently = []
        if len(self.hexa_memory.cells_changed_recently) > 0 :
           self.hexaview.extract_and_convert_recently_changed_cells(self.hexa_memory,self.to_reset,[])
           self.hexa_memory.cells_changed_recently = []
        self.refresh_count +=1