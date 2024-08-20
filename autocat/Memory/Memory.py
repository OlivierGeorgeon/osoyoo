import numpy as np
from pyrr import quaternion
from . import GRID_WIDTH, GRID_HEIGHT, CELL_RADIUS
from .EgocentricMemory.EgocentricMemory import EgocentricMemory
from .AllocentricMemory.AllocentricMemory import AllocentricMemory
from .BodyMemory import BodyMemory
from .PhenomenonMemory.PhenomenonMemory import PhenomenonMemory
from .PhenomenonMemory import PHENOMENON_ENCLOSED_CONFIDENCE
from ..Integrator.Integrator import integrate
from ..Enaction.Predict import push_objects
from .PlaceMemory.PlaceMemory import PlaceMemory

NEAR_HOME = 300    # (mm) Max distance to consider near home
# ARRANGE_MIN_RADIUS = 100
# ARRANGE_MAX_RADIUS = 400


class Memory:
    """The Memory serves as the general container of the three memories:
        body memory, egocentric memory, and allocentric memory
    """

    def __init__(self, arena_id, robot_id):
        self.arena_id = arena_id
        self.robot_id = robot_id
        self.clock = 0
        self.body_memory = BodyMemory(robot_id)
        self.egocentric_memory = EgocentricMemory(robot_id)
        self.allocentric_memory = AllocentricMemory(GRID_WIDTH, GRID_HEIGHT, cell_radius=CELL_RADIUS)
        self.phenomenon_memory = PhenomenonMemory(arena_id)
        self.place_memory = PlaceMemory()

    def __str__(self):
        return "Memory Robot position (" + str(round(self.allocentric_memory.robot_point[0])) + "," +\
                                           str(round(self.allocentric_memory.robot_point[1])) + ")"

    def update(self, enaction):
        """ Process the enacted interaction to update the memory
        - Move the robot in body memory
        - Move the previous experiences in egocentric_memory
        - Add new experiences in egocentric_memory
        - Move the robot in allocentric_memory
        """
        self.egocentric_memory.focus_point = enaction.trajectory.focus_point
        self.egocentric_memory.prompt_point = enaction.trajectory.prompt_point
        # print("Trajectory prompt", enaction.trajectory.prompt_point)

        # Push objects before moving the robot
        push_objects(enaction.trajectory, self, enaction.outcome.floor)

        # Translate the robot before applying the yaw
        # print("Robot relative translation", enaction.translation)
        self.allocentric_memory.move(self.body_memory.body_quaternion, enaction.trajectory, enaction.clock)
        self.body_memory.update(enaction)

        # Compute the other robot's position relative to the current state of memory
        if enaction.message is not None:
            enaction.message.set_position_matrix(self)

        # Update egocentric memory
        self.egocentric_memory.update_and_add_experiences(enaction)

        # Call the integrator to create and update the phenomena
        integrate(self)

        # Create or update place cell
        self.place_memory.add_or_update_place_cell(self)
        # print(f"Adjust the robot's position to place cell by {tuple(position_correction[:2].astype(int))}")
        # self.allocentric_memory.robot_point += position_correction

        """Update allocentric memory on the basis of body, phenomenon, and egocentric memory"""
        # Mark the cells where is the robot
        self.allocentric_memory.place_robot(self.body_memory, self.clock)

        # Update the grid with affordances and place cells
        self.allocentric_memory.update_grid(self)

        # Update the focus in allocentric memory
        allo_focus = self.egocentric_to_allocentric(self.egocentric_memory.focus_point)
        self.allocentric_memory.update_focus(allo_focus, self.clock)

        # Update the prompt in allocentric memory
        allo_prompt = self.egocentric_to_allocentric(self.egocentric_memory.prompt_point)
        self.allocentric_memory.update_prompt(allo_prompt, self.clock)

    def egocentric_to_polar_egocentric(self, point):
        """Convert the position of a point from egocentric to polar-egocentric reference"""
        if point is None:
            return None
        return quaternion.apply_to_vector(self.body_memory.body_quaternion, point)

    def egocentric_to_allocentric(self, point):
        """Return the point in allocentric from the point in egocentric reference"""
        if point is None:
            return None
        # convert to polar-egocentric and then add the position in allocentric memory
        return self.egocentric_to_polar_egocentric(point) + self.allocentric_memory.robot_point

    def polar_egocentric_to_egocentric(self, point):
        """Convert from polar-egocentric to egocentric references"""
        if point is None:
            return None
        # Rotate the point by the opposite body direction using the inverse body quaternion
        return quaternion.apply_to_vector(self.body_memory.body_quaternion.inverse, point)

    def allocentric_to_egocentric(self, point):
        """Return the point in egocentric coordinates from the point in allocentric coordinates"""
        if point is None:
            return None
        return self.polar_egocentric_to_egocentric(point - self.allocentric_memory.robot_point)

    def terrain_centric_to_egocentric(self, point):
        """Return the point in egocentric coordinates from the point in terrain-centric coordinates"""
        if point is None:
            return None
        if self.phenomenon_memory.terrain_confidence() >= PHENOMENON_ENCLOSED_CONFIDENCE:
            return self.allocentric_to_egocentric(point + self.phenomenon_memory.terrain().point)
        return self.allocentric_to_egocentric(point)

    def egocentric_to_terrain_centric(self, point):
        """Return the point in terrain egocentric coordinates from the point in egocentric coordinates"""
        if point is None:
            return None
        if self.phenomenon_memory.terrain_confidence() >= PHENOMENON_ENCLOSED_CONFIDENCE:
            return self.egocentric_to_allocentric(point) - self.phenomenon_memory.terrain().point
        return self.egocentric_to_allocentric(point)

    def terrain_centric_to_allocentric(self, point):
        """Return the point in allocentric coordinates from the point in terrain_centric"""
        if point is None:
            return None
        elif self.phenomenon_memory.terrain_confidence() >= PHENOMENON_ENCLOSED_CONFIDENCE:
            return point + self.phenomenon_memory.terrain().point
        else:
            return point

    def terrain_centric_robot_point(self):
        """Return the position of the robot relative to the terrain point"""
        if self.phenomenon_memory.terrain_confidence() >= PHENOMENON_ENCLOSED_CONFIDENCE:
            return self.allocentric_memory.robot_point - self.phenomenon_memory.terrain().point
        else:
            return self.allocentric_memory.robot_point

    def adjust_robot_position(self):
        """Adjust the robot's position by the correction from place cell memory"""
        current_cell = self.place_memory.current_place_cell()
        # The position of the robot estimated from the current cell
        estimated_allo_robot_point = current_cell.place_centric_to_allocentric(self.place_memory.estimated_robot_point)
        # The robot position correction
        position_correction = estimated_allo_robot_point - self.allocentric_memory.robot_point
        robot_position_correction = position_correction * current_cell.position_confidence / 100
        print(f"Adjusting the robot's position to place cell {self.place_memory.current_cell_id} "
              f"by {tuple(robot_position_correction[:2].astype(int))}")
        # Move the robot by the position correction proportionally to the place cell confidence
        self.allocentric_memory.robot_point += robot_position_correction

        # Propagate the position error to all the place cells since last position correction
        # Proportionally to the complementary of the place cell position confidence
        position_correction *= (current_cell.position_confidence - 100) / 100
        last_position_clock = self.place_memory.place_cells[self.place_memory.current_cell_id].last_position_clock
        self.place_memory.place_cells[self.place_memory.current_cell_id].last_position_clock = self.clock
        # ps = {k: p for k, p in self.place_memory.place_cells.items() if p.last_visited_clock > last_position_clock}
        ps = [p for p in self.place_memory.place_cells.values() if p.last_visited_clock > last_position_clock]
        n = len(ps)
        if n > 0:
            i = 1
            # sorted_ps = dict(sorted(ps.items(), key=lambda x: x[1].last_visited_clock))
            sorted_ps = sorted(ps, key=lambda p: p.last_visited_clock)
            for p in sorted_ps:
                # The older the place cell, the smaller the position correction
                correction_coefficient = i / n
                i += 1
                ac = np.array(position_correction * correction_coefficient, dtype=int)
                p.point += ac
                print(f"Place {p.key} adjusted by: {tuple(ac[0:2].astype(int))} coef: {correction_coefficient:.2f}")

        # Move the cell by the position correction
        self.allocentric_memory.update_grid(self)

    def save(self):
        """Return a clone of memory for memory snapshot"""
        # start_time = time.time()
        saved_memory = Memory(self.phenomenon_memory.arena_id, self.robot_id)
        saved_memory.clock = self.clock
        # saved_memory.emotion_code = self.emotion_code
        # Clone body memory
        saved_memory.body_memory = self.body_memory.save()
        # Clone egocentric memory
        saved_memory.egocentric_memory = self.egocentric_memory.save()
        # Clone allocentric memory
        saved_memory.allocentric_memory = self.allocentric_memory.save()
        # Clone phenomenon memory
        saved_memory.phenomenon_memory = self.phenomenon_memory.save()
        # Clone place memory
        saved_memory.place_memory = self.place_memory.save()
        # print("Save memory duration:", time.time() - start_time, "seconds")

        return saved_memory

    def is_outside_terrain(self, ego_point):
        """Return True if ego_point is not None and there is a terrain and ego_point is outside"""
        allo_point = self.egocentric_to_allocentric(ego_point)
        return self.phenomenon_memory.is_outside_terrain(allo_point)

    def is_near_terrain_origin(self):
        """Return True if the robot is near the origin of the terrain"""
        terrain = self.phenomenon_memory.terrain()
        if terrain is not None:
            delta = terrain.relative_origin_point + terrain.point - self.allocentric_memory.robot_point
            return np.linalg.norm(delta) < NEAR_HOME
        else:
            return False
