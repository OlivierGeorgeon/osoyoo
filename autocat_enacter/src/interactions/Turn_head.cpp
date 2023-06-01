/*
  Turn_head.cpp - library for controlling the turn head interaction
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
#include "Turn_head.h"

Turn_head::Turn_head(
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
  int focus_speed,
  int target_angle
  ) :
  Interaction(CLR, FCR, HEA, IMU, WifiCat, action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed)
{
  _target_angle = target_angle;
}

// STEP 0: Start the interaction
void Turn_head::begin()
{
  if (_is_focussed)
    _HEA.turnHead(_HEA.head_direction(_focus_x, _focus_y));  // Look to the focussed phenomenon
  else
    _HEA.turnHead(_target_angle);  // look parallel to the direction

  _HEA.beginEchoAlignment();
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Turn_head::ongoing()
{
  if (!_HEA._is_enacting_head_alignment && !_HEA._is_enacting_echo_scan)
  {
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
}