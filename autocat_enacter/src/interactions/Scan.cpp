/*
  Scan.h - library for controlling the scan interaction
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
#include "Scan.h"

Scan::Scan(
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Scan::begin()
{
  _HEA.beginEchoScan();
  _action_end_time = millis() + 2000;
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Scan::ongoing()
{
  if (!_HEA._is_enacting_echo_scan)
  {
    if (!_HEA._is_enacting_head_alignment)
      _HEA.beginEchoAlignment();  // Force HEA
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
}