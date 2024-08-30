/*
  Scan.h - library for controlling the scan interaction
  Created by Olivier Georgeon, June 1 2023
  released into the public domain
*/
#ifndef Scan_h
#define Scan_h

#define MAX_SCANS 181  // To scan at most every 1° from -90 to 90 (reduce if need to spare memory)

#include "../../Interaction.h"

//struct significant_array
//{
//    // Struct to store the angles and the corresponding measures,
//    int distances[MAX_SACCADES]{0};
//    int8_t angles[MAX_SACCADES]{0};
////    bool sign[MAX_SACCADES]{false};
//};


class Scan : public Interaction
{
public:
  Scan(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action);
  void begin() override;
  void ongoing() override;
  void outcome(JSONVar & outcome_object) override;
private:
  int _head_angle;
  int _current_ultrasonic_measure;
  int _min_ultrasonic_measure;
  int _angle_min_ultrasonic_measure;
  int _head_angle_span;
  unsigned long _next_saccade_time;
  // significant_array _sign_array;
  int distances[MAX_SCANS]{0};
  int8_t angles[MAX_SCANS]{0};
  int _current_index;
};

#endif
