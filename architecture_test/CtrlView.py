from stage_titouan import *
class CtrlView():
    """blabla"""

    def __init__(self,model):
        self.view = EgocentricView()
        self.model = model


    def main(self,dt):
        if self.model.f_new_things_in_memory :
            self.view.extract_and_convert_interactions(self.model.memory)
            self.model.f_new_things_in_memory = False