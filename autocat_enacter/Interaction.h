/*
  Interaction.h - library for controlling an interaction
  Created by Olivier Georgeon, mai 26 2023
  released into the public domain
*/
#ifndef Interaction_h
#define Interaction_h

#define INTERACTION_BEGIN 1
#define INTERACTION_ONGOING 2
#define INTERACTION_TERMINATE 3
#define INTERACTION_SEND 4
#define INTERACTION_DONE 0

class Interaction
{
public:
  // Interaction(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long& action_end_time, int& interaction_step, String& status, char& action, int& clock, unsigned long& duration1, unsigned long& action_start_time);
  Interaction(Color& CLR, Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, unsigned long action_end_time, char action,
  int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed);
  virtual void begin();
  virtual void ongoing();
  void terminate();
  void send();
  int update();
  int getStep();
protected:
  Color& _CLR;
  Floor& _FCR;
  Head& _HEA;
  Imu& _IMU;
  WifiCat& _WifiCat;
  unsigned long _action_end_time;
  String _status;
  char _action;
  int _clock;
  unsigned long _duration1;
  unsigned long _action_start_time;
  int _step;
  bool _is_focussed;
  int _focus_x;
  int _focus_y;
  int _focus_speed;
};

#endif
