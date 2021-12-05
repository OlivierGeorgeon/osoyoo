/*
  Imu_control.cpp - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  https://github.com/jarzebski/Arduino-MPU6050
  released into the public domain

  Attention: You must reset the arduino after turning the power on otherwise the IMU is not properly calibrated
*/
#include "Arduino.h"
#include "Imu_control.h"
#include "Robot_define.h"
#include <Wire.h>
#include <MPU6050.h>
#if ROBOT_HAS_HMC5883L == true
  #include <HMC5883L.h>
#endif

Imu_control::Imu_control()
{
  _next_imu_read_time = 0;
  _yaw = 0;
}
void Imu_control::setup()
{
  //Serial.begin(9200);

  #if ROBOT_HAS_MPU6050 == true
  // Initialize MPU6050

  while(!_mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    Serial.println("You may need to comment line 54 in library MPU6050.cpp");
    delay(500);
  }

  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  _mpu.calibrateGyro();
  Serial.println("Gyroscope calibrated");

  // Set threshold sensitivity. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  _mpu.setThreshold(3); // Tried without but gives absurd results

  // Set DLP Filter
  // See https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
  _mpu.setDLPFMode(MPU6050_DLPF_4);  // Filter out frequencies over 21 Hz

  #else
    #warning "No MPU6050"
  #endif

  #if ROBOT_HAS_HMC5883L == true
  // Initialize Initialize HMC5883L

  _mpu.setI2CMasterModeEnabled(false);
  _mpu.setI2CBypassEnabled(true) ;
  _mpu.setSleepEnabled(false);

  Serial.println("Initialize HMC5883L");
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
  compass.setOffset(1475, -1685);
  #endif
}
void Imu_control::begin()
{
  _yaw = 0;
  _shock_measure = 0;
  _cycle_count = 0;
  _blocked = false;
  _max_acceleration = X_AXIS_DEFAULT_ACCELERATION;
  _min_acceleration = X_AXIS_DEFAULT_ACCELERATION;
  _max_speed = 0;
  _xSpeed = 0;
  _xDistance = 0;
}
void Imu_control::update()
{
  unsigned long timer = millis();
  if (_next_imu_read_time < timer)
  {
    _next_imu_read_time = timer + IMU_READ_PERIOD;
    _cycle_count++;

    #if ROBOT_HAS_MPU6050 == true
    // Read normalized values
    Vector normAccel = _mpu.readNormalizeAccel();
    Vector normGyro = _mpu.readNormalizeGyro();

    // Integrate Yaw during the interaction
    float _ZAngle = normGyro.ZAxis * IMU_READ_PERIOD / 1000;
    _yaw += _ZAngle;

    // Trying to detect strong X-axis acceleration after starting, possibly due to shock on solid obstacle
    if (normAccel.XAxis > _max_acceleration) _max_acceleration =  normAccel.XAxis;
    if (_cycle_count <= 6) {
      if (normAccel.XAxis < _min_acceleration) _min_acceleration =  normAccel.XAxis;
    }
    // When moving forward
    // Check for shock on the right
    if (_ZAngle < -1) _shock_measure |= B001;
    // Check for shock on the front
    if (normAccel.XAxis > X_AXIS_DEFAULT_ACCELERATION + 2) _shock_measure |= B010;
    // Check for shock on the left
    if (_ZAngle > 1) _shock_measure |= B100;
    // Check for blocked on the front (cannot accelerate properly during the first 250ms)
    if (_cycle_count >= 6) {
      if (_min_acceleration > X_AXIS_DEFAULT_ACCELERATION - 0.3) _blocked = true;
    }

    // Trying to compute the speed by integrating acceleration (not working)
    _xSpeed += (normAccel.XAxis) * IMU_READ_PERIOD / 1000;
    if (abs(_xSpeed) > _max_speed) _max_speed = abs(_xSpeed);
    // Trying to compute the distance by integrating the speed (not working)
    _xDistance += _xSpeed * IMU_READ_PERIOD / 1000;

    // Output raw
    //Serial.print("ZAxis = ");
    //Serial.println(normGyro.ZAxis * IMU_READ_PERIOD / 1000);

    #endif
  }
}
void Imu_control::outcome(JSONVar & outcome_object)
{
  outcome_object["yaw"] = (int) _yaw;
  outcome_object["shock"] = _shock_measure;
  outcome_object["blocked"] = _blocked;
  outcome_object["max_acceleration"] = (int) (_max_acceleration * 100);
  outcome_object["min_acceleration"] = (int) (_min_acceleration * 100);

  #if ROBOT_HAS_HMC5883L == true
  outcome_object["azimuth"] = read_azimuth();
  #endif
}

#if ROBOT_HAS_HMC5883L == true
int Imu_control::read_azimuth()
{
  Vector norm = compass.readNormalize();

  // Calculate heading
  float heading = atan2(norm.YAxis, norm.XAxis);

  // Convert to degrees
  int headingDegrees = heading * 180/M_PI;

  // Set declination angle on your location and fix heading
  // You can find your declination on: http://magnetic-declination.com/
  // (+) Positive or (-) for negative
  // For Bytom / Poland declination angle is 4'26E (positive)
  // Formula: (deg + (min / 60.0)) / (180 / M_PI) radiant;
  float declinationAngle = (4.0 + (26.0 / 60.0));
  //heading += declinationAngle;

  headingDegrees += 180;
  if (heading >= 360)
  {
    headingDegrees -= 360;
  }

  Serial.print("Azimuth = ");
  Serial.print(headingDegrees);
  Serial.println();

  return headingDegrees;
}
#endif