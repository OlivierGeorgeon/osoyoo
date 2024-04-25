/*
  Backward.h - library for controlling the move bakward interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"
#include "../../Interaction.h"
#include "../../Action_define.h"
#include "Backward.h"

Backward::Backward(
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Backward::begin()
{
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _FLO._OWM.goBack(SPEED);
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Backward::ongoing()
{
  if (_is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action) (speed is negative)
    _HEA.turnHead(_HEA.head_direction(_focus_x - _speed * (millis()- _action_start_time)/1000, _focus_y));

  // If impact then proceed to phase 2
  int impact = _IMU.get_impact_backward();
  if (impact > 0) // && !_FLO._is_enacting)
  {
    // Trigger head alignment
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }

  // Check if Floor Change Retreat
  if (_FLO._is_retreating)
  {
    _FLO.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no floor change, check whether duration has elapsed
  else if (_action_end_time < millis()) {
    if (_align > 0 && !_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }
}

void Backward::outcome(JSONVar & outcome_object)
{
  _IMU.outcome_backward(outcome_object);
}

int Backward::direction()
{
 return DIRECTION_BACK;
}