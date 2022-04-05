#include <Arduino.h>
#include "Head_Dist.h"

Head_Dist::Head_Dist()
{
}
void Head_Dist::setup() {
  /* function for initializing the infrared sensor */
  /* Initialize the pins */
  pinMode(TRIGGER_PIN, OUTPUT);
  digitalWrite(TRIGGER_PIN, LOW); // The TRIGGER pin must be at LOW when not in use
  pinMode(ECHO_PIN, INPUT);
}
 

float Head_Dist::dist() {
    /* function to calculate a distance */
    /* 1. Start a distance measurement by sending a 10µs HIGH pulse to the TRIGGER pin */
    digitalWrite(TRIGGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGGER_PIN, LOW);

    /* 2. Measures the time between the sending of the ultrasonic pulse and its echo (if it exists) */
    long measure = pulseIn(ECHO_PIN, HIGH, MEASURE_TIMEOUT);

    /* 3. Calculates the distance from the measured time */
    float distance_mm = measure / 2.0 * SOUND_SPEED;

    /* Displays the results in mm*/
    return distance_mm;

}
