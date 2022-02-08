#ifndef Head_h
#define Head_h
#include <Servo.h>
#define SERVO_PIN     13  //servo connect to D5
class Head
{
private:
    Servo head_servo;
public:
    Head();
    int scan(int angleMin, int angleMax, int nbre_mesure, int index_0);
    // void distances_loop(int angle, float mesure);
    // int miniScan(int angle);
    int getIndexMin(int nb_mesures, float distances[]);
    void servo_port();
};
#endif
