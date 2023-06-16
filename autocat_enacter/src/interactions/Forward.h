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
  Forward(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  // unsigned long action_end_time, char action, int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
