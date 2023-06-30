/*
  Turn_head.cpp - library for controlling the turn head interaction
  Turn the head towards the focus point or the target angle and then align head to nearest echo
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
#include "Turn_head.h"

Turn_head::Turn_head( Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
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