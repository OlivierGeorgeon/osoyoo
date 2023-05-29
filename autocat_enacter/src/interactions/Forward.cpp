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
  unsigned long& action_end_time,
  int& interaction_step,
  String& status,
  char& action,
  int& clock,
  unsigned long& duration1,
  unsigned long& action_start_time,
  bool& is_focussed,
  int& focus_x,
  int& focus_y,
  int& focus_speed,
  int& shock_event
  ) :
  Interaction(CLR, FCR, HEA, IMU, WifiCat, action_end_time, interaction_step, status, action, clock, duration1, action_start_time),
  _is_focussed(is_focussed), _focus_x(focus_x), _focus_y(focus_y), _focus_speed(focus_speed), _shock_event(shock_event)
{
}

void Forward::step1()
{
  if (_is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action)
    _HEA.turnHead(_HEA.head_direction(_focus_x - _focus_speed * (millis()- _action_start_time)/1000, _focus_y));
  if (_shock_event > 0 && !_FCR._is_enacting)
  {
    // If shock then stop the go advance action
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _FCR._OWM.stopMotion();
    _interaction_step = 2;
    // break;
  }
  // Check if Floor Change Retreat
  else if (_FCR._is_enacting)
  {
    _FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
    _status ="1";
    // Proceed to step 2 for enacting Floor Change Retreat
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _interaction_step = 2;
  }
  // If no floor change, check whether duration has elapsed
  else if (_action_end_time < millis())
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _FCR._OWM.stopMotion();
    _interaction_step = 2;
  }
}