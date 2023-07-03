#define ROBOT_ID 1 // 0: regular Osoyoo robot, 1: robot BSN, 2: robot UCBL, 3: SHS chez Olivier, 11 to 14: DOLL robots

#define AP_SSID "osoyoo_robot"          // The wifi SSID of this robot in Access Point
#define ROBOT_HEAD_X 80                 // (mm) X position of the head
#define SPEED 120                       // (mm/s)
#define TURN_SPEED 110                  // (degree/s)
#define SHIFT_SPEED 150                 // (mm/s) 130
#define TURN_TIME 500                   // (ms)
#define MOVE_TIME 500                   // (ms)
#define TURN_SPOT_ANGLE 45              // (degree)

#if ROBOT_ID == 1

#warning "Compiling for BSN's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2 // "MMC5883"
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1.2
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 500
#define TURN_SPOT_ENDING_ANGLE 20  //  25
#define ACCELERATION_X_OFFSET -15  // -40
#define ACCELERATION_Y_OFFSET -30  // -3
#define COMPASS_X_OFFSET 6982 // 7062 // 7051 // 7022
#define COMPASS_Y_OFFSET 7320  // 7306 // 7336
#define ACCELERATION_X_IMPACT_THRESHOLD 200 // -400 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  //  110
#define ACCELERATION_X_BLOCK_THRESHOLD 60  // TODO depends whether the interaction starts when the robot is immobile
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // 100 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.0  // 1.2  //  1 // IMU is upright. If turns too much, increase this value
#define ROBOT_SERVO_PIN 4  // 13 Changed because 13 is used for internal led
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 2

#warning "Compiling for Olivier's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE  1 // "HMC5883L"
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1.1  // 1.1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1 // 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 0.9  //1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1  // 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200  // Rotation speed is about 1° per 10ms
#define TURN_SPOT_ENDING_ANGLE 10
#define COMPASS_X_OFFSET 1421  // 1431  //  1435
#define COMPASS_Y_OFFSET -1601 // -1645
#define ACCELERATION_X_OFFSET -550  // 550 //
#define ACCELERATION_Y_OFFSET 150  // -150 //  Negative if max acceleration is too high
#define ACCELERATION_X_IMPACT_THRESHOLD 250 // -400 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_Y_IMPACT_THRESHOLD 200
#define ACCELERATION_X_BLOCK_THRESHOLD 60 // Below the threshold, the robot is blocked
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.0 // 1.35 // UMI is upright
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 3

#warning "Compiling for SHS's robot with GY-86"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1 //  "HMC5883L"
#define ROBOT_REAR_LEFT_WHEEL_COEF  1.2  // 1.1 20/05/2023 // 1.3 04/04/2023 // 1.1 26/02/2023 // 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1.2  // 1.1 20/05/2023 // 1.3 04/04/2023
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1.0  //                                     0.9 26/02/2023
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1.0 // 1.1 20/05/2023 // 1.0 04/04/2023 // 1.1 26/02/2023 // 1.2 29/05/2022
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 9 // 5
#define COMPASS_X_OFFSET  1071  // 1100  // 1005  //  1020,  1060
#define COMPASS_Y_OFFSET  -1225  // -1300  // -1247 // -1300, -1290
#define ACCELERATION_X_OFFSET -55  // 55  // 35
#define ACCELERATION_Y_OFFSET 0  // -3        //
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 30 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // 100 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 2.0 // 1.33  // 1.5 si tourne trop, augmenter cette valeur
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree/s) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 11

#warning "Compiling for DOLL robot D1"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1 // "HMC5883L"
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET -1155
#define COMPASS_Y_OFFSET -1150
// #define ACCELERATION_IMPACT_THRESHOLD -300
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 12

#warning "Compiling for DOLL robot D2"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2// "MMC5883"
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 6435
#define COMPASS_Y_OFFSET 5581
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 13

#warning "Compiling for DOLL robot D3"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 6021
#define COMPASS_Y_OFFSET 5653
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.4
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact

#elif ROBOT_ID == 14

#warning "Compiling for DOLL robot D4"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1.2
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 10
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 5921
#define COMPASS_Y_OFFSET 5669
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define ROBOT_SERVO_PIN 4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact


#else

#warning "Compiling for a regular Osoyoo robot"
#define ROBOT_HAS_MPU6050 false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 1300
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define ROBOT_SERVO_PIN 13

#endif
