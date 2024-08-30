/*
  Backward.h - library for controlling the move backward interaction
  Created by Olivier Georgeon, mai 31 2023
  released into the public domain
*/
#ifndef Backward_h
#define Backward_h

#include "../../Interaction.h"

class Backward : public Interaction
{
public:
  Backward(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  // unsigned long action_end_time, char action, int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
  int direction() override;
private:
};

#endif
