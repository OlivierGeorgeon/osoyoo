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
#include "src/wifi/WifiCat.h"
#include "Interaction.h"
// #include "Action_define.h"

class Sequencer
{
public:
  Sequencer(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat);
  Interaction* update(int& interaction_step, Interaction* INT);
  // int get_interaction_step();
private:
  Floor& _FLO;
  Head& _HEA;
  Imu& _IMU;
  WifiCat& _WifiCat;

  // int interaction_step = INTERACTION_DONE;
  int previous_clock = -1;
  char packetBuffer[UDP_BUFFER_SIZE];
};

#endif