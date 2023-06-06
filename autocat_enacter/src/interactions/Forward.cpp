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
#include "Forward.h"

Forward::Forward(
  Color& CLR,
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  unsigned long action_end_time,
  char action,
  int clock,
  bool is_focussed,
  int focus_x,
  int focus_y,
  int focus_speed
  ) :
  Interaction(CLR, FCR, HEA, IMU, WifiCat, action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed)
{
}

// STEP 0: Start the interaction
void Forward::begin()
{
  // _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _FCR._OWM.goForward(SPEED);
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Forward::ongoing()
{
  if (_is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action)
    _HEA.turnHead(_HEA.head_direction(_focus_x - _focus_speed * (millis()- _action_start_time)/1000, _focus_y));


  // If impact then proceed to phase 2
  if (_IMU.get_impact_measure() > 0 && !_FCR._is_enacting)
  {
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _FCR._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }

  // If obstacle the proceed to step 2
  if (_HEA.get_ultrasonic_measure() < 200)
  {
    _status ="2";
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _FCR._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }

  // Floor Change Retreat then proceed to phase 2
  if (_FCR._is_enacting)
  {
    _FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no floor change, check whether duration has elapsed
  else if (_action_end_time < millis())
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FCR._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }
}