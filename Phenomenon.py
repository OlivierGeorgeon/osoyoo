from pyglet import shapes


class Phenomenon:
    def __init__(self, x, y, batch):
        self.batch = batch
        self.x = x
        self.y = y

        self.circle = shapes.Circle(self.x, self.y, 20, color=(50, 225, 30), batch=self.batch)
