/*
  Circumvent.h - library for controlling the circumvent interaction
  Created by Olivier Georgeon, June 28 2023
  released into the public domain
*/
#ifndef Circumvent_h
#define Circumvent_h

#include "../../Interaction.h"

class Circumvent : public Interaction
{
public:
  Circumvent(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
private:
};

#endif
