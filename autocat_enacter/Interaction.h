/*
  Interaction.h - library for controlling an interaction
  Created by Olivier Georgeon, mai 26 2023
  released into the public domain
*/
#ifndef Interaction_h
#define Interaction_h

class Interaction
{
  public:
  //Interaction(Color& TCS, Head& HEA);
  Interaction(Color& TCS, Floor& FCR, Head& HEA);
  void Step1(int& interaction_step);
  void Step2(unsigned long& action_end_time, int& interaction_step);
  void Step3(int& interaction_step);
  private:
  Color& _TCS;
  Floor& _FCR;
  Head& _HEA;
};

#endif
