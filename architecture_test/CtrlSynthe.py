class CtrlSynthe():
    """Controller for the synthesizer"""


    def __init__(self,model):
        self.model = model

    def main(self,dt):
        """Blabla"""
        model = self.model
        synthe = model.synthesizer
        if model.f_memory_changed and model.f_hexmem_changed and synthe.synthetizing_step == 0 :
            print("synthe acting")
            synthe.act()
            model.f_memory_changed = False
            model.f_hexmem_changed = False
            print("synthe_step = ,",synthe.synthetizing_step)
        elif synthe.synthetizing_step == 1 :
            model.need_user_action = True
            
            if len(synthe.indecisive_cells) != 0 :
                model.cell_inde_a_traiter = model.synthesizer.indecisive_cells[-1]
                if model.f_user_action_ready :
                    model.f_user_action_ready = False
                    synthe.apply_user_action(model.user_action)
                    model.user_action = None
                    synthe.synthetize()

            if len(synthe.indecisive_cells) == 0 :
                synthe.synthetizing_step = 2
                model.need_user_action = False
                model.f_ready_for_hex_refresh = True

        if synthe.synthetizing_step == 2 :
            print("synthe et reset synthe step")
            synthe.synthetize()
            synthe.synthetizing_step = 0
            print ("synthe step : ",synthe.synthetizing_step)
            model.f_ready_for_next_loop = True

