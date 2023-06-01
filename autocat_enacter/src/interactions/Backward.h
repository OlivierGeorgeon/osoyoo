/*
  Backward.h - library for controlling the move backward interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Backward_h
#define Backward_h

#include "../../Interaction.h"

class Backward : public Interaction
{
public:
  // Forward(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long& action_end_time, int& interaction_step, String& status, char& action, int& clock, unsigned long& duration1, unsigned long& action_start_time,
  // bool& _is_focussed, int& _focus_x, int& _focus_y, int& focus_speed, int& shock_event);
  Backward(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action, int clock,
  bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
