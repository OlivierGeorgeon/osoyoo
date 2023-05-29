/*
  Forward.h - library for controlling the move forward interaction
  Created by Olivier Georgeon, mai 29 2023
  released into the public domain
*/
#ifndef Forward_h
#define Forward_h

#include "../../Interaction.h"

class Forward : public Interaction
{
public:
  Forward(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long& action_end_time, int& interaction_step, String& status, char& action, int& clock, unsigned long& duration1, unsigned long& action_start_time,
  bool& _is_focussed, int& _focus_x, int& _focus_y, int& focus_speed, int& shock_event);
  void step1();
private:
  bool& _is_focussed;
  int& _focus_x;
  int& _focus_y;
  int& _focus_speed;
  int& _shock_event;
};

#endif
