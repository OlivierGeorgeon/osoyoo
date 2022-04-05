#include <Arduino.h>
#include "Head_Dist.h"

Head_Dist::Head_Dist()
{
}
void Head_Dist::setup() {
  /* Initialise les broches */
  pinMode(TRIGGER_PIN, OUTPUT);
  digitalWrite(TRIGGER_PIN, LOW); // La broche TRIGGER doit être à LOW au repos
  pinMode(ECHO_PIN, INPUT);
}
 

float Head_Dist::dist() {
    /* 1. Lance une mesure de distance en envoyant une impulsion HIGH de 10µs sur la broche TRIGGER */
    digitalWrite(TRIGGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGGER_PIN, LOW);

    /* 2. Mesure le temps entre l'envoi de l'impulsion ultrasonique et son écho (si il existe) */
    long measure = pulseIn(ECHO_PIN, HIGH, MEASURE_TIMEOUT);

    /* 3. Calcul la distance à partir du temps mesuré */
    float distance_mm = measure / 2.0 * SOUND_SPEED;

    /* Affiche les résultats en mm*/
    return distance_mm;

}
