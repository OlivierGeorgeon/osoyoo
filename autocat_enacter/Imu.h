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
#include "src/lib/MPU6050.h"
#include <Arduino_JSON.h>
#include <Wire.h>
#if ROBOT_COMPASS_TYPE == 1
#include <HMC5883L.h>
#endif
#if ROBOT_COMPASS_TYPE == 2
#include "src/lib/MMC5883.h"
#endif

#define IMU_READ_PERIOD 50  // (ms)
#define IMU_ACCELERATION_CYCLES 5  // number of cycles of imu read during acceration phase

class Imu
{
  public:
    Imu();
    void setup();
    void begin();
    int update(int interaction_step);
    void outcome(JSONVar & outcome_object, char action);
    int get_impact_measure();
    float _yaw;
    float _xSpeed;
    float _xDistance;
    #if ROBOT_COMPASS_TYPE > 0
    void read_azimuth(JSONVar & outcome_object);
    #endif
    //String _debug_message;
  private:
    MPU6050 _mpu;
    #if ROBOT_COMPASS_TYPE == 1
    #warning "Compiling for HMC5883L"
    HMC5883L compass;
    #endif
    #if ROBOT_COMPASS_TYPE == 2
    #warning "Compiling for MMC5883"
    MMC5883MA compass;
    #endif
    unsigned long _next_imu_read_time;
    int _max_acceleration;
    int _min_acceleration;
    float _max_speed;
    float _min_speed;
    int _impact_measure;
    bool _blocked;
    int _cycle_count;
};
#endif