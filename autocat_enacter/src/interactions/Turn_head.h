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
  Turn_head(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
private:
};

#endif
