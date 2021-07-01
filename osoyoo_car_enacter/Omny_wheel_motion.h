/*
  Omny_wheel_motion.h - library for Osoyoo car motion command.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Omny_wheel_motion_h
#define Omny_wheel_motion_h
#include "Arduino.h"

class Omny_wheel_motion
{
  public:
    Omny_wheel_motion();
    void setup();
    void goForward(int speed);
    void goBack(int speed);
    void turnInSpotRight(int speed);
    void turnInSpotLeft(int speed);
    void turnFrontRigh(int speed);
    void turnFrontLeft(int speed);
    void setMotion(int speed_fl, int speed_rl, int speed_rr, int speed_fr);
    void stopMotion();
  private:
    void frontLeftWheel(int speed_fl);
    void rearLeftWheel(int speed_rl);
    void frontRightWheel(int speed_fr);
    void rearRightWheel(int speed_rr);
};

#endif