/*
  Imu_control.h - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  released into the public domain
*/
#ifndef Imu_control_h
#define Imu_control_h
#include "Arduino.h"
#include "Robot_define.h"
#include <Wire.h>
#include <MPU6050.h>
#if ROBOT_HAS_HMC5883L == true
  #include <HMC5883L.h>
#endif
#include <Arduino_JSON.h>

#define IMU_READ_PERIOD 50

class Imu_control
{
  public:
    Imu_control();
    void setup();
    void begin();
    void update();
    void outcome(JSONVar & outcome_object);
    float _yaw;
    float _xSpeed;
    float _xDistance;
    #if ROBOT_HAS_HMC5883L == true
      int read_azimuth();
    #endif
  private:
    MPU6050 _mpu;
    #if ROBOT_HAS_HMC5883L == true
      HMC5883L compass;
    #endif
    unsigned long _next_imu_read_time;
    float _max_acceleration;
    float _min_acceleration;
    float _max_speed;
    int _shock_measure;
    bool _blocked;
    int _cycle_count;
};
#endif