/*
  Sequencer.h - library to control the sequences of interaction.
  Created Olivier Georgeon June 16 2023
  Released into the public domain
*/

#ifndef Sequencer_h
#define Sequencer_h

#include "Color.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Led.h"
#include "src/wifi/WifiCat.h"
#include "Interaction.h"

class Sequencer
{
public:
  Sequencer(Floor& FLO, Head& HEA, Imu& IMU, Led& LED, WifiCat& WifiCat);
  Interaction* update(int& interaction_step, Interaction* INT);
private:
  Floor& _FLO;
  Head& _HEA;
  Imu& _IMU;
  Led& _LED;
  WifiCat& _WifiCat;

  int previous_clock = -1;
  char packetBuffer[UDP_BUFFER_SIZE];
};

#endif