/*
  Turn_right.cpp - library for controlling the move turn in spot right interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#include "../wifi/WifiCat.h"
#include "../../Action_define.h"
#include "../../Robot_define.h"
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"
#include "../../Interaction.h"
#include "Turn_right.h"

Turn_right::Turn_right(
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
  _robot_destination_angle = -TURN_SPOT_ANGLE;
}

// STEP 0: Start the interaction
void Turn_right::begin()
{
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _action_end_time = millis() + TURN_SPOT_MAX_DURATION;
  if (_target_angle < 0)   // Received negative angle overrides the default rotation angle
    _robot_destination_angle = _target_angle;

  _FCR._OWM.turnInSpotRight(TURN_SPEED);

  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Turn_right::ongoing()
{
  // Keep head aligned with destination angle
  if (_is_focussed)
  {
    // float current_robot_direction = (head_destination_angle - IMU._yaw) * M_PI / 180.0;
    float current_focus_direction = (_target_focus_angle - _IMU._yaw) * M_PI / 180.0;
    float r = sqrt(sq((float)_focus_x) + sq((float)_focus_y));  // conversion to float is necessary for some reason
    float current_head_direction = _HEA.head_direction(cos(current_focus_direction) * r, sin(current_focus_direction) * r);
    // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
    _HEA.turnHead(current_head_direction); // Keep looking at destination
  }
  else
    _HEA.turnHead(_robot_destination_angle - _IMU._yaw); // Keep looking at destination

  // Stop before reaching destination angle or when duration has elapsed
  if ((_IMU._yaw < _robot_destination_angle + TURN_SPOT_ENDING_ANGLE) || (_action_end_time < millis()))
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FCR._OWM.stopMotion();
    _action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
    _step = INTERACTION_TERMINATE;
  }
}