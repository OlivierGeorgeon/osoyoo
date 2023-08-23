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

class Interaction
{
public:
  Interaction(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  virtual void begin();
  virtual void ongoing();
  virtual void outcome(JSONVar & outcome_object);
  virtual void terminate();
  void send();
  int update();
protected:
  Floor& _FLO;
  Head& _HEA;
  Imu& _IMU;
  WifiCat& _WifiCat;
  unsigned long _action_end_time;
  String _status;
  char _action = 0;
  int _target_angle = 0;
  int _target_duration = 1000;
  int _target_focus_angle = 0;
  bool _is_focussed = false;
  int _focus_x = 0;
  int _focus_y = 0;
  float _focus_speed = 160.;  // Must be a float to multiply by the elapsed time
  int _clock = 0;
  int head_destination_angle = 0;
  unsigned long _duration1;
  unsigned long _action_start_time;
  int _step;
  int _caution = 0;
  int _span = 40;
};

#endif
