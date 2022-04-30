# By Olivier GEORGEON 15 March 2022

import sys
import os
import json
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from stage_titouan import *

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

    robot_controller = RobotController(ip)

    ego_view = EgocentricView()
    ego_controller = EgoController(ego_view)

    memory = MemoryV1()
    hexa_memory = HexaMemory(width=40, height=80, cell_radius=50)
    agent_act = Agent5()
    agent = Agent6(memory, hexa_memory)
    hexaview = HexaView(cell_radius=hexa_memory.cell_radius)

    synthesizer = Synthesizer(memory,hexa_memory)
    controller = ControllerNew(agent, memory, ip, view=ego_view, synthesizer = synthesizer, hexa_memory = hexa_memory, hexaview = hexaview)
    controller.hexaview.extract_and_convert_interactions(controller.hexa_memory)

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
            if robot_controller.enact_step == 0:
                # controller.action_angle = emw.mouse_press_angle
                #  if text == "/" or text == "+":  # Send the angle marked by the mouse click
                #      text = json.dumps({'action': text, 'angle': emw.mouse_press_angle})
                robot_controller.command_robot(text)
            else:
                print("Waiting for previous outcome before sending new action")

    def main_loop(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if robot_controller.enact_step == 2:
            # Update the egocentric memory window
            phenom_info, angle, translation, controller.outcome, echo_array, head_angle, azimuth, status = robot_controller.translate_robot_data()
            if status != "T":
                controller.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
                controller.send_phenom_info_to_memory(phenom_info, echo_array) # when the robot detect interaction (before or after moving)
                controller.memory.tick()
                # ego_controller.extract_and_convert_interactions(memory)
                controller.hexaview.extract_and_convert_interactions(controller.hexa_memory)
                controller.azimuth = azimuth
                controller.send_position_change_to_hexa_memory(angle, translation)
                controller.ask_synthetizer_to_act()

                # Displace the points of interest
                translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
                rotation_matrix = matrix44.create_from_z_rotation(math.radians(angle))
                displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                ego_controller.displace(displacement_matrix)
                ego_controller.add_point_of_interest(0, 0, POINT_PLACE)
                ego_controller.rotate_head(head_angle)

                ego_controller.extract_and_convert_interactions(memory)
                ego_view.azimuth = azimuth  # TODO Use the EgoController
                controller.main_refresh()
            robot_controller.enact_step = 0

        if control_mode == CONTROL_MODE_AUTOMATIC:
            if robot_controller.enact_step == 0:
                # Retrieve the previous outcome
                outcome = 0
                json_outcome = json.loads(robot_controller.outcome_bytes)
                if 'floor' in json_outcome:
                    outcome = json_outcome['floor']
                if 'shock' in json_outcome:
                    if json_outcome['shock'] > 0:
                        outcome = json_outcome['shock']

                # Choose the next action
                action = agent_act.action(outcome)
                robot_controller.command_robot(['8', '1', '3'][action])

    # Schedule the main loop that updates the agent
    pyglet.clock.schedule_interval(main_loop, 0.1)

    # Run all the windows
    pyglet.app.run()
