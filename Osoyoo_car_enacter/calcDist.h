#ifndef calcDist_h
#define calcDist_h
    
#include "Arduino.h"

const byte TRIGGER_PIN = 30; // Broche TRIGGER
const byte ECHO_PIN = 31;    // Broche ECHO
 
/* Constantes pour le timeout */
const unsigned long MEASURE_TIMEOUT = 25000UL; // 25ms = ~8m à 340m/s

/* Vitesse du son dans l'air en mm/us */
const float SOUND_SPEED = 340.0 / 1000;


void set();
void dist();

#endif
