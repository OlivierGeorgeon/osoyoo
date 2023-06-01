/*
  Turn_right.h - library for controlling the turn in spot right interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Turn_right_h
#define Turn_right_h

#include "../../Interaction.h"

class Turn_right : public Interaction
{
public:
  Turn_right(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed, int _target_angle, int _target_focus_angle);
  void begin() override;
  void ongoing() override;
private:
  int _robot_destination_angle;
  int _target_angle;
  int _target_focus_angle;
};

#endif
