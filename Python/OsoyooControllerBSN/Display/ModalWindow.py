import pyglet
from pyglet.gl import *
from ..Display.Phenomenon import Phenomenon


class ModalWindow(pyglet.window.Window):
    # draw a modalwindow
    # take the list of phenomena in parameter
    def __init__(self, phenomena):
        super(ModalWindow, self).__init__(width=450, height=100, resizable=True)

        self.label = pyglet.text.Label('Appuyer sur "O" pour confirmer la suppression', font_name='Times New Roman',
                                       font_size=15, x=20, y=50)
        self.label.anchor_position = 0, 0
        self.phenomena = phenomena

    def on_draw(self):
        """ Function for window drawing code in the on_draw event"""
        self.clear()
        self.label.draw()

    def on_text(self, text):
        # the on_text event called when this event is triggered
        # param : text
        print("Pressed :", text)
        if text.upper() == "O":
            for p in self.phenomena:
                p.delete()
            self.phenomena.clear()
            ModalWindow.close(self)
        else:
            ModalWindow.close(self)


# Testing the delete phenomena functionality
# python -m Python.OsoyooControllerBSN.Display.ModalWindow
if __name__ == "__main__":
    echo = Phenomenon(150, 0, None, 0)
    phenomena = [echo]
    mw = ModalWindow(phenomena)

    pyglet.app.run()