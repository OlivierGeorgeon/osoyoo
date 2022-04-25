import pyglet
from pyglet.gl import *
from .. Misc.Utils import hexaMemory_to_pyglet
from .. Misc.Utils import translate_indecisive_cell_to_pyglet
from .. Model.Hexamemories import HexaMemory
from webcolors import name_to_rgb

NB_CELL_WIDTH = 30
NB_CELL_HEIGHT = 100
CELL_RADIUS = 50

ZOOM_IN_FACTOR = 1.2


class HexaView(pyglet.window.Window):
    """blabla"""
    def __init__(self, width=400, height=400, shapesList=None, cell_radius=20, hexa_memory = None, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Hexa Memory")
        self.set_minimum_size(150, 150)
        # glClearColor(0.2, 0.2, 0.7, 1.0)  # Make it look like hippocampus imaging
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 4
        self.azimuth = 0
        self.shapesList = shapesList
        # self.mouse_press_x = 0
        # self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.window = None

        self.nb_cell_x = 30
        self.nb_cell_y = 100
        self.cell_radius = cell_radius

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.label = pyglet.text.Label('0', font_name='Arial', font_size=200, x=0, y=-300, batch = self.batch)
        self.label.color = (0,0,0,255)

        self.need_user_action = False
        self.user_acted = False
        self.hexa_memory = hexa_memory

    def set_ShapesList(self,s):
        self.shapesList = s

    # def refresh(self,memory):
    #     @self.event
    #     def on_close():
    #         self.close()
    #         #@self.window.event
    #         #def on_key_press(key, mod):
    #         #    # ...do stuff on key press
    #     pyglet.clock.tick()
    #     self.clear()
    #     self.dispatch_events()
    #     self.extract_and_convert_phenomenons(memory)
    #     self.on_draw()
    #     # ...transform, update, create all objects that need to be rendered
    #     self.flip()

    def extract_and_convert_interactions(self, memory):
        self.shapesList = hexaMemory_to_pyglet(memory, self.batch)
        self.nb_cell_x = memory.width
        self.nb_cell_y = memory.height
        self.cell_radius = memory.cell_radius

    def show_indecisive_cell(self,indecisive_cell): #(indecisive_cell,hexaMemory,batch)
        self.indecisive_cell_shape = translate_indecisive_cell_to_pyglet(indecisive_cell,self.hexa_memory,self.batch)
    def on_draw(self):
        """ Drawing the window """
        glClear(GL_COLOR_BUFFER_BIT)

        # The transformations are stacked, and applied backward to the vertices
        glLoadIdentity()

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the translation to center the grid in the widow
        tx = -self.nb_cell_x * 30 * self.cell_radius / 20
        ty = -self.nb_cell_y * 8.66 * self.cell_radius / 20
        glTranslatef(tx, ty, 0)

        # Draw the grid
        self.batch.draw()

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        # Always display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        # if .4 < self.zoom_level * f < 5:  # Olivier
        self.zoom_level *= f

        # def set_batch(self, batch):
        #     self.batch = batch

    # def on_mouse_press(self, x, y, button, modifiers):
    #     """ Computing the position of the mouse click in the hexagrid  """
    #     # Compute the position relative to the center in mm
    #     self.mouse_press_x = int((x - self.width/2)*self.zoom_level*2)
    #     self.mouse_press_y = int((y - self.height/2)*self.zoom_level*2)
    #     print(self.mouse_press_x, self.mouse_press_y)


# Testing  HexaView by displaying HexaMemory
# Click on a cell to change its status
# py -m Views.HexaView
if __name__ == "__main__":
    hexaview = HexaView()

    # Create the hexa grid
    hexa_memory = HexaMemory(width=30, height=100, cell_radius=50)

    # Create the shapes to draw the cells
    hexaview.extract_and_convert_interactions(hexa_memory)

    @hexaview.event
    def on_mouse_press(x, y, button, modifiers):
        """ Computing the position of the mouse click in the hexagrid  """
        # Compute the position relative to the center in mm
        hexaview.mouse_press_x = int((x - hexaview.width/2)*hexaview.zoom_level*2)
        hexaview.mouse_press_y = int((y - hexaview.height/2)*hexaview.zoom_level*2)
        print(hexaview.mouse_press_x, hexaview.mouse_press_y)
        # Find the cell
        cell_x, cell_y = hexa_memory.convert_pos_in_cell(hexaview.mouse_press_x, hexaview.mouse_press_y)
        print("Cell: ", cell_x, cell_y)
        hexaview.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)
        hexa_memory.grid[cell_x][cell_y].status = "Free"
        # Refresh
        hexaview.extract_and_convert_interactions(hexa_memory)

    @hexaview.event
    def on_mouse_motion(x, y, dx, dy):
        mouse_x = int((x - hexaview.width/2)*hexaview.zoom_level*2)
        mouse_y = int((y - hexaview.height/2)*hexaview.zoom_level*2)
        # Find the cell
        cell_x, cell_y = hexa_memory.convert_pos_in_cell(mouse_x, mouse_y)
        print("Cell: ", cell_x, cell_y)
        hexaview.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)

    pyglet.app.run()
