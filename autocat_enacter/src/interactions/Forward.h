/*
  Forward.h - library for controlling the move forward interaction
  Created by Olivier Georgeon, mai 29 2023
  released into the public domain
*/
#ifndef Forward_h
#define Forward_h

#include "../../Interaction.h"

class Forward : public Interaction
{
public:
  Forward(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
private:
};

#endif
