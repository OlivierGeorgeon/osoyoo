/*
  Scan.h - library for controlling the scan interaction
  Created by Olivier Georgeon, June 1 2023
  released into the public domain
*/
#ifndef Scan_h
#define Scan_h

#include "../../Interaction.h"

class Scan : public Interaction
{
public:
  Scan(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action, int clock,
  bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
