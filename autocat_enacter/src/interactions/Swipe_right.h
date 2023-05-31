/*
  Swipe_right.h - library for controlling the swipe right interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Swipe_right_h
#define Swipe_right_h

#include "../../Interaction.h"

class Swipe_right : public Interaction
{
public:
  Swipe_right(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
