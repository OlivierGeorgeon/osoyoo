/*
  Imu_control.cpp - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  https://github.com/jarzebski/Arduino-MPU6050
  released into the public domain
*/
#include "Arduino.h"
#include "Imu_control.h"
#include "Robot_define.h"
#include <Wire.h>
#include "src/lib/MPU6050.h"
#if ROBOT_HAS_HMC5883L == true
  #include <HMC5883L.h>
#endif

Imu_control::Imu_control()
{
  _next_imu_read_time = 0;
  _yaw = 0;
  //_debug_message = "";
}
void Imu_control::setup()
{
  #if ROBOT_HAS_MPU6050 == true
  // Initialize MPU6050

  _mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G);
  // _mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G);

  //while(!_mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  //{
  //  Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
  //  Serial.println("You may need to check the WHO_AM_I address in line 54 in library MPU6050.cpp");
  //  delay(500);
  //}

  // Set DLP Filter
  // See https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
  _mpu.setDLPFMode(MPU6050_DLPF_4);  // Filter out frequencies over 21 Hz

  // Calibrate gyroscope. The robot must be at rest during calibration.
  // If you don't want calibrate, comment this line.
  _mpu.calibrateGyro();

  // Set threshold sensitivity. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  _mpu.setThreshold(3); // Tried without but gives absurd results

  #else
    #warning "No MPU6050"
  #endif

  #if ROBOT_HAS_HMC5883L == true

  // Initialize HMC5883L
  _mpu.setI2CMasterModeEnabled(false);
  _mpu.setI2CBypassEnabled(true) ;
  _mpu.setSleepEnabled(false);
  // Serial.println("Initialize HMC5883L");
  while (!compass.begin())
  {
    Serial.println("Could not find a valid HMC5883L sensor, check wiring!");
    delay(500);
  }

  // Set measurement range
  compass.setRange(HMC5883L_RANGE_1_3GA);

  // Set measurement mode
  compass.setMeasurementMode(HMC5883L_CONTINOUS);

  // Set data rate
  compass.setDataRate(HMC5883L_DATARATE_30HZ); // HMC5883L_DATARATE_15HZ

  // Set number of samples averaged
  compass.setSamples(HMC5883L_SAMPLES_4); // HMC5883L_SAMPLES_8

  // Set calibration offset. See HMC5883L_calibration.ino
  compass.setOffset(COMPASS_X_OFFSET, COMPASS_Y_OFFSET);
  #endif
}
void Imu_control::begin()
{
  _yaw = 0;
  _shock_measure = 0;
  _cycle_count = 0;
  _blocked = false;
  _max_acceleration = 0;
  _min_acceleration = 0;
  _max_speed = 0;
  _min_speed = 0;
  _xSpeed = 0;
  _xDistance = 0;
}
int Imu_control::update()
{
  unsigned long timer = millis();
  if (_next_imu_read_time < timer)
  {
    _next_imu_read_time = timer + IMU_READ_PERIOD;
    _cycle_count++;

    #if ROBOT_HAS_MPU6050 == true
    // Read normalized values
    // Serial.println("Read Acceleration"); // for debug
    Vector normAccel = _mpu.readNormalizeAccel();
    // Serial.println("Read Gyro"); // for debug
    Vector normGyro = _mpu.readNormalizeGyro();
    // Serial.println("end read mpu"); // for debug

    int normalized_acceleration = -normAccel.XAxis * 100 + ACCELERATION_X_OFFSET;

    // Integrate yaw during the interaction
    float _ZAngle = normGyro.ZAxis * IMU_READ_PERIOD / 1000 * GYRO_COEF;
    _yaw += _ZAngle;

    // Record the min acceleration (deceleration) during the interaction to detect collision
    if (normalized_acceleration < _min_acceleration) {
      _min_acceleration =  normalized_acceleration;
    }
    // Record the max acceleration during the interaction to detect block
    if (normalized_acceleration > _max_acceleration) {
      _max_acceleration =  normalized_acceleration;
    }
    // Check for turned to the right by more than 1°/s
    if (_ZAngle < -GYRO_SHOCK_THRESHOLD) {
      // If moving forward, this will mean collision on the right
      _shock_measure = B01;
    }
    // Check a peek deceleration = frontal shock
    if (normalized_acceleration < ACCELERATION_SHOCK_THRESHOLD) {
      _shock_measure = B11;
    }
    // Check for turned to the left by more than 1°/s
    if (_ZAngle > GYRO_SHOCK_THRESHOLD) {
      // If moving forward, this will mean collision on the left
      _shock_measure = B10;
    }
    // Check for blocked on the front
    // (the acceleration did not pass the threshold during the first 250ms)
    if (_cycle_count >= 6) {
      if (_max_acceleration < ACCELERATION_BLOCK_THRESHOLD) {
        // _shock_measure = B11;
        _blocked = true;
      }
    }

    // Trying to compute the speed by integrating acceleration (not working)
    _xSpeed += (normalized_acceleration) * IMU_READ_PERIOD / 100;
    if (_xSpeed > _max_speed) _max_speed = _xSpeed;
    if (_xSpeed < _min_speed) _min_speed = _xSpeed;
    // Trying to compute the distance by integrating the speed (not working)
    _xDistance += _xSpeed * IMU_READ_PERIOD / 1000;

    #endif
  }
  return _shock_measure;
}
void Imu_control::outcome(JSONVar & outcome_object)
{
  #if ROBOT_HAS_MPU6050 == true
  outcome_object["yaw"] = (int) _yaw;
  outcome_object["shock"] = _shock_measure;
  outcome_object["blocked"] = _blocked;
  outcome_object["max_acc"] = _max_acceleration;
  outcome_object["min_acc"] = _min_acceleration;
  // outcome_object["max_speed"] = (int) _max_speed;
  // outcome_object["min_speed"] = (int) _min_speed;
  // outcome_object["distance"] = (int) _xDistance;

  #endif
  //outcome_object["debug"] = _debug_message;
  //_debug_message = "";

  #if ROBOT_HAS_HMC5883L == true
  read_azimuth(outcome_object);
  #endif
}

#if ROBOT_HAS_HMC5883L == true
void Imu_control::read_azimuth(JSONVar & outcome_object)
{
  Vector norm = compass.readNormalize();

  // Calculate heading
  float heading = atan2(norm.YAxis, norm.XAxis);
  // Serial.println("compass_x: " + String((int)norm.XAxis) + ", compass_y: " + String((int)norm.YAxis));

  // You must set the offset so that compass_x is near 0 when the robot is East or West
  //                             and compass_y is near 0 when the robot is North or South.
  // see https://www.best-microcontroller-projects.com/hmc5883l.html
  // For example, I obtain:
  // North compass_x: -230, compass_y:    2
  // Est   compass_x:  -30, compass_y: -225
  // South compass_x:  218, compass_y:  -29
  // West  compass_x:    3, compass_y:  217

  // Convert to degrees
  int headingDegrees = heading * 180.0/M_PI;

  // Set declination angle on your location and fix heading
  // You can find your declination on: http://magnetic-declination.com/
  // (+) Positive or (-) for negative
  // For Bytom / Poland declination angle is 4'26E (positive)
  // Formula: (deg + (min / 60.0)) / (180 / M_PI) radiant;
  // float declinationAngle = (2.0 + (13.0 / 60.0));
  // heading += declinationAngle;

  headingDegrees += 180;
  if (heading >= 360)
  {
    headingDegrees -= 360;
  }

  outcome_object["compass_x"] = (int)norm.XAxis;
  outcome_object["compass_y"] = (int)norm.YAxis;
  outcome_object["azimuth"] = headingDegrees;

  // return headingDegrees;
}
#endif