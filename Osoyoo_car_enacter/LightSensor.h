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
    //Constructeur
    LightSensor();
    
    //Methode
    int tracking();
    void until_line(int speed);
};

#endif