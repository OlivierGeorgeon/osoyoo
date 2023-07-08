/*
  Circumvent.cpp - library for controlling the circumvent interaction
  Created by Olivier Georgeon, June 28 2023
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
#include "Circumvent.h"

Circumvent::Circumvent(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FLO, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Circumvent::begin()
{
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _FLO._OWM.circumvent(SHIFT_SPEED);
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Circumvent::ongoing()
{
  // Keep the head towards the focus (HEA is inhibited during the action)
  if (_is_focussed)
    _HEA.turnHead(_HEA.head_direction(_focus_x, _focus_y + _focus_speed * (millis()- _action_start_time)/1000));

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
  else if ((_action_end_time < millis() )) // || _IMU.get_impact_rightwards() > 0)
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
    _action_end_time = 0;
  }
}

void Circumvent::outcome(JSONVar & outcome_object)
{
  _IMU.outcome_rightwards(outcome_object);
}