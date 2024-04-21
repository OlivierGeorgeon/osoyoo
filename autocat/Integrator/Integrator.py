from pyrr import Quaternion
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_AZIMUTH, EXPERIENCE_COMPASS, EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from autocat.Memory.PhenomenonMemory.Affordance import Affordance
from ..Display.AllocentricDisplay import DISPLAY_CONE

# PHENOMENON_DELTA = 300


def integrate(memory):
    """Create phenomena and update cells in allocentric memory"""

    # The new experiences generated during this step that indicate affordances
    new_experiences = [e for e in memory.egocentric_memory.experiences.values() if (e.clock >= memory.clock)
                       and e.type in [EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO]]
    # The new affordances
    new_affordances = []
    for e in new_experiences:
        # if e.type not in [EXPERIENCE_LOCAL_ECHO, EXPERIENCE_AZIMUTH, EXPERIENCE_COMPASS, EXPERIENCE_PLACE]:
        # The position of the affordance in allocentric memory
        affordance_point = memory.egocentric_to_allocentric(e.point()).astype("int")
        new_affordances.append(Affordance(affordance_point, e.type, e.clock, e.color_index,
                               e.absolute_quaternion(memory.body_memory.body_quaternion),
                               e.polar_sensor_point(memory.body_memory.body_quaternion)))
    # for a in new_affordances:
    #     print(a)

    # Mark the area covered by the echo in allocentric memory
    if DISPLAY_CONE:
        for a in [a for a in new_affordances if a.type in [EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO]]:
            memory.allocentric_memory.mark_echo_area(a)

    # Try to attach the new affordances to existing phenomena and remove these affordances
    new_affordances, position_correction = memory.phenomenon_memory.update_phenomena(new_affordances)

    # Adjust the robot's position in allocentric memory
    # print("Position correction due to phenomenon update", position_correction)
    memory.allocentric_memory.robot_point += position_correction
    # Create new hypothetical phenomena from remaining affordances
    memory.phenomenon_memory.create_phenomena(new_affordances)

    # Store the remaining new affordances in allocentric memory
    # self.allocentric_memory.affordances.extend(new_affordances) Not sure why
