/*
  Turn_angle.cpp - library for controlling the move turn in spot to angle interaction
  Turn the robot to the _target_angle while keeping the head to the focus or to the_target_angle
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
#include "Turn.h"

Turn::Turn(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FLO, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Turn::begin()
{
  _action_end_time = millis() + 5000;
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  if (_target_angle < - TURN_SPOT_ENDING_ANGLE)
    _FLO._OWM.turnInSpotRight(TURN_SPEED);

  if (_target_angle > TURN_SPOT_ENDING_ANGLE)
    _FLO._OWM.turnInSpotLeft(TURN_SPEED);

  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Turn::ongoing()
{
  if (_is_focussed)
  {
    // Keep looking at the focus point
    float current_focus_direction = (_focus_angle - _IMU._yaw) * M_PI / 180.0;
    float current_head_direction = _HEA.head_direction(cos(current_focus_direction) * _focus_distance, sin(current_focus_direction) * _focus_distance);
    _HEA.turnHead(current_head_direction);
  }
  else
    _HEA.turnHead(_target_angle - _IMU._yaw); // Keep looking at destination

  // Check if Floor Change Retreat
  if (_FLO._is_retreating)
  {
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis()- _action_start_time;
    _action_end_time = _FLO._retreat_end_time + TURN_SPOT_ENDING_DELAY;
    _step = INTERACTION_TERMINATE;
  }
  // When reached the target angle or the max duration
  else if (((_target_angle > TURN_SPOT_ENDING_ANGLE) && (_IMU._yaw > _target_angle - TURN_SPOT_ENDING_ANGLE)) ||
  ((_target_angle < -TURN_SPOT_ENDING_ANGLE) && (_IMU._yaw < _target_angle + TURN_SPOT_ENDING_ANGLE)) ||
  (abs(_target_angle) <= TURN_SPOT_ENDING_ANGLE) ||
  (_action_end_time < millis()))
  {
    if (!_HEA._is_enacting_head_alignment)
        _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FLO._OWM.stopMotion();
    _action_end_time = millis() + TURN_SPOT_ENDING_DELAY;// give it time to immobilize before terminating interaction
    _step = INTERACTION_TERMINATE;
  }
}