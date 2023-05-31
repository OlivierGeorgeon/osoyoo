/*
  Turn_angle.h - library for controlling the turn in spot to angle interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Turn_angle_h
#define Turn_angle_h

#include "../../Interaction.h"

class Turn_angle : public Interaction
{
public:
  Turn_angle(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed, int target_angle);
  void begin() override;
  void ongoing() override;
private:
  int _robot_destination_angle;
};

#endif
