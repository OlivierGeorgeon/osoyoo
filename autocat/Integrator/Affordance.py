

class Affordance:
    """An affordance is an experience localized relative to a phenomenon"""
    def __init__(self, x, y, experience):
        self.x, self.y = x, y
        self.experience = experience

        # The position matrix is applied to the vertices of the point_of_interest to display
        # the point of interest at the position of the affordance in phenomenon view
        # self.position_matrix = position_matrix
