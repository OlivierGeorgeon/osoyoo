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
  Sequencer(Floor& FLO, Head& HEA, Imu& IMU, Led& LED);
  void setup();
  void update(int& interaction_step, int& interaction_direction);
private:
  Floor& _FLO;
  Head& _HEA;
  Imu& _IMU;
  Led& _LED;
  WifiCat _WIFI;
  Interaction* INT  = nullptr;  // The interaction type will depend on the action received from the PC
  int _previous_clock = -1;
  char _packetBuffer[UDP_BUFFER_SIZE];
};

#endif