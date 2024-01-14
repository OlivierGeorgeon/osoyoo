import time
from pyglet.window import key, mouse
from .AllocentricView import AllocentricView
from ...Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ...Memory.PhenomenonMemory.PhenomenonMemory import ROBOT1
from ...Robot.CtrlRobot import ENACTION_STEP_REFRESHING, ENACTION_STEP_ENACTING
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ...Memory.AllocentricMemory.GridCell import CELL_UNKNOWN
from ...Memory.BodyMemory import point_to_echo_direction_distance


class CtrlAllocentricView:
    def __init__(self, workspace):
        """Control the allocentric view"""
        self.workspace = workspace
        self.view = AllocentricView(self.workspace)
        self.next_time_refresh = 0

        # Handlers
        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.view.on_text = on_text

        def on_mouse_press(x, y, button, modifiers):
            """Display the label of this cell"""
            click_point = self.view.mouse_coordinates_to_point(x, y)
            cell_x, cell_y = point_to_cell(click_point)
            cell = self.workspace.memory.allocentric_memory.grid[cell_x][cell_y]

            # Change cell status
            if button == mouse.RIGHT:
                # SHIFT clear the cell and all the prompts
                if modifiers & key.MOD_SHIFT:
                    self.delete_prompt()
                    # Clear the FLOOR status
                    self.workspace.memory.allocentric_memory.clear_cell(cell_x, cell_y, self.workspace.clock)
                # CTRL ALT: toggle COLOR FLOOR
                elif modifiers & key.MOD_CTRL and modifiers & key.MOD_ALT:
                    if cell.status[0] == EXPERIENCE_FLOOR and cell.color_index > 0:
                        cell.status[0] = CELL_UNKNOWN
                        cell.color_index = 0
                    else:
                        # Mark a green FLOOR cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_FLOOR,
                                                                                      self.workspace.clock, 4)
                # CTRL: Toggle FLOOR
                elif modifiers & key.MOD_CTRL:
                    if cell.status[0] == EXPERIENCE_FLOOR and cell.color_index == 0:
                        cell.status[0] = CELL_UNKNOWN
                    else:
                        # Mark a FLOOR cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_FLOOR,
                                                                                      self.workspace.clock, 0)
                # ALT: Toggle ECHO
                elif modifiers & key.MOD_ALT:
                    if cell.status[1] == EXPERIENCE_ALIGNED_ECHO:
                        cell.status[1] = CELL_UNKNOWN
                        cell.color_index = 0
                        # if (cell_x, cell_y) in self.workspace.memory.allocentric_memory.user_added_echos:
                        self.workspace.memory.allocentric_memory.user_added_echos.remove((cell_x, cell_y))
                    else:
                        # Mark an echo cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y,
                                                                                      EXPERIENCE_ALIGNED_ECHO,
                                                                                      self.workspace.clock, 0)
                        self.workspace.memory.allocentric_memory.user_added_echos.append((cell_x, cell_y))
                # No modifier: move the prompt
                else:
                    # Mark the prompt
                    self.workspace.memory.allocentric_memory.update_prompt(click_point, self.workspace.clock)
                    # Store the prompt in egocentric memory
                    ego_point = self.workspace.memory.allocentric_to_egocentric(click_point)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_point

                self.update_view()
            # if cell.phenomenon_id is not None:
                # print("Displaying Phenomenon", cell.phenomenon_id)
                # self.workspace.ctrl_phenomenon_view.phenomenon = \
                #     self.workspace.memory.phenomenon_memory.phenomena[cell.phenomenon_id]
                # ctrl_phenomenon_view = CtrlPhenomenonView(workspace)
                # ctrl_phenomenon_view.update_body_robot()
                # ctrl_phenomenon_view.update_points_of_interest(phenomenon)
            self.view.label_click.text = cell.label()

        self.view.on_mouse_press = on_mouse_press

        def on_key_press(symbol, modifiers):
            """ Deleting the prompt"""
            if symbol == key.DELETE:
                self.delete_prompt()

        self.view.on_key_press = on_key_press

    def delete_prompt(self):
        """Delete the prompt"""
        self.workspace.memory.egocentric_memory.prompt_point = None
        self.workspace.memory.allocentric_memory.update_prompt(None, self.workspace.clock)
        self.update_view()

    def update_view(self):
        """Update the allocentric view from the status in the allocentric grid cells"""
        for c in [c for line in self.workspace.memory.allocentric_memory.grid for c in line]:
            self.view.update_hexagon(c)
        # Update the other robot
        # if ROBOT1 in self.workspace.memory.phenomenon_memory.phenomena:
        #     self.view.update_robot_poi(self.workspace.memory.phenomenon_memory.phenomena[ROBOT1])

    def main(self, dt):
        """Refresh allocentric view"""
        # Refresh during the simulation very 250 millisecond
        # if self.workspace.enacter.interaction_step == ENACTION_STEP_ENACTING and time.time() > self.next_time_refresh:
        #     self.next_time_refresh = time.time() + 0.250
        #     self.update_view()
        # Refresh at the end of the interaction cycle
        if self.workspace.enacter.interaction_step in [ENACTION_STEP_ENACTING, ENACTION_STEP_REFRESHING]:
            self.update_view()
