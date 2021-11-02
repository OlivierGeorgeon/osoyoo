/*
 *  _____     _____     __      __   __     __   _______   __               _______         __         ___        ____   ______     __       ___
 * |  __  \  |  __  \  |  |    |  | |  \   |  | |   ____| |  |            /   _____|      /    \      |   \      /    | |   __  \  |  |    /     \
 * | |__|  | | |__|  | |  |    |  | |   \  |  | |  |__    |  |           /   /           /  /\  \     |    \    /     | |  |__|  | |  |   /   _   \
 * |     _/  |     _/  |  |    |  | |    \ |  | |     |   |  |          |   |  ____     /  /__\  \    |  |\  \ /  /|  | |  _____/  |  |  |   |  |  |
 * |  __  \  |  __  \  |  |    |  | |  |\ \|  | |   __|   |  |          |   |  |__ |   /   ____   \   |  |  \___/  |  | |  |       |  |  |   |_ |  |
 * | |__|  | | |  \  \ |   \__/   | |  | \    | |  |____  |  |____       \  \ _ |  |  /   /    \   \  |  |         |  | |  |       |  |   \       / 
 * |______/  |_|   \__\ \________/  |__|  \___| |_______| |_______|       \ _______| /__ /      \   \ |__|         |__| |__|       |__|    \ ___ /
 */

#ifndef omny_wheel_motion_h
#define omny_wheel_motion_h

//Definition de la vitesse des roues
#define SPEED 85   

//Selection des ports sur la cartes Arduino et la carte WIFI
#define speedPinR 9   //  RIGHT WHEEL PWM pin D45 connect front MODEL-X ENA 
#define RightMotorDirPin1  22    //Front Right Motor direction pin 1 to Front MODEL-X IN1  (K1)
#define RightMotorDirPin2  24   //Front Right Motor direction pin 2 to Front MODEL-X IN2   (K1)                                 
#define LeftMotorDirPin1  26    //Left front Motor direction pin 1 to Front MODEL-X IN3 (  K3)
#define LeftMotorDirPin2  28   //Left front Motor direction pin 2 to Front MODEL-X IN4 (  K3)
#define speedPinL 10   // Left WHEEL PWM pin D7 connect front MODEL-X ENB

#define speedPinRB 11   //  RIGHT WHEEL PWM pin connect Back MODEL-X ENA 
#define RightMotorDirPin1B  5    //Rear Right Motor direction pin 1 to Back MODEL-X IN1 (  K1)
#define RightMotorDirPin2B 6    //Rear Right Motor direction pin 2 to Back MODEL-X IN2 (  K1) 
#define LeftMotorDirPin1B 7    //Rear left Motor direction pin 1 to Back MODEL-X IN3  K3
#define LeftMotorDirPin2B 8  //Rear left Motor direction pin 2 to Back MODEL-X IN4  k3
#define speedPinLB 12    //   LEFT WHEEL  PWM pin D8 connect Rear MODEL-X ENB

//Fonction gerant le roulages des roues du robot
void setMotion(int speed_fl,int speed_rl ,int speed_rr,int speed_fr);

void go_forward(int speed);  //Faire avancer le robot 

void go_back(int speed);    //Faire reculer le robot 

void left_turn(int speed);   //Faire tourner le robot à gauche

void right_turn(int speed);  //Faire torner le robot à droite

void FL(int speed);      //Roulage de la roue avant gauche

void RL(int speed);      //Roulage de la roue arriere gauche

void FR(int speed);     //Roulage de la roue avant droite

void RR(int speed);      //Roulage de la roue arriere droite

void stop_Stop();       //Stopper l'action du robot

void init_GPIO();

#endif
