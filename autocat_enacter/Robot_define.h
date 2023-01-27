#define ROBOT_ID 4 // 0: regular Osoyoo robot, 1: robot BSN, 2: robot UCBL, 3: robot SHS, 4: SHS with GY86 chez Olivier

#define ROBOT_HEAD_X 80                 // (mm) X position of the head
#define SPEED 120
#define TURN_SPEED 110
#define SHIFT_SPEED 130
#define TURN_TIME 500                   // (ms)
#define MOVE_TIME 500
#define TURN_FRONT_ENDING_DELAY 100     // (ms)
#define TURN_FRONT_ENDING_ANGLE 3       // (degree)
#define TURN_SPOT_ANGLE 45              // (degree)

#if ROBOT_ID == 1

#warning "Compiling for BSN's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1.2
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 500
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET -40
#define ACCELERATION_SHOCK_THRESHOLD -200
#define ACCELERATION_BLOCK_THRESHOLD 60  // TODO depends whether the interaction starts when the robot is immobile
#define GYRO_COEF 1 // IMU is upright
#define GYRO_SHOCK_THRESHOLD 1 // °/s
#define ROBOT_SERVO_PIN 4  // 13 Changed because 13 is used for internal led

#elif ROBOT_ID == 2

#warning "Compiling for Olivier's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L true
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1.1  // 1.1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1 // 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 0.9  //1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1  // 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200  // Rotation speed is about 1° per 10ms
#define TURN_SPOT_ENDING_ANGLE 10
#define COMPASS_X_OFFSET 1431  //  1435
#define COMPASS_Y_OFFSET -1601 // -1645
#define ACCELERATION_X_OFFSET 550 //
#define ACCELERATION_SHOCK_THRESHOLD -400 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_BLOCK_THRESHOLD 60 // Below the threshold, the robot is blocked
#define GYRO_COEF 1.35 // UMI is upright
#define GYRO_SHOCK_THRESHOLD 1.5 // °/s Above the threshold is a shock to the left
#define ROBOT_SERVO_PIN 4

#elif ROBOT_ID == 3

#warning "Compiling for SHS's robot with GY521"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1.3
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define ACCELERATION_X_OFFSET 0 // TODO tune this value
#define ACCELERATION_SHOCK_THRESHOLD -200 // TODO set this value
#define ACCELERATION_BLOCK_THRESHOLD 30 // TODO set this value
#define GYRO_COEF -1 // IMU GY521 upside down
#define GYRO_SHOCK_THRESHOLD 1 // °/s TODO set this value
#define ROBOT_SERVO_PIN 4

#elif ROBOT_ID == 4

#warning "Compiling for SHS's robot with GY-86"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_HAS_HMC5883L true
#define ROBOT_REAR_LEFT_WHEEL_COEF 1.1 // 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1.2
#define ROBOT_REAR_RIGHT_WHEEL_COEF 0.9
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1.1 // 1.2 29/05/2022
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define COMPASS_X_OFFSET 1005  //  1020,  1060
#define COMPASS_Y_OFFSET -1247 // -1300, -1290
#define ACCELERATION_X_OFFSET 35
#define ACCELERATION_SHOCK_THRESHOLD -200 // TODO set this value
#define ACCELERATION_BLOCK_THRESHOLD 30 // TODO set this value
#define GYRO_COEF 1.50  // 1.5 si tourne trop, augmenter cette valeur
#define GYRO_SHOCK_THRESHOLD 1 // °/s TODO set this value
#define ROBOT_SERVO_PIN 4

#else

#warning "Compiling for a regular Osoyoo robot"
#define ROBOT_HAS_MPU6050  false
#define ROBOT_HAS_HMC5883L false
#define ROBOT_REAR_RIGHT_WHEEL_COEF 1
#define ROBOT_REAR_LEFT_WHEEL_COEF 1
#define ROBOT_FRONT_RIGHT_WHEEL_COEF 1
#define ROBOT_FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 1300
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 3
#define ROBOT_SERVO_PIN 13

#endif
