import pyglet
from pyglet.window import key
from .. Views.PointOfInterest import *
from .. Views.EgocentricView import EgocentricView
from .. Model.Memories.MemoryV1 import MemoryV1


class EgoController:
    def __init__(self, ego_view: EgocentricView):
        self.ego_view = ego_view
        self.points_of_interest = []

        self.shape_list = []

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest"""
            self.mouse_press_x, self.mouse_press_y, self.mouse_press_angle = \
                self.ego_view.set_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.points_of_interest:
                if p.is_near(self.mouse_press_x, self.mouse_press_y):
                    p.set_color("red")
                else:
                    p.set_color()

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                for p in self.points_of_interest:
                    if p.is_selected:
                        p.delete()
                        self.points_of_interest.remove(p)
            if symbol == key.INSERT:
                print("insert phenomenon")
                phenomenon = PointOfInterest(self.mouse_press_x, self.mouse_press_y, self.ego_view.batch,
                                             self.ego_view.foreground, POINT_PHENOMENON)
                self.points_of_interest.append(phenomenon)

        self.ego_view.push_handlers(on_mouse_press, on_key_press)

    def add_point_of_interest(self, x, y, point_type):
        """ Adding a point of interest to the view """
        point_of_interest = PointOfInterest(x, y, self.ego_view.batch, self.ego_view.foreground, point_type)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    def rotate_head(self, head_angle):
        self.ego_view.robot.rotate_head(head_angle)

    def displace(self, displacement_matrix):
        """ Moving all the points of interest by the displacement matrix """
        for p in self.points_of_interest:
            p.displace(displacement_matrix)

    def extract_and_convert_interactions(self, memory):
        """ Retrieve the interactions from memory and create the points of interest """
        # self.points_of_interest = []
        for p in self.points_of_interest:
            if p.type == INTERACTION_ECHO or p.type == INTERACTION_TRESPASSING:
                self.points_of_interest.remove(p)
        for i in range(len(memory.interactions)):
            interaction = memory.interactions[i]
            poi = self.add_point_of_interest(0, 0, interaction.type)
            # Attach the interaction to this point of interest
            poi.reference = interaction
            # Move and rotate this point of interest by the interaction's position
            translation_matrix = matrix44.create_from_translation([interaction.x, interaction.y, 0])
            rotation_matrix = matrix44.create_from_z_rotation(math.radians(interaction.rotation))
            displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
            poi.displace(displacement_matrix)


# Displaying EgoMemoryWindowNew with phenomena in MemoryV1
# py -m stage_titouan.Controllers.EgoController
if __name__ == "__main__":
    view = EgocentricView()
    view.robot.rotate_head(-45)

    controller = EgoController(view)

    # Add interactions to memory
    mem = MemoryV1()
    mem.add((3, 0, 0, 0, 0, 0))  # Line
    mem.add((0, 0, 0, 1, 300, -200))  # Echo
    # Retrieve interactions from memory and construct the shapes in the window
    controller.extract_and_convert_interactions(mem)

    # Add points of interest
    controller.add_point_of_interest(150, 0, POINT_TRESPASS)
    controller.add_point_of_interest(300, -300, POINT_ECHO)

    pyglet.app.run()
