#ifndef DelayAction_h
#define DelayAction_h

#include <Time.h>


class DelayAction
{
  public:
    //Constructor
    DelayAction();

    unsigned long interval[10];
    unsigned long endTime[10];
    void (*functions[10])();

    unsigned int index;

    /* 
     * Execute in robot setup function
     * interval_  : time between 2 function execution
     * func       : Execute function
     * millis     : "millis()" to get current time
     *
     * Example: setDelayAction(2000, [](){Serial.println("print every 2 s");}, millis());
     */
    void setDelayAction(unsigned long interval_, void (*func)(), int millis);

    /*
     * To check if a function should be executed
     * Execute 1 time in robot loop function
     */
    void checkDelayAction(int millis);
    
};

#endif