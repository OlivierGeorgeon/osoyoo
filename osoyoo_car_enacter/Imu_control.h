/*
  Imu_control.h - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  released into the public domain
*/
#ifndef Imu_control_h
#define Imu_control_h
#include "Arduino.h"
#include <Wire.h>
#include <MPU6050.h>

#define IMU_READ_PERIOD 100

class Imu_control
{
  public:
    Imu_control();
    setup();
    begin();
    update();
    end();
  private:
    MPU6050 _mpu;
    unsigned long _next_imu_read_time;
    float _yaw;
};
#endif