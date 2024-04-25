/*
  Forward.h - library for controlling the move forward interaction
  Created by Olivier Georgeon, mai 29 2023
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
#include "Forward.h"

Forward::Forward(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Forward::begin()
{
  // _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _FLO._OWM.goForward(SPEED);
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Forward::ongoing()
{
  if (_is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action)
    _HEA.turnHead(_HEA.head_direction(_focus_x - _speed * (millis()- _action_start_time)/1000, _focus_y));


  // If caution mode and obstacle then proceed to step 2
  // if (_caution > 0 && _HEA.get_ultrasonic_measure() < 200) // 200
  if (_caution > 0 && !digitalRead(TOUCH_PIN))
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force to look at the obstacle
    _status ="echo";
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }

  int impact = _IMU.get_impact_forward();
  // Floor Change Retreat then proceed to phase 2
  if (_FLO._is_retreating)
  {
    // Turn head to the line as if it attracted focus
    if (_FLO._floor_outcome == B01)
      _HEA.turnHead(-30);
    else if (_FLO._floor_outcome == B10)
      _HEA.turnHead(30);
    else
      _HEA.turnHead(0);
    _FLO.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis() - _action_start_time;
    _action_end_time = _FLO._retreat_end_time + TURN_SPOT_ENDING_DELAY;
    _step = INTERACTION_TERMINATE;
  }
  else if (impact > 0  && _caution >= 0)  // If caution is negative ignore impact
  {
    // If lateral impact, look at the direction of the impact
    if (impact == B01)
      _HEA.turnHead(-70);
    else if (impact == B10)
      _HEA.turnHead(70);
    // Trigger head alignment
    _HEA.beginEchoAlignment();
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }
  // If no floor change nor impact, check whether duration has elapsed
  else if (_action_end_time < millis())
  {
    if (_align > 0 && !_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FLO._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }
}

void Forward::outcome(JSONVar & outcome_object)
{
  _IMU.outcome_forward(outcome_object);
}
