/*
  Watch.h - library for controlling the circumvent interaction
  Created by Olivier Georgeon, June 28 2023
  released into the public domain
*/
#ifndef Watch_h
#define Watch_h

#include "../../Interaction.h"
#include "Scan.h"

class Watch : public Interaction
{
public:
  Watch(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void terminate() override;
private:
  Scan* _scan  = nullptr;
};

#endif
