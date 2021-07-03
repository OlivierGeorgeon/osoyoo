/*
  Imu_control.h - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  released into the public domain
*/
#ifndef Imu_control_h
#define Imu_control_h
#include "Arduino.h"
#include <Wire.h>
#include <MPU6050.h>

#define IMU_READ_PERIOD 50

class Imu_control
{
  public:
    Imu_control();
    setup();
    begin();
    update();
    float end();
    float _yaw;
  private:
    MPU6050 _mpu;
    unsigned long _next_imu_read_time;
};
#endif