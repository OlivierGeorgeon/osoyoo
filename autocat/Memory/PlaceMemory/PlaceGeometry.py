# The geometrical calculus used for Place Cells

import math
import numpy as np
import pandas as pd
import open3d as o3d
from . import MIN_PLACE_CELL_DISTANCE, ICP_DISTANCE_THRESHOLD, ANGULAR_RESOLUTION, MASK_ARRAY
from ...Robot import NO_ECHO_DISTANCE
from ...Utils import cartesian_to_polar


def transform_estimation_cue_to_cue(points1, points2, threshold=ICP_DISTANCE_THRESHOLD):
    """Return the transformation points1 minus points2 using o3d ICP algorithm"""
    # print("Cues 1", cues1)
    # print("Cues 2", cues2)
    # Create the o3d point clouds
    pcd1 = o3d.geometry.PointCloud()
    pcd2 = o3d.geometry.PointCloud()
    # Converting to integers seems to avoid rotation
    pcd1.points = o3d.utility.Vector3dVector(np.array(points1, dtype=int))
    pcd2.points = o3d.utility.Vector3dVector(np.array(points2, dtype=int))
    trans_init = np.eye(4)  # Initial transformation matrix (4x4 identity matrix)
    # Apply ICP
    reg_p2p = o3d.pipelines.registration.registration_icp(
        pcd1, pcd2, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
        # Add robust kernel (e.g., TukeyLoss)
        # , loss = o3d.pipelines.registration.TukeyLoss(k=0.2)
    )
    if len(reg_p2p.correspondence_set) == 0:
        print("ICP no match")
    else:
        print(np.asarray(reg_p2p.correspondence_set))
        mse = np.mean([np.linalg.norm(np.asarray(pcd1.points)[i] - np.asarray(pcd2.points)[j])**2
                       for i, j in np.asarray(reg_p2p.correspondence_set)])
        print(f"ICP standard distance: {math.sqrt(mse):.0f}, fitness: {reg_p2p.fitness:.2f}")
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


def point_to_polar_array(point):
    """Return an array representing the angular span of the cue at this point"""
    r, theta = cartesian_to_polar(point)
    return np.roll(MASK_ARRAY * r, round(math.degrees(theta)) // ANGULAR_RESOLUTION)


def resample_by_diff(polar_points, theta_span, r_tolerance=30):
    """Return the array of points where difference is greater that tolerance"""
    # Convert point array to a sorted pandas DataFrame
    polar_points = polar_points.copy()
    df = pd.DataFrame(polar_points, columns=['r', 'theta'])  # .sort_values(by='theta').reset_index(drop=True)

    # The mask for rows where r decreases or will increase next and is not zero
    diff_mask = ((df['r'].diff() < -r_tolerance) | (df['r'].diff() > r_tolerance).shift(-1, fill_value=False)) & \
                (df['r'] > 0)
    diff_points = df[diff_mask]

    # Create a grouping key for streaks of similar r values
    df['group'] = (df['r'].diff().abs() > r_tolerance).cumsum()
    # Theta 0 and 2pi belong to the same group
    # max_group = max(df['group'])
    max_group_mask = (df['group'] == max(df['group']))
    df.loc[max_group_mask, 'theta'] = df.loc[max_group_mask, 'theta'].apply(lambda x: x - 2 * math.pi)
    df.loc[max_group_mask, 'group'] = 0

    # Group by the grouping key and calculate the mean r and theta for each group
    grouped = df.groupby('group').agg({'r': 'mean', 'theta': ['mean', lambda x: x.max() - x.min()]}).reset_index(drop=True)
    grouped.columns = ['r', 'theta', 'span']
    large_group_points = grouped[(grouped['span'] >= theta_span) & (grouped['r'] > 0) & (grouped['r'] < NO_ECHO_DISTANCE)]
    # print("groups\n", grouped, f"theta_span {theta_span}")

    points_of_interest = pd.concat([diff_points, large_group_points[['r', 'theta']]], ignore_index=True)
    return points_of_interest.sort_values(by='theta').to_numpy()
