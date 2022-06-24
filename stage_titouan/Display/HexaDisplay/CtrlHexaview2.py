import pyglet
from . HexaView import HexaView
from ... Workspace import Workspace
from ... Memory.HexaMemory.HexaMemory import HexaMemory

class CtrlHexaview2:
    """Made to work with CtrlWorkspace"""

    def __init__(self, ctrl_workspace):
        self.ctrl_workspace = ctrl_workspace
        self.hexaview = HexaView(hexa_memory = self.ctrl_workspace.workspace.hexa_memory)
        self.refresh_count = 0
        self.mouse_x, self.mouse_y = None, None
        self.hexa_memory = ctrl_workspace.workspace.hexa_memory
        self.to_reset = []
        #Handlers
        def on_text_hemw(text):
                if text.upper() == "R" :
                    self.ctrl_workspace.reset()
                    self.refresh_count = 0
                    return                    
                elif ctrl_workspace.need_user_to_command_robot:
                    x = self.mouse_x
                    y= self.mouse_y
                    action = text
                    print("krrrrrrrrrrrrrr")
                    ctrl_workspace.interaction_to_enact = {"action": action}
                    if x is not None and y is not None:
                        ctrl_workspace.interaction_to_enact["x"] = x
                        ctrl_workspace.interaction_to_enact["y"] = y
                    ctrl_workspace.f_interaction_to_enact_ready = True

                    print("intended interaction : ",ctrl_workspace.interaction_to_enact)
                    self.mouse_x = None
                    self.mouse_y = None

                else:
                    message = "Waiting for previous outcome before sending new action" if ctrl_workspace.enact_step != 0 else "Waiting for user action"
                    print(message)

                
        self.hexaview.on_text = on_text_hemw


    def react_to_user_interaction(self):
        """blbablal"""
        self.hexaview.indecisive_cell_shape = []
        self.inde_cell_projection_done = False

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