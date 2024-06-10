import time
from .Workspace import Workspace
from .SoundPlayer import SoundPlayer, SOUND_STARTUP
from .Robot.CtrlRobot import CtrlRobot
from .Display.EgocentricDisplay.CtrlEgocentricView import CtrlEgocentricView
from .Display.AllocentricDisplay.CtrlAllocentricView import CtrlAllocentricView
from .Display.BodyDisplay.CtrlBodyView import CtrlBodyView
from .Display.PhenomenonDisplay.CtrlPhenomenonView import CtrlPhenomenonView
from .Display.PlaceCellDisplay.CtrlPlaceCellView import CtrlPlaceCellView


class Flock:
    """The Flock handles communication between robots"""
    def __init__(self, arguments):
        """Create the flock of robots"""
        # Try to load sounds (it may not work on all platforms)
        SoundPlayer.play(SOUND_STARTUP)

        self.workspaces = {}
        self.ctrl_robots = {}
        self.ctrl_egocentric_views = {}
        self.ctrl_allocentric_views = {}
        self.ctrl_body_views = {}
        self.ctrl_phenomenon_views = {}
        self.ctrl_place_cell_views = {}
        for i in range(2, len(arguments)):
            workspace = Workspace(arguments[1], arguments[i])
            self.workspaces[arguments[i]] = workspace
            self.ctrl_robots[arguments[i]] = CtrlRobot(workspace)
            self.ctrl_egocentric_views[arguments[i]] = CtrlEgocentricView(workspace)
            self.ctrl_egocentric_views[arguments[i]].view.set_caption("Egocentric " + arguments[i])
            self.ctrl_allocentric_views[arguments[i]] = CtrlAllocentricView(self.workspaces[arguments[i]])
            self.ctrl_allocentric_views[arguments[i]].view.set_caption("Allocentric " + arguments[i])
            self.ctrl_body_views[arguments[i]] = CtrlBodyView(self.workspaces[arguments[i]])
            self.ctrl_body_views[arguments[i]].view.set_caption("Robot " + arguments[i])
            self.ctrl_phenomenon_views[arguments[i]] = CtrlPhenomenonView(self.workspaces[arguments[i]])
            self.ctrl_phenomenon_views[arguments[i]].view.set_caption("Terrain " + arguments[i])
            self.workspaces[arguments[i]].ctrl_phenomenon_view = self.ctrl_phenomenon_views[arguments[i]]
            self.ctrl_place_cell_views[arguments[i]] = CtrlPlaceCellView(self.workspaces[arguments[i]])
            self.ctrl_place_cell_views[arguments[i]].view.set_caption("Place Cell Robot " + arguments[i])
            self.workspaces[arguments[i]].ctrl_place_cell_view = self.ctrl_place_cell_views[arguments[i]]

        # Create the views for the first robot
        # self.ctrl_phenomenon_view = CtrlPhenomenonView(self.workspaces[arguments[2]])
        # self.workspaces[arguments[2]].ctrl_phenomenon_view = self.ctrl_phenomenon_view

    def main(self, dt):
        """Update the robots"""
        start_time = time.time()
        for robot_id in self.workspaces.keys():
            self.ctrl_robots[robot_id].main(dt)
            self.workspaces[robot_id].main(dt)
            self.ctrl_egocentric_views[robot_id].main(dt)
            self.ctrl_allocentric_views[robot_id].main(dt)
            self.ctrl_body_views[robot_id].main(dt)
            self.ctrl_phenomenon_views[robot_id].main(dt)
            self.ctrl_place_cell_views[robot_id].main(dt)

        # Transmit messages between robots
        for key_sender in self.workspaces.keys():
            for key_receiver in self.workspaces.keys():
                if key_sender != key_receiver:
                    self.workspaces[key_receiver].receive_message(self.workspaces[key_sender].emit_message())
        main_loop_duration = time.time() - start_time
        if main_loop_duration > 0.1:
            print(f"Main loop duration: {main_loop_duration:.3f} seconds")

        # # Pass the message from robot '2' to robot '1'
        # if all(key in self.workspaces for key in ['1', '2']):
        #     self.workspaces['1'].receive_message(self.workspaces['2'].emit_message())
        # # Pass the message from robot '3' to robot '1'
        # if all(key in self.workspaces for key in ['3', '1']):
        #     self.workspaces['1'].receive_message(self.workspaces['3'].emit_message())
