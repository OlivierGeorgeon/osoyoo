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
// #include <HMC5883L.h>
#include "src/lib/HMC5883L.h"
#endif
#if ROBOT_COMPASS_TYPE == 2
#include "src/lib/MMC5883.h"
#endif

#define IMU_READ_PERIOD 10 // 25  // 50 (ms)
#define IMU_ACCELERATION_CYCLES 10  // 5  // number of cycles of imu read during acceleration phase

class Imu
{
  public:
    Imu();
    void setup();
    void begin();
    void update(int interaction_step);
    void outcome(JSONVar & outcome_object);
    void outcome_forward(JSONVar & outcome_object);
    void outcome_backward(JSONVar & outcome_object);
    void outcome_leftwards(JSONVar & outcome_object);
    void outcome_rightwards(JSONVar & outcome_object);
    int get_impact_forward();
    int get_impact_backward();
    int get_impact_leftwards();
    int get_impact_rightwards();
    float _yaw = 0;
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
    unsigned long _imu_read_time = 0;
    int _max_positive_x_acc;
    int _min_negative_x_acc;
    int _max_positive_y_acc;
    int _min_negative_y_acc;
    float _max_speed;
    float _min_speed;
    int _impact_forward;
    int _impact_backward;
    int _impact_leftwards;
    int _impact_rightwards;
    bool _blocked;
    int _cycle_count;
    float _max_positive_yaw_left;
    float _min_negative_yaw_right;
};
#endif