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
  Swipe_right(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
private:
};

#endif
