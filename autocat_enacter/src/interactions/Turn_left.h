/*
  Turn_left.h - library for controlling the turn in spot left interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Turn_left_h
#define Turn_left_h

#include "../../Interaction.h"

class Turn_left : public Interaction
{
public:
  Turn_left(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  // unsigned long action_end_time, char action, int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed, int _target_angle, int _target_focus_angle);
  void begin() override;
  void ongoing() override;
private:
  int _robot_destination_angle;
  int _target_angle;
  int _target_focus_angle;
};

#endif
