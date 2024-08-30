/*
  Turn_angle.h - library for controlling the turn in spot interaction
  Turn the robot to the _target_angle
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Turn_h
#define Turn_h

#include "../../Interaction.h"

class Turn : public Interaction
{
public:
  Turn(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
private:
};

#endif
