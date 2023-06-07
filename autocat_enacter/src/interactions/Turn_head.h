/*
  Turn_head.h - library for controlling the turn head interaction
  Turn the head towards the focus point or the target angle and then align head to nearest echo
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Turn_head_h
#define Turn_head_h

#include "../../Interaction.h"

class Turn_head : public Interaction
{
public:
  Turn_head(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed, int target_angle);
  void begin() override;
  void ongoing() override;
private:
  int _target_angle;
};

#endif
