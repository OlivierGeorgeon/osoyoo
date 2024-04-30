/*
Interaction.h - library for controlling an interaction
Created by Olivier Georgeon, mai 26 2023
released into the public domain
*/

#ifndef Interaction_h
#define Interaction_h

#include "Color.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "src/wifi/WifiCat.h"
#include "Action_define.h"

class Interaction
{
public:
  Interaction(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  virtual void begin();
  virtual void ongoing();
  virtual void outcome(JSONVar & outcome_object);
  virtual void terminate();
  virtual int direction();
  void send();
  int update();
protected:
  Floor& _FLO;
  Head& _HEA;
  Imu& _IMU;
  WifiCat& _WifiCat;
  unsigned long _action_end_time;
  String _status = "0";
  char _action = 0;
  int _target_angle = 0;
  int _target_duration = 1000;
  int _focus_angle = 0;
  float _focus_distance = 0;
  bool _is_focussed = false;
  int _focus_x = 0;
  int _focus_y = 0;
  float _speed = 160.;  // Must be a float to multiply by the elapsed time
  int _clock = 0;
  int head_destination_angle = 0;
  unsigned long _duration1;
  unsigned long _action_start_time;
  int _step = INTERACTION_BEGIN;
  int _caution = 0;
  int _span = 40;
  int _align = 0;
//  unsigned long _duration2 =0;  // Seems to create memory overflow
};

#endif
