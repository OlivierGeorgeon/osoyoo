/*
  Swipe_left.h - library for controlling the swipe left interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Swipe_left_h
#define Swipe_left_h

#include "../../Interaction.h"

class Swipe_left : public Interaction
{
public:
  Swipe_left(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
