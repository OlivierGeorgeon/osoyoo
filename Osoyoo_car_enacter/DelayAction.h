#ifndef DelayAction_h
#define DelayAction_h

#include <Time.h>


class DelayAction
{
  public:
    //constructeur
    DelayAction();

    unsigned long interval[10];
    unsigned long endTime[10];
    void (*functions[10])();

    unsigned int index;

    //appeler dans le setup
    //  interval_  = temps entre 2 execution
    //  func       = Fonction à executer tout les interval_
    //  millis     = millis() pour avoir le temps actuel
    void setDelayAction(unsigned long interval_, void (*func)(), int millis);

    //appeler 1 fois dans loop pour vérifier si il y a des fonctions à executer
    void checkDelayAction(int millis);
    
};

#endif