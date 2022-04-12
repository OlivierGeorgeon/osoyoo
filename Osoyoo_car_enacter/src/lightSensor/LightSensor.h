#ifndef LightSensor_h
#define LightSensor_h

#define sensor0   A0 // Left   sensor
#define sensor1   A1 // center left  sensor
#define sensor2   A2 // center sensor
#define sensor3   A3 // center right  sensor
#define sensor4   A4 // right sensor

class LightSensor
{
    public:
    //Constructor
    LightSensor();
    
    /*
     * Method to check if the robot detects a black line
     *
     * Return 1 =   Oriented line : /
     * Return 2 =   Oriented line : \
     * Return 3 =   Oriented line : --
     * Return 0 =   No line
     */
    int tracking();

    /*
     * Move forward until the robot detects a line
     */
    void until_line(int speed);
};

#endif