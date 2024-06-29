# The geometrical calculus used for Place Cells

import numpy as np
import open3d as o3d
from . import MIN_PLACE_CELL_DISTANCE, ICP_DISTANCE_THRESHOLD
from ...Robot import NO_ECHO_DISTANCE


def transform_estimation_cue_to_cue(cues1, cues2):
    """Return the transformation cues1 minus cues2 using o3d ICP algorithm"""
    # print("Cues 1", cues1)
    # print("Cues 2", cues2)
    # Create the o3d point clouds
    pcd1 = o3d.geometry.PointCloud()
    pcd2 = o3d.geometry.PointCloud()
    # Converting to integers seems to avoid rotation
    pcd1.points = o3d.utility.Vector3dVector(np.array(cues1, dtype=int))
    pcd2.points = o3d.utility.Vector3dVector(np.array(cues2, dtype=int))
    # Define ICP criteria and parameters
    threshold = ICP_DISTANCE_THRESHOLD
    trans_init = np.eye(4)  # Initial transformation matrix (4x4 identity matrix)
    # Apply ICP
    reg_p2p = o3d.pipelines.registration.registration_icp(
        pcd1, pcd2, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
        # Add robust kernel (e.g., TukeyLoss)
        # , loss = o3d.pipelines.registration.TukeyLoss(k=0.2)
    )
    print(f"ICP fitness: {reg_p2p.fitness:.2f}")
    # Return the resulting transformation
    return reg_p2p.transformation


def nearby_place_cell(robot_point, place_cells):
    """Return the id of the place cell within place cell distance if any, otherwise 0"""
    pc_distance_id = {np.linalg.norm(pc.point - robot_point): key for key, pc in place_cells.items()}
    if len(pc_distance_id) > 0:
        min_distance = min(pc_distance_id.keys())
        if min_distance < MIN_PLACE_CELL_DISTANCE:
            return pc_distance_id[min_distance]
    return 0


def delta_echo_curves(polar1, cartesian1, polar2, cartesian2):
    """Return the cartesian position difference between points with same polar angle """
    # The points that have echoes in both curves
    # echo_points = np.logical_and(np.where(0 < polar1[:, 0]), np.where(0 < polar2[:, 0]))
    echo_points = np.where(np.logical_and(np.logical_and(polar1[:, 0] > 0, polar1[:, 0] < NO_ECHO_DISTANCE),
                                          np.logical_and(polar2[:, 0] > 0, polar2[:, 0] < NO_ECHO_DISTANCE)))
    print("Echo points", echo_points)
    print(cartesian1[:, :][echo_points])
    # The delta between the echo points
    deltas = cartesian2[:, :][echo_points] - cartesian1[:, :][echo_points]
    # The sum of the deltas
    return np.sum(deltas, axis=0)
