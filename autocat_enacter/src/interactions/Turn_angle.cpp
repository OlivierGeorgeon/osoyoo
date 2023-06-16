/*
  Turn_angle.cpp - library for controlling the move turn in spot to angle interaction
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
#include "Turn_angle.h"

Turn_angle::Turn_angle(
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
  // _robot_destination_angle = target_angle;
}

// STEP 0: Start the interaction
// Does not handle focus
void Turn_angle::begin()
{
  _action_end_time = millis() + 5000;
  _robot_destination_angle = _target_angle;
  Serial.println("Begin align robot angle : " + String(_robot_destination_angle));
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  if (_robot_destination_angle < - TURN_SPOT_ENDING_ANGLE)
    _FCR._OWM.turnInSpotRight(TURN_SPEED);

  if (_robot_destination_angle > TURN_SPOT_ENDING_ANGLE)
    _FCR._OWM.turnInSpotLeft(TURN_SPEED);

  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Turn_angle::ongoing()
{
  if (_is_focussed)
  {
    float current_robot_direction = (_robot_destination_angle - _IMU._yaw) * M_PI / 180.0;
    float r = sqrt(sq((float)_focus_x) + sq((float)_focus_y));  // conversion to float is necessary for some reason
    float current_head_direction = _HEA.head_direction(cos(current_robot_direction) * r, sin(current_robot_direction) * r);
    // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
    _HEA.turnHead(current_head_direction); // Keep looking at destination
  }
  else
    _HEA.turnHead(_robot_destination_angle - _IMU._yaw); // Keep looking at destination
  // If nearly turned to destination or duration elapsed
  if (((_robot_destination_angle > TURN_SPOT_ENDING_ANGLE) && (_IMU._yaw > _robot_destination_angle - TURN_SPOT_ENDING_ANGLE)) ||
  ((_robot_destination_angle < -TURN_SPOT_ENDING_ANGLE) && (_IMU._yaw < _robot_destination_angle + TURN_SPOT_ENDING_ANGLE)) ||
  (abs(_robot_destination_angle) <= TURN_SPOT_ENDING_ANGLE) ||
  (_action_end_time < millis()))
  {
    if (!_HEA._is_enacting_head_alignment)
        _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FCR._OWM.stopMotion();
    _action_end_time = millis() + TURN_SPOT_ENDING_DELAY;// give it time to immobilize before terminating interaction
    _step = INTERACTION_TERMINATE;
  }
}