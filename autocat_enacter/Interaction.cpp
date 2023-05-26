/*
  Interaction.cpp - library for controlling an interaction
  Created by Olivier Georgeon, mai 26 2023
  released into the public domain
*/
#include "Color.h"
#include "Floor.h"
#include "Head.h"
#include "Interaction.h"

// Interaction::Interaction(Color& TCS, Head& HEA) : _TCS(TCS), _HEA(HEA)
Interaction::Interaction(Color& TCS, Floor& FCR, Head& HEA) : _TCS(TCS), _FCR(FCR), _HEA(HEA)
{
  //_TCS = TCS;
  //_FCR = FCR;
  //_HEA = HEA;
}
void Interaction::Step1(int& interaction_step)
{
}

// Wait for the interaction to terminate and proceed to Step 3
// Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
// Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
// Warning: in some situations, the head alignment may take quite long
void Interaction::Step2(unsigned long& action_end_time, int& interaction_step)
{
  if (action_end_time < millis() &&  !_FCR._is_enacting && !_HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
  //if (action_end_time < millis() )
  {
    _TCS.read();
    interaction_step = 3;
  }
}

void Interaction::Step3(int& interaction_step)
{
}
