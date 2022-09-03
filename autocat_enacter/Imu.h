/*
  Imu_control.h - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  released into the public domain
*/
#ifndef Imu_h
#define Imu_h
#include "Arduino.h"
#include "Robot_define.h"
#include <Wire.h>
#include "src/lib/MPU6050.h"
#if ROBOT_HAS_HMC5883L == true
  #include <HMC5883L.h>
#endif
#include <Arduino_JSON.h>

#define IMU_READ_PERIOD 50

class Imu
{
  public:
    Imu();
    void setup();
    void begin();
    int update(int interaction_step);
    void outcome(JSONVar & outcome_object, char action);
    float _yaw;
    float _xSpeed;
    float _xDistance;
    #if ROBOT_HAS_HMC5883L == true
      void read_azimuth(JSONVar & outcome_object);
    #endif
    //String _debug_message;
  private:
    MPU6050 _mpu;
    #if ROBOT_HAS_HMC5883L == true
      HMC5883L compass;
    #endif
    unsigned long _next_imu_read_time;
    int _max_acceleration;
    int _min_acceleration;
    float _max_speed;
    float _min_speed;
    int _shock_measure;
    bool _blocked;
    int _cycle_count;
};
#endif