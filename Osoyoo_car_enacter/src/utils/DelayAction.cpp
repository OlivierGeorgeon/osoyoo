#include "DelayAction.h"

#include <Time.h>

DelayAction::DelayAction()
{
    index = 0;
}

void DelayAction::setDelayAction(unsigned long interval_, void (*func)(), int millis)
{
    interval[index] = interval_;
    endTime[index] = millis + interval_;
    functions[index] = func;
    
    index++;
}

void DelayAction::checkDelayAction(int millis)
{
    for (int i = 0; i < index; i++)
    {
        if(endTime[i] < millis)
        {
            (*functions[i])();
            endTime[i] = millis + interval[i];
        }
    }
}