/* Get tilt angles on X and Y, and rotation angle on Z
    Angles are given in degrees
 License: MIT
 */
 #include "Wire.h"
 #include <MPU6050_light.h>
 MPU6050 mpu(Wire);
 unsigned long timer = 0;
 void mpu_setup(){
     Wire.begin();
     byte status = mpu.begin();
     Serial.print(F("MPU6050 status: "));
     Serial.println(status);
     while (status != 0) { } // stop everything if could not connect to MPU6050
     Serial.println(F("Calculating offsets, do not move MPU6050"));
     delay(1000);
     mpu.calcOffsets(); // gyro and accelero
     mpu.setAngleZ(0);
     Serial.println("Done!\n");
 }
 void reset_gyroZ(){
    mpu.setAngleZ(0); // créer une fonction pour réinitialiser l'angle à 0 quand on ne fait plus d'action.
    // Il faut créer cette fonction dans la librairie MPU6050_light.h ligne 91, inserer :
    // 	void setAngleZ(float value) {angleZ = value;};
 }
 void gyro_update(){
    mpu.update(); //Créer une fonction pour update le mpu dans le loop.
 }
 float gyroZ(){
     return (mpu.getAngleZ()); //créer une fonction pour récuperer l'angle Z.
 }
