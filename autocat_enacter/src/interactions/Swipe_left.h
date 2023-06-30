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
  Swipe_left(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
private:
};

#endif
