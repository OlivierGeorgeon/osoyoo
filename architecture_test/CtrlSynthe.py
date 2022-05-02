class CtrlSynthe():
    """Controller for the synthesizer"""


    def __init__(self,model):
        self.model = model

    def main(self,dt):
        """Blabla"""
        model = self.model
        synthe = model.synthesizer
        if model.f_memory_changed and model.f_hexmem_changed and synthe.step == 0 :
            synthe.act()
            model.f_memory_changed = False
            model.f_hexmem_changed = False
        elif synthe.synthetizing_step == 1 :
            if len(synthe.indecisive_cells) != 0 :
                if model.f_user_action_ready :
                    model.f_user_action_ready = False
                    synthe.apply_user_action(model.user_action)
                    model.user_action = None
                    synthe.synthesize()

            if len(synthe.indecisive_cells) == 0 :
                synthe.synthetizing_step = 2
                model.need_user_action = False
                model.f_ready_for_hex_refresh = True

