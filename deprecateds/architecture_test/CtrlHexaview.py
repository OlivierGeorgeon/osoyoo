from stage_titouan import *
class CtrlHexaview :
    """ This class is used to control the model"""

    def __init__(self,model):
        self.model = model
        self.hexaview = HexaView(hexa_memory = self.model.hexa_memory)
        self.refresh_count = 0
        
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
                            model.f_agent_action_ready = True
                            model.action_angle = 0

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
        hemw.on_mouse_press = on_mouse_press_hemw
        @hemw.event
        def on_mouse_motion(x, y, dx, dy):
            mouse_x = int((x - hemw.width/2)*hemw.zoom_level*2)
            mouse_y = int((y - hemw.height/2)*hemw.zoom_level*2)
            # Find the cell
            cell_x, cell_y = model.hexa_memory.convert_pos_in_cell(mouse_x, mouse_y)
            hemw.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)
    
    def main(self,dt):
        """blalbla"""
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