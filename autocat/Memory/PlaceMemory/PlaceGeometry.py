# The geometrical calculus used for Place Cells

import math
import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
from . import MIN_PLACE_CELL_DISTANCE, ICP_DISTANCE_THRESHOLD, ANGULAR_RESOLUTION, MASK_ARRAY
from ...Robot import NO_ECHO_DISTANCE
from ...Utils import cartesian_to_polar
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_CENTRAL_ECHO


def transform_estimation_cue_to_cue(points1, points2, threshold=ICP_DISTANCE_THRESHOLD):
    """Return the transformation from points1 to points2 using o3d ICP algorithm"""
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
    # Compute the similarity
    correspondence_set = np.asarray(reg_p2p.correspondence_set)
    residual_distance = 0
    source_points_transformed = np.asarray(pcd1.points)
    if len(correspondence_set) == 0:
        print("ICP no match")
    else:
        # Print the correspondence
        for i, j in np.asarray(reg_p2p.correspondence_set):
            t = np.sqrt(np.linalg.norm(np.asarray(pcd1.points)[i] - np.asarray(pcd2.points)[j])**2)
            print(f"Match {np.asarray(pcd1.points)[i, 0:2]} - {np.asarray(pcd2.points)[j, 0:2]} = {t:.0f}")

        average_distance = np.mean([np.linalg.norm(np.asarray(pcd1.points)[i] - np.asarray(pcd2.points)[j])
                                    for i, j in correspondence_set])
        print(f"ICP average source-target distance: {average_distance:.0f}, fitness: {reg_p2p.fitness:.2f}")

        # Apply the transformation to the source cloud
        pcd1.transform(reg_p2p.transformation)
        source_points_transformed = np.asarray(pcd1.points)

        # Compute the distances between corresponding points
        target_points_corresponding = np.asarray(pcd2.points)[correspondence_set[:, 1]]

        distances = np.linalg.norm(
            source_points_transformed[correspondence_set[:, 0]] - target_points_corresponding, axis=1
        )

        # Compute Mean (not Squared Error MSE)
        residual_distance = np.mean(distances)

        # Compute the proportion of good correspondences
        good_correspondences_ratio = np.mean(distances < threshold)
        # print(f"ICP residual average distance: {mse:.0f}, nb close {good_correspondences_ratio}")

    # Return the resulting transformation
    return reg_p2p, residual_distance, source_points_transformed  # .transformation


def nearby_place_cell(robot_point, place_cells):
    """Return the id of the place cell within place cell distance if any, otherwise 0"""
    pc_distance_id = {np.linalg.norm(pc.point - robot_point): key for key, pc in place_cells.items()}
    if len(pc_distance_id) > 0:
        min_distance = min(pc_distance_id.keys())
        if min_distance < MIN_PLACE_CELL_DISTANCE:
            return pc_distance_id[min_distance]
    return 0


def nearest_place_cell(place_id, place_cells):
    """Return the id of the place cell closest to this place cell"""
    distances = {np.linalg.norm(pc.point - place_cells[place_id].point): k for k, pc in place_cells.items()
                 if k != place_id and pc.is_fully_observed()}
    if len(distances) > 0:
        min_distance = min(distances.keys())
        return distances[min_distance]
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
    grouped = df.groupby('group').agg(
        {'r': 'mean', 'theta': ['mean', lambda x: x.max() - x.min()]}
    ).reset_index(drop=True)
    grouped.columns = ['r', 'theta', 'span']
    large_group_points = grouped[(grouped['span'] >= theta_span) & (grouped['r'] > 0)
                                 & (grouped['r'] < NO_ECHO_DISTANCE)]
    # print("groups\n", grouped, f"theta_span {theta_span}")

    points_of_interest = pd.concat([diff_points, large_group_points[['r', 'theta']]], ignore_index=True)
    return points_of_interest.sort_values(by='theta').to_numpy()


def compare_place_cells(cell_id, place_cells):
    """Print a comparison of this place cell with all others"""
    if len(place_cells) < 2:
        return
    points1 = np.array([c.point() for c in place_cells[cell_id].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    for k, p in place_cells.items():
        if k != cell_id and p.is_fully_observed():
            points2 = np.array([c.point() for c in place_cells[k].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
            reg_p2p, residual_distance, points_transformed = transform_estimation_cue_to_cue(points1, points2)
            print("Transformation\n", reg_p2p.transformation)
            print(f"Compare cell {cell_id} to cell {k}: "
                  f"translation: {tuple(-reg_p2p.transformation[0:2, 3].astype(int))}, "
                  f"residual distance: {residual_distance:.0f}, fitness: {reg_p2p.fitness:.2f}")
            plot_correspondences(points1, points2, points_transformed, reg_p2p, residual_distance, cell_id, k)

    # keys = list(place_cells.keys())
    # for i in range(len(place_cells)):
    #     k1 = keys[i]
    #     if place_cells[k1].is_fully_observed():
    #         points1 = np.array([c.point() for c in place_cells[k1].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    #         np.savetxt(f"log/20_Cell_{k1}.txt", points1)
    #         for j in range(i + 1, len(place_cells)):
    #             k2 = keys[j]
    #             if place_cells[k2].is_fully_observed():
    #                 points2 = np.array([c.point() for c in place_cells[k2].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    #                 reg_p2p, residual_distance, points_transformed = transform_estimation_cue_to_cue(points1, points2)
    #                 print("Transformation\n", reg_p2p.transformation)
    #                 print(f"Compare cell {k1} to cell {k2}: "
    #                       f"translation: {tuple(-reg_p2p.transformation[0:2,3].astype(int))}, "
    #                       f"residual distance: {residual_distance:.0f}, fitness: {reg_p2p.fitness:.2f}")
    #                 plot_correspondences(points1, points2, points_transformed,
    #                                      np.asarray(reg_p2p.correspondence_set), k1, k2)


def plot_correspondences(source_points, target_points, source_points_transformed, reg_p2p, residual_distance, k1, k2):
    """Save a plot of the correspondence"""
    plt.figure()

    correspondence_set = np.asarray(reg_p2p.correspondence_set)

    # The robot at coordinates (0, 0)
    plt.scatter(0, 0, s=1000, color='darkSlateBlue')
    # The translated robot
    plt.scatter(reg_p2p.transformation[0, 3], reg_p2p.transformation[1, 3], s=1000, color='lightSteelBlue')

    # Plot source points
    plt.scatter(source_points[:, 0], source_points[:, 1], c='sienna', label=f"Place {k1}", marker="s")

    # Plot segments from source points to target points
    for idx in correspondence_set:
        i, j = idx
        plt.plot([source_points[i, 0], target_points[j, 0]],
                 [source_points[i, 1], target_points[j, 1]], c='k')

    # Plot target points in green first in the background
    plt.scatter(target_points[:, 0], target_points[:, 1], c='g', label=f"Place {k2}")

    # Plot transformed source points
    plt.scatter(source_points_transformed[:, 0], source_points_transformed[:, 1], c='sienna', marker="^",
                label=f"{k1} moved to {k2}")

    plt.legend()
    plt.xlabel('West-East')
    plt.ylabel('South-North')
    plt.title(f"{k1} to {k2}. Fitness: {reg_p2p.fitness:.2f}, residual distance: {residual_distance:.0f}")
    # plt.show()
    try:
        plt.savefig(f"log/20_match_{k1}_{k2}.pdf")
    except PermissionError:
        print("Permission denied")
    plt.close()
