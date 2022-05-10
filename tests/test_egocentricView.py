# By Olivier GEORGEON 15 March 2022

import sys
from stage_titouan import *
from stage_titouan.Agent.Agent5 import Agent5
from stage_titouan.Robot.RobotDefine import *

CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1
control_mode = CONTROL_MODE_MANUAL
print("Control mode: MANUAL")


# Testing ControllerNew by remote controlling the robot from the EgoMemoryWindowNew
# py -m tests.test_EgomemoryWindowNew <ROBOT_IP>
if __name__ == "__main__":
    ip = "192.168.1.11"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)

    workspace = Workspace()
    ctrl_robot = CtrlRobot(workspace, ip)
    ctrl_view = CtrlView(workspace)
    ego_view = ctrl_view.view
    agent = Agent5()
    ctrl_hexaview = CtrlHexaview(workspace)
    ctrl_hexaview.hexaview.extract_and_convert_interactions(workspace.hexa_memory)
    ctrl_synthe = CtrlSynthe(workspace)
    workspace.synthesizer.mode = 'automatic'

    @ego_view.event
    def on_text(text):
        global control_mode
        if text.upper() == "A":
            control_mode = CONTROL_MODE_AUTOMATIC
            print("Control mode: AUTOMATIC")
        elif text.upper() == "M":
            control_mode = CONTROL_MODE_MANUAL
            print("Control mode: MANUAL")

        if control_mode == CONTROL_MODE_MANUAL:
            if ctrl_robot.enact_step == 0:
                intended_interaction = {'action': text, 'angle': ctrl_view.mouse_press_angle}
                # workspace.intended_interaction = intended_interaction
                focus = ctrl_view.get_focus_phenomenon()
                if focus:
                    intended_interaction['focus_x'] = int(focus.x)
                    intended_interaction['focus_y'] = int(focus.y)
                    if text in ['8', '2']:
                        intended_interaction['speed'] = FORWARD_SPEED
                    if text in ['4', '6']:
                        intended_interaction['speed'] = LATERAL_SPEED
                ctrl_robot.command_robot(intended_interaction)
            else:
                print("Waiting for previous outcome before sending new action")

    def main_loop(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if ctrl_robot.enact_step == 2:
            # Update the egocentric memory window
            enacted_interaction = ctrl_robot.translate_robot_data()
            workspace.enacted_interaction = enacted_interaction
            ctrl_robot.enact_step = 0
            if enacted_interaction["status"] != "T":
                ctrl_view.update_model(enacted_interaction)
                ctrl_robot.send_position_change_to_memory()
                ctrl_robot.send_position_change_to_hexa_memory()
                ctrl_robot.send_phenom_info_to_memory()
                # ctrl_robot.main(0.1)
                # ctrl_view.main(0.1)

                workspace.synthesizer.act()  # prend les interactions qui n'ont pas été traitées dans memory
                    # treat_echo trouve l'echo centré dans l'echo array
                    # project_interactions_on_internal_hexagrid
                    # comparison_step prend la derniere interaction dans internal grid et crée hexagrid
                workspace.synthesizer.synthetize()  # c'est le moment ou on met à jour hexamemory

                #ctrl_hexaview.main(0.1)
                if len(workspace.hexa_memory.cells_changed_recently) > 0:
                    ctrl_hexaview.hexaview.extract_and_convert_recently_changed_cells(workspace.hexa_memory)
                    workspace.hexa_memory.cells_changed_recently = []

                # ctrl_synthe.main(0.1)
                # ctrl_hexaview.extract_and_convert_interactions(workspace.hexa_memory)
            ctrl_robot.enact_step = 0

        if control_mode == CONTROL_MODE_AUTOMATIC:
            if ctrl_robot.enact_step == 0:
                # Construct the outcome expected by Agent5
                enacted_interaction = ctrl_robot.translate_robot_data()
                outcome = 0
                if 'floor' in enacted_interaction:
                    outcome = int(enacted_interaction['floor'])
                if 'shock' in enacted_interaction:
                    if enacted_interaction['shock'] > 0:
                        outcome = enacted_interaction['shock']

                # Choose the next action
                action = agent.action(outcome)
                intended_interaction = {'action': ['8', '1', '3'][action]}
                ctrl_robot.command_robot(intended_interaction)

    # Schedule the main loop that updates the agent
    pyglet.clock.schedule_interval(main_loop, 0.1)

    # Run all the windows
    pyglet.app.run()
