# The geometrical calculus used for Place Cells

import math
import numpy as np
import pandas as pd
import open3d as o3d
import csv
import matplotlib.pyplot as plt
import threading
from pyrr import Quaternion
from . import MIN_PLACE_CELL_DISTANCE, ICP_DISTANCE_THRESHOLD, ANGULAR_RESOLUTION, MASK_ARRAY
from ...Robot import NO_ECHO_DISTANCE
from ...Utils import cartesian_to_polar
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_CENTRAL_ECHO
from ...Utils import quaternion_to_direction_rad


def transform_estimation_cue_to_cue(points1, points2, threshold=ICP_DISTANCE_THRESHOLD, translation_init=None):
    """Return the transformation from points1 to points2 using o3d ICP algorithm"""
    # Create the o3d point clouds
    pcd1 = o3d.geometry.PointCloud()
    pcd2 = o3d.geometry.PointCloud()
    # Converting to integers seems to avoid rotation
    pcd1.points = o3d.utility.Vector3dVector(np.array(points1, dtype=int))
    pcd2.points = o3d.utility.Vector3dVector(np.array(points2, dtype=int))
    trans_init = np.eye(4)  # Initial transformation matrix (4x4 identity matrix)
    if translation_init is not None:
        trans_init[0:3, 3] = translation_init

    # Apply ICP
    estimation_method = o3d.pipelines.registration.TransformationEstimationPointToPoint()
    # criteria = o3d.pipelines.registration.ICPConvergenceCriteria()
    reg_p2p = o3d.pipelines.registration.registration_icp(pcd1, pcd2, threshold, trans_init, estimation_method)
                                                          # criteria=criteria)
    # Return the resulting transformation
    return reg_p2p


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
    # If same group at 0 and 2pi
    if abs(df['r'].iloc[0] - df['r'].iloc[-1]) < r_tolerance:
        # Subtract 2pi to the last group and name it group 0 to wrap the last streak
        max_group_mask = (df['group'] == max(df['group']))
        df.loc[max_group_mask, 'theta'] = df.loc[max_group_mask, 'theta'].apply(lambda x: x - 2 * math.pi)
        df.loc[max_group_mask, 'group'] = 0

    # Group by the grouping key
    grouped = df.groupby('group')

    # Calculate the mean r, mean theta, and span for each group
    # result = grouped.agg({'r': 'mean', 'theta': ['mean', lambda x: x.max() - x.min()]})  # .reset_index(drop=True)
    result = grouped.agg(r=('r', 'mean'), theta=('theta', 'mean'), span=('theta', lambda x: x.max() - x.min()))
    # grouped.columns = ['r', 'theta', 'span']

    # The points
    large_group_points = result[(result['span'] >= theta_span) & (result['r'] > 0) & (result['r'] < NO_ECHO_DISTANCE)]
    # print("groups\n", grouped, f"theta_span {theta_span}")

    # Concatenate the diff points and the large group points
    points_of_interest = pd.concat([diff_points, large_group_points[['r', 'theta']]], ignore_index=True)

    return points_of_interest.sort_values(by='theta').to_numpy()


def unscanned_direction(polar_points):
    """Return the array of points where difference is greater that tolerance"""
    # Convert point array to a sorted pandas DataFrame
    polar_points = polar_points.copy()
    df = pd.DataFrame(polar_points, columns=['r', 'theta'])  # .sort_values(by='theta').reset_index(drop=True)

    # Create a grouping key for streaks of similar r values
    df['group'] = (df['r'].diff().abs() > 30).cumsum()

    # If same group at 0 and 2pi
    if abs(df['r'].iloc[0] - df['r'].iloc[-1]) < 30:
        # Subtract 2pi to the last group and name it group 0 to wrap the last streak
        max_group_mask = (df['group'] == max(df['group']))
        df.loc[max_group_mask, 'theta'] = df.loc[max_group_mask, 'theta'].apply(lambda x: x - 2 * math.pi)
        df.loc[max_group_mask, 'group'] = 0

    # Group by the grouping key
    grouped = df.groupby('group')

    # Calculate the mean r, mean theta, and span for each group
    result = grouped.agg(r=('r', 'mean'), theta=('theta', 'mean'), span=('theta', lambda x: x.max() - x.min()))
    # print(result)

    # Find the group for which r is zero
    matches = result.loc[result['r'] == 0, ['theta', 'span']]
    # Check if there are any matching rows and retrieve it
    if matches.empty:
        theta_unscanned, span_unscanned = None, None
    else:
        theta_unscanned, span_unscanned = matches.iloc[0]

    return theta_unscanned, span_unscanned


def open_direction(polar_points):
    """Return the array of points where difference is greater that tolerance"""
    # Convert point array to a sorted pandas DataFrame
    polar_points = polar_points.copy()
    df = pd.DataFrame(polar_points, columns=['r', 'theta'])  # .sort_values(by='theta').reset_index(drop=True)

    # Identify where 'value' is greater than the threshold
    greater_than_threshold = df['r'] > 500

    # Identify consecutive rows where the condition is true
    # consecutive_groups = (greater_than_threshold != greater_than_threshold.shift()).cumsum()

    df['group'] = (greater_than_threshold != greater_than_threshold.shift()).cumsum()
    # If same group at 0 and 2pi
    if df['r'].iloc[0] > 500 and df['r'].iloc[-1] > 500:
        # print("round group")
        # Subtract 2pi to the last group and name it group 0 to wrap the last streak
        max_group_mask = (df['group'] == max(df['group']))
        df.loc[max_group_mask, 'theta'] = df.loc[max_group_mask, 'theta'].apply(lambda x: x - 2 * math.pi)
        df.loc[max_group_mask, 'group'] = 1  # For some reason the first group is 1 and not 0
    # print("df\n", df)

    # Group by the consecutive groups and filter for those that meet the threshold condition
    grouped = df[greater_than_threshold].groupby('group')

    # Calculate the average theta and the span for each group
    # result = grouped['theta'].agg(theta=('mean'), span=(lambda x: x.max() - x.min()), size=('size'))
    result = grouped.agg(r=('r', 'mean'), theta=('theta', 'mean'), min_theta=('theta', 'min'),
                         max_theta=('theta', 'max'), span=('theta', lambda x: x.max() - x.min()))

    # Display the result
    # print(result)
    max_value_index = result['span'].idxmax()
    return tuple(result.loc[max_value_index, ['theta', 'min_theta', 'max_theta']])


def compare_all_place_cells(cell_id, place_cells):
    """Print a comparison of this place cell with all others"""
    if len(place_cells) < 2:
        return

    points1 = np.array([c.point() for c in place_cells[cell_id].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    comparisons = {}
    for k, p in place_cells.items():
        if k != cell_id and p.is_fully_observed():
            points2 = np.array([c.point() for c in place_cells[k].cues if c.type == EXPERIENCE_CENTRAL_ECHO])
            reg_p2p = transform_estimation_cue_to_cue(points1, points2)
            # print("Transformation\n", reg_p2p.transformation)
            translation = -reg_p2p.transformation[0:2, 3].astype(int)
            rotation_deg = round(math.degrees(
                quaternion_to_direction_rad(Quaternion.from_matrix(reg_p2p.transformation[:3, :3]))))
            print(f"Compare cell {cell_id} to cell {k}: "
                  f"translation: {tuple(translation)}, "
                  f"rotation: {rotation_deg:.0f}, "
                  f"fitness: {reg_p2p.fitness:.2f}, "
                  f"rmse: {reg_p2p.inlier_rmse:.0f}")  # Root mean square error (residual distance)
            # Save the plot
            plot_compare(points1, points2, reg_p2p, cell_id, k, place_cells[cell_id].last_visited_clock)
            # Save the comparison
            comparisons[k] = (translation[0], translation[1], rotation_deg,
                              round(reg_p2p.fitness, 2), round(reg_p2p.inlier_rmse))

    # Save the comparison file
    with open(f"log/01_compare_{cell_id}.csv", 'w', newline='') as file:
        csv.writer(file).writerow(["cell", "translate_x", "translate_y", "rotation", "fitness", "rmse"])
    with open(f"log/01_compare_{cell_id}.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        for k, v in comparisons.items():
            writer.writerow([k, *v])


def compare_place_cells(place_source, place_target, clock):
    """Compare two place cells based on central echoes"""
    points1 = np.array([c.point() for c in place_source.cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    points2 = np.array([c.point() for c in place_target.cues if c.type == EXPERIENCE_CENTRAL_ECHO])
    translation_init = place_source.point - place_target.point
    # print(f"Comparing Place {place_source.key} to Place {place_target.key} "
    #       f"with trans_init: {tuple(trans_init[0:2, 3].astype(int))}")
    reg_p2p = transform_estimation_cue_to_cue(points1, points2, 100, translation_init)
    translation = -reg_p2p.transformation[:3, 3].astype(int)
    rotation_deg = round(math.degrees(
        quaternion_to_direction_rad(Quaternion.from_matrix(reg_p2p.transformation[:3, :3]))))
    print(f"Compare cell {place_source.key} to cell {place_target.key}: "
          f"translation: {tuple(translation[:2])}, "
          f"rotation: {rotation_deg:.0f}, "
          f"fitness: {reg_p2p.fitness:.2f}, "
          f"rmse: {reg_p2p.inlier_rmse:.0f}")  # Root mean square error (residual distance)

    # Save the plot in an asynchronous thread
    thread = threading.Thread(target=plot_compare, args=(
        points1, points2, reg_p2p, place_source.key, place_target.key, clock))
    thread.start()

    # If less than three points match or rotation then cancel the translation
    if len(reg_p2p.correspondence_set) < 3 or rotation_deg > 10:
        translation = None
        print(f"Adjustment cancelled points: {reg_p2p.correspondence_set}, rotation: {rotation_deg:.0f}")
    return translation


def plot_compare(source_points, target_points, reg_p2p, k1, k2, clock):
    """Save a plot of the correspondence"""
    plt.figure()

    # Plot invisible points to scale the axes
    plt.axis('equal')
    plt.plot(1000, 1000, marker=' ')
    plt.plot(-1000, -1000, marker=' ')

    # Plot the robot at coordinates (0, 0)
    plt.scatter(0, 0, s=1000, color='darkSlateBlue')

    # Plot the robot translated by the transformation
    plt.scatter(reg_p2p.transformation[0, 3], reg_p2p.transformation[1, 3], s=1000, color='lightSteelBlue')

    # Plot the source points
    plt.scatter(source_points[:, 0], source_points[:, 1], c='sienna', label=f"Place {k1}")

    # Plot the segments from source points to target points
    for idx in np.asarray(reg_p2p.correspondence_set):
        i, j = idx
        plt.plot([source_points[i, 0], target_points[j, 0]],[source_points[i, 1], target_points[j, 1]], c='k')

    # Plot the transformed source points
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(np.array(source_points, dtype=int))
    pcd1.transform(reg_p2p.transformation)
    source_points_transformed = np.asarray(pcd1.points)
    plt.scatter(source_points_transformed[:, 0], source_points_transformed[:, 1], c='sienna', marker="^",
                label=f"{k1} moved to {k2}")

    # Plot the target points in light sienna in the forefront
    plt.scatter(target_points[:, 0], target_points[:, 1], c='#ffb366', label=f"Place {k2}")

    # Plot the axis and legends
    plt.legend()
    plt.xlabel('West - East')
    plt.ylabel('South - North')
    distance = np.linalg.norm(reg_p2p.transformation[:3, 3])
    plt.title(f"{k1} to {k2}. Dist: {distance:.0f}. Fitness: {reg_p2p.fitness:.2f}. RMSE: {reg_p2p.inlier_rmse:.0f}")

    # Save the plot
    try:
        plt.savefig(f"log/01_{clock}_compare_{k1}_{k2}.pdf")
    except PermissionError:
        print("Permission denied")
    plt.close()
