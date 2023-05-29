/*
  Interaction.h - library for controlling an interaction
  Created by Olivier Georgeon, mai 26 2023
  released into the public domain
*/
#ifndef Interaction_h
#define Interaction_h

class Interaction
{
  public:
  Interaction(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long& action_end_time, int& interaction_step, String& status, char& action, int& clock, unsigned long& duration1, unsigned long& action_start_time);
  void Step2();
  void Update();
  private:
  Color& _CLR;
  Floor& _FCR;
  Head& _HEA;
  Imu& _IMU;
  WifiCat& _WifiCat;
  unsigned long& _action_end_time;
  int& _interaction_step;

  String& _status;
  char& _action;
  int& _clock;
  unsigned long& _duration1;
  unsigned long& _action_start_time;
};

#endif
