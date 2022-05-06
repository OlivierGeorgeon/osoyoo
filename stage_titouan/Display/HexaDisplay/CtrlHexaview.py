import pyglet
from . HexaView import HexaView
from ... Workspace import Workspace
from ... Memory.HexaMemory.HexaMemory import HexaMemory


class CtrlHexaview:
    """ This class is used to control the model"""

    def __init__(self, model):
        self.model = model
        self.hexaview = HexaView(hexa_memory = self.model.hexa_memory)
        self.refresh_count = 0
        self.mouse_x, self.mouse_y = None, None
        
        #Handlers
        hemw = self.hexaview
        def on_text_hemw(text):
                if model.need_user_action and not model.f_user_action_ready and model.f_inde_cell_projected :
                    if text.upper() == "Y":
                        model.user_action = 'y',None
                        model.f_user_action_ready = True
                        self.react_to_user_interaction()
                    elif text.upper() == "N":
                        model.user_action = 'n',None
                        model.f_user_action_ready = True
                        self.react_to_user_interaction()
                elif not model.synthesizer.synthetizing_step == 1:
                        if model.enact_step == 0 and not model.need_user_action:
                            model.agent_action = text

                            model.action_angle = 0
                            model.intended_interaction = {"action" : text}
                            if self.mouse_x is not None and self.mouse_y is not None :
                                model.intended_interaction["x"] = self.mouse_x
                                model.intended_interaction["y"] = self.mouse_y
                            model.f_agent_action_ready = True

                            print("intended interaction : ",model.intended_interaction)
                            self.mouse_x = None
                            self.mouse_y = None

                        else:
                            message = "Waiting for previous outcome before sending new action" if model.enact_step != 0 else "Waiting for user action"
                            print(message)
        hemw.on_text = on_text_hemw

        def on_mouse_press_hemw(x, y, button, modifiers):
            """ Computing the position of the mouse click in the hexagrid  """
            # Compute the position relative to the center in mm
            if model.need_user_action:
                self.hexaview.mouse_press_x = int((x - self.hexaview.width/2)*self.hexaview.zoom_level*2)
                self.hexaview.mouse_press_y = int((y - self.hexaview.height/2)*self.hexaview.zoom_level*2)
                print(self.hexaview.mouse_press_x, self.hexaview.mouse_press_y)
                cell_x, cell_y = model.hexa_memory.convert_pos_in_cell(self.hexaview.mouse_press_x, self.hexaview.mouse_press_y)
                model.user_action = 'click',(cell_x,cell_y)
                model.f_user_action_ready = True
                self.react_to_user_interaction()
            else:
                self.mouse_x = int((x - hemw.width/2)*hemw.zoom_level*2)
                self.mouse_y = int((y - hemw.height/2)*hemw.zoom_level*2)
                # print(self.mouse_x, self.mouse_y)

        hemw.on_mouse_press = on_mouse_press_hemw

    def main(self,dt):
        """blalbla"""
        if self.model.f_reset_flag :
            self.hexaview.shapesList = []
            self.hexaview = HexaView()
        if self.refresh_count > 500 :
            self.refresh_count = 0
        if self.refresh_count == 0 :
            print("RESET BASE HEXAVIEW")
            self.hexaview.shapesList = []
            self.hexaview.extract_and_convert_interactions(self.model.hexa_memory)
            self.model.hexa_memory.cells_changed_recently = []
        model = self.model
        if model.need_user_action and not model.f_user_action_ready : #and not model.f_inde_cell_projected :
            self.hexaview.show_indecisive_cell(model.cell_inde_a_traiter)
            model.f_inde_cell_projected = True
        if len(model.hexa_memory.cells_changed_recently) > 0 :
           self.hexaview.extract_and_convert_recently_changed_cells(model.hexa_memory)
           model.hexa_memory.cells_changed_recently = []

        self.refresh_count +=1


    def react_to_user_interaction(self):
        """blbablal"""
        self.hexaview.indecisive_cell_shape = []
        self.model.f_inde_cell_projected = False


# Displaying Hexaview
# py -m stage_titouan.Display.HexaDisplay.CtrlHexaview
if __name__ == "__main__":
    workspace = Workspace()

    # Create the hexa grid
    workspace.hexa_memory = HexaMemory(width=30, height=100, cell_radius=50)
    workspace.hexa_memory.robot_angle = 30

    # Create the Controller
    controller = CtrlHexaview(workspace)
    controller.hexaview.extract_and_convert_interactions(workspace.hexa_memory)

    # workspace.need_user_action = True

    # Add points of interest

    pyglet.app.run()
