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
  // Forward(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long& action_end_time, int& interaction_step, String& status, char& action, int& clock, unsigned long& duration1, unsigned long& action_start_time,
  // bool& _is_focussed, int& _focus_x, int& _focus_y, int& focus_speed, int& shock_event);
  Scan(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action, int clock,
  bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
private:
};

#endif
