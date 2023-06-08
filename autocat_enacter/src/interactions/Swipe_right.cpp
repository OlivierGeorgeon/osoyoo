/*
  Swipe_right.cpp - library for controlling the move swipe right interaction
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
#include "Swipe_right.h"

Swipe_right::Swipe_right(
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
void Swipe_right::begin()
{
  _HEA._next_saccade_time = _action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
  _FCR._OWM.shiftRight(SHIFT_SPEED);
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Swipe_right::ongoing()
{
  // Keep the head towards the focus (HEA is inhibited during the action)
  if (_is_focussed)
    _HEA.turnHead(_HEA.head_direction(_focus_x, _focus_y + _focus_speed * (millis()- _action_start_time)/1000));

  // Check if Floor Change Retreat
  if (_FCR._is_enacting)
  {
    _FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no floor change, check whether duration has elapsed
  else if (_action_end_time < millis()) {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FCR._OWM.stopMotion();
    _step = INTERACTION_TERMINATE;
  }
}